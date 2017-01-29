from __future__ import unicode_literals

from collections import namedtuple
from datetime import date, datetime, timedelta

from django.core.urlresolvers import reverse_lazy as reverse
from django.db import models
from django.dispatch import receiver
from django.utils.encoding import (
    force_text, python_2_unicode_compatible, smart_text,
)
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from djangocms_text_ckeditor.fields import HTMLField

from ..utils import comma_separated
from .fields import DAY_OF_WEEK, DayOfWeekField
from .startend import StartEndMixin
from .subjects import Subject, SubjectDiscount, SubjectRegistration
from .utils import PaymentStatus


class Course(Subject):
    unit        = models.CharField(_('unit'), max_length=150)

    class Meta:
        app_label           = 'leprikon'
        ordering            = ('name',)
        verbose_name        = _('course')
        verbose_name_plural = _('courses')

    @cached_property
    def all_times(self):
        return list(self.times.all())

    @cached_property
    def all_periods(self):
        return list(self.periods.all())

    @cached_property
    def all_journal_entries(self):
        return list(self.journal_entries.all())

    def get_current_period(self):
        return self.periods.filter(end__gte=date.today()).first() or self.periods.last()

    def get_times_list(self):
        return comma_separated(self.all_times)
    get_times_list.short_description = _('times')

    def get_periods_list(self):
        return '<br/>'.join(smart_text(p) for p in self.all_periods)
    get_periods_list.short_description = _('periods')
    get_periods_list.allow_tags = True

    def get_next_time(self, now = None):
        try:
            return min(t.get_next_time(now) for t in self.all_times)
        except ValueError:
            return None

    @property
    def registrations_history_registrations(self):
        return CourseRegistration.objects.filter(course_history__course=self).distinct()

    @property
    def inactive_registrations(self):
        return (CourseRegistration.objects.filter(course_history__course=self)
                .exclude(id__in=self.active_registrations.all()).distinct())

    def get_active_registrations(self, d):
        ids = (CourseRegistrationHistory.objects.filter(course=self, start__lte=d)
               .exclude(end__lt=d).values_list('registration_id', flat=True))
        return CourseRegistration.objects.filter(id__in=ids).exclude(canceled__lt=d).distinct()

    def copy_to_school_year(old, school_year):
        new = Course.objects.get(id=old.id)
        new.id = None
        new.school_year = school_year
        new.public      = False
        new.evaluation  = ''
        new.note        = ''
        new.save()
        new.groups      = old.groups.all()
        new.age_groups  = old.age_groups.all()
        new.leaders     = old.leaders.all()
        new.questions   = old.questions.all()
        new.times       = old.times.all()
        new.attachments = old.attachments.all()
        year_offset = school_year.year - old.school_year.year
        if new.reg_from:
            try:
                new.reg_from = datetime(
                    new.reg_from.year + year_offset,
                    new.reg_from.month,
                    new.reg_from.day,
                    new.reg_from.hour,
                    new.reg_from.minute,
                    new.reg_from.second,
                )
            except ValueError:
                # handle leap-year
                new.reg_from = datetime(
                    new.reg_from.year + year_offset,
                    new.reg_from.month,
                    new.reg_from.day - 1,
                    new.reg_from.hour,
                    new.reg_from.minute,
                    new.reg_from.second,
                )
        if new.reg_to:
            try:
                new.reg_to = datetime(
                    new.reg_to.year + year_offset,
                    new.reg_to.month,
                    new.reg_to.day,
                    new.reg_to.hour,
                    new.reg_to.minute,
                    new.reg_to.second,
                )
            except ValueError:
                # handle leap-year
                new.reg_to = datetime(
                    new.reg_to.year + year_offset,
                    new.reg_to.month,
                    new.reg_to.day - 1,
                    new.reg_to.hour,
                    new.reg_to.minute,
                    new.reg_to.second,
                )
        for period in old.all_periods:
            period.id = None
            period.course = new
            try:
                period.start = date(period.start.year + year_offset, period.start.month, period.start.day)
            except ValueError:
                # handle leap-year
                period.start = date(period.start.year + year_offset, period.start.month, period.start.day - 1)
            try:
                period.end   = date(period.end.year   + year_offset, period.end.month,   period.end.day)
            except ValueError:
                # handle leap-year
                period.end   = date(period.end.year   + year_offset, period.end.month,   period.end.day - 1)
            period.save()
        return new



@python_2_unicode_compatible
class CourseTime(StartEndMixin, models.Model):
    course      = models.ForeignKey(Course, verbose_name=_('course'), related_name='times')
    day_of_week = DayOfWeekField(_('day of week'))
    start       = models.TimeField(_('start time'), blank=True, null=True)
    end         = models.TimeField(_('end time'), blank=True, null=True)

    class Meta:
        app_label           = 'leprikon'
        ordering            = ('day_of_week', 'start')
        verbose_name        = _('time')
        verbose_name_plural = _('times')

    def __str__(self):
        if self.start is not None and self.end is not None:
            return _('{day}, {start:%H:%M} - {end:%H:%M}').format(
                day     = self.day,
                start   = self.start,
                end     = self.end,
            )
        elif self.start is not None:
            return _('{day}, {start:%H:%M}').format(
                day     = self.day,
                start   = self.start,
            )
        else:
            return force_text(self.day)

    @cached_property
    def day(self):
        return DAY_OF_WEEK[self.day_of_week]

    Time = namedtuple('Time', ('date', 'start', 'end'))

    def get_next_time(self, now = None):
        now = now or datetime.now()
        daydelta = (self.day_of_week - now.isoweekday()) % 7
        if daydelta == 0 and (isinstance(now, date) or self.start is None or self.start <= now.time()):
            daydelta = 7
        if isinstance(now, datetime):
            next_date = now.date() + timedelta(daydelta)
        else:
            next_date = now + timedelta(daydelta)
        return self.Time(
            date    = next_date,
            start   = self.start,
            end     = self.end,
        )



@python_2_unicode_compatible
class CoursePeriod(StartEndMixin, models.Model):
    course      = models.ForeignKey(Course, verbose_name=_('course'), related_name='periods')
    name        = models.CharField(_('name'), max_length=150)
    start       = models.DateField(_('start date'))
    end         = models.DateField(_('end date'))

    class Meta:
        app_label           = 'leprikon'
        ordering            = ('course__name', 'start')
        verbose_name        = _('period')
        verbose_name_plural = _('periods')

    def __str__(self):
        return _('{name}, {start:%m/%d %y} - {end:%m/%d %y}').format(
            name    = self.name,
            start   = self.start,
            end     = self.end,
        )

    @cached_property
    def journal_entries(self):
        return self.course.journal_entries.filter(date__gte=self.start, date__lte=self.end)

    @cached_property
    def all_journal_entries(self):
        return list(self.journal_entries.all())

    @cached_property
    def all_registrations(self):
        return list(self.course.registrations_history_registrations.filter(created__lt=self.end))

    @cached_property
    def all_alternates(self):
        alternates = set()
        for entry in self.all_journal_entries:
            for alternate in entry.all_alternates:
                alternates.add(alternate)
        return list(alternates)

    PresenceRecord = namedtuple('PresenceRecord', ('name', 'presences'))

    def get_participant_presences(self):
        return [
            self.PresenceRecord(
                reg.participant,
                [
                    reg in entry.all_registrations
                    for entry in self.all_journal_entries
                ]
            ) for reg in self.all_registrations
        ]

    def get_leader_presences(self):
        return [
            self.PresenceRecord(
                leader,
                [
                    entry.all_leader_entries_by_leader.get(leader, None)
                    for entry in self.all_journal_entries
                ]
            ) for leader in self.course.all_leaders
        ]

    def get_alternate_presences(self):
        return [
            self.PresenceRecord(
                alternate,
                [
                    entry.all_leader_entries_by_leader.get(alternate, None)
                    for entry in self.all_journal_entries
                ]
            ) for alternate in self.all_alternates
        ]



class CourseRegistration(SubjectRegistration):

    class Meta:
        app_label           = 'leprikon'
        verbose_name        = _('course registration')
        verbose_name_plural = _('course registrations')

    @property
    def periods(self):
        if self.canceled:
            return self.subject.course.periods.filter(end__gt=self.created, start__lt=self.canceled)
        else:
            return self.subject.course.periods.filter(end__gt=self.created)

    @cached_property
    def all_periods(self):
        return list(self.periods.all())

    @cached_property
    def all_discounts(self):
        return list(self.discounts.all())

    @cached_property
    def period_payment_statuses(self):
        return self.get_payment_statuses()

    PeriodPaymentStatus = namedtuple('PeriodPaymentStatus', ('period', 'status'))

    def get_period_payment_statuses(self, d=None):
        paid = self.get_paid(d)
        for counter, period in enumerate(self.all_periods, start=-len(self.all_periods)):
            discount = sum(
                discount.amount
                for discount in filter(
                    lambda discount: discount.period == period and (d is None or discount.created <= d),
                    self.all_discounts
                )
            )
            yield self.PeriodPaymentStatus(
                period  = period,
                status  = PaymentStatus(
                    price       = self.price,
                    discount    = discount,
                    paid        = min(self.price - discount, paid) if counter < -1 else paid,
                ),
            )
            paid = max(paid - (self.price - discount), 0)

    @cached_property
    def payment_statuses(self):
        return self.get_payment_statuses()

    PaymentStatuses = namedtuple('PaymentStatuses', ('partial', 'total'))

    def get_payment_statuses(self, d=None):
        if d is None:
            d = date.today()
        partial_price       = self.price * len(list(filter(lambda p: p.start <= d, self.all_periods)))
        total_price         = self.price * len(self.all_periods)
        partial_discount    = sum(
            discount.amount
            for discount in filter(lambda discount: discount.period.start <= d, self.all_discounts)
        )
        total_discount  = sum(discount.amount for discount in self.all_discounts)
        paid            = self.get_paid(d)
        return self.PaymentStatuses(
            partial = PaymentStatus(price=partial_price, discount=partial_discount, paid=paid),
            total   = PaymentStatus(price=total_price, discount=total_discount, paid=paid),
        )



class CourseDiscount(SubjectDiscount):
    registration    = models.ForeignKey(CourseRegistration, verbose_name=_('registration'),
                                        related_name='discounts', on_delete=models.PROTECT)
    period          = models.ForeignKey(CoursePeriod, verbose_name=_('period'),
                                        related_name='discounts', on_delete=models.PROTECT)



class CourseRegistrationHistory(models.Model):
    registration = models.ForeignKey(CourseRegistration, verbose_name=_('course'),
                                     related_name='course_history', on_delete=models.PROTECT)
    course = models.ForeignKey(Course, verbose_name=_('course'),
                               related_name='registrations_history', on_delete=models.PROTECT)
    start = models.DateField()
    end = models.DateField(default=None, null=True)

    class Meta:
        ordering            = ('start',)

    @property
    def course_journal_entries(self):
        qs = CourseJournalEntry.objects.filter(course=self.course, date__gte=self.start)
        if self.end:
            return qs.filter(date__lte=self.end)
        else:
            return qs



@receiver(models.signals.post_save, sender=CourseRegistration)
def update_course_registration_history(sender, instance, created, **kwargs):
    d = date.today()
    # if created or changed
    if (created or
        CourseRegistrationHistory.objects.filter(registration_id=instance.id, end=None)
                                 .exclude(course_id=instance.subject_id).update(end=d)):
        # reopen or create entry starting today
        (
            CourseRegistrationHistory.objects.filter(
                registration_id=instance.id, course_id=instance.subject_id, start=d,
            ).update(end=None) or
            CourseRegistrationHistory.objects.create(
                registration_id=instance.id, course_id=instance.subject_id, start=d,
            )
        )



def get_default_agenda():
    return '<p>{}</p>'.format(_('instruction on OSH'))



@python_2_unicode_compatible
class CourseJournalEntry(StartEndMixin, models.Model):
    course      = models.ForeignKey(Course, verbose_name=_('course'), editable=False,
                                    related_name='journal_entries', on_delete=models.PROTECT)
    date        = models.DateField(_('date'))
    start       = models.TimeField(_('start time'), blank=True, null=True,
                                   help_text=_('Leave empty, if the course does not take place'))
    end         = models.TimeField(_('end time'), blank=True, null=True,
                                   help_text=_('Leave empty, if the course does not take place'))
    agenda      = HTMLField(_('session agenda'), default=get_default_agenda)
    registrations = models.ManyToManyField(CourseRegistration, verbose_name=_('participants'), blank=True,
                                           related_name='journal_entries')

    class Meta:
        app_label           = 'leprikon'
        ordering            = ('date', 'start', 'end')
        verbose_name        = _('journal entry')
        verbose_name_plural = _('journal entries')

    def __str__(self):
        return '{course}, {date}'.format(
            course  = self.course.name,
            date    = self.date,
        )

    @cached_property
    def datetime_start(self):
        try:
            return datetime.combine(self.date, self.start)
        except:
            return None

    @cached_property
    def datetime_end(self):
        try:
            return datetime.combine(self.date, self.end)
        except:
            return None

    @cached_property
    def duration(self):
        try:
            return self.datetime_end - self.datetime_start
        except:
            return timedelta()
    duration.short_description = _('duration')

    @cached_property
    def all_registrations(self):
        return list(self.registrations.all())

    @cached_property
    def all_leader_entries(self):
        return list(self.leader_entries.all())

    @cached_property
    def all_leader_entries_by_leader(self):
        return dict((e.timesheet.leader, e) for e in self.all_leader_entries)

    @cached_property
    def all_leaders(self):
        return list(
            le.timesheet.leader for le in self.all_leader_entries
            if le.timesheet.leader in self.course.all_leaders
        )

    @cached_property
    def all_alternates(self):
        return list(
            le.timesheet.leader for le in self.all_leader_entries
            if le.timesheet.leader not in self.course.all_leaders
        )

    @property
    def timesheets(self):
        from .timesheets import Timesheet
        return Timesheet.objects.by_date(self.start).filter(
            leader__in = self.all_leaders + self.all_alternates,
        )

    def save(self, *args, **kwargs):
        if self.end is None:
            self.end = self.start
        super(CourseJournalEntry, self).save(*args, **kwargs)

    def get_edit_url(self):
        return reverse('leprikon:coursejournalentry_update', args=(self.id,))

    def get_delete_url(self):
        return reverse('leprikon:coursejournalentry_delete', args=(self.id,))



@python_2_unicode_compatible
class CourseJournalLeaderEntry(StartEndMixin, models.Model):
    course_entry = models.ForeignKey(CourseJournalEntry, verbose_name=_('course journal entry'),
                                     related_name='leader_entries', editable=False)
    timesheet   = models.ForeignKey('leprikon.Timesheet', verbose_name=_('timesheet'), related_name='course_entries',
                                    editable=False, on_delete=models.PROTECT)
    start       = models.TimeField(_('start time'))
    end         = models.TimeField(_('end time'))

    class Meta:
        app_label           = 'leprikon'
        verbose_name        = _('course journal leader entry')
        verbose_name_plural = _('course journal leader entries')
        unique_together     = (('course_entry', 'timesheet'),)

    def __str__(self):
        return '{}'.format(self.duration)

    @cached_property
    def date(self):
        return self.course_entry.date
    date.short_description = _('date')
    date.admin_order_field = 'course_entry__date'

    @cached_property
    def course(self):
        return self.course_entry.course
    course.short_description = _('course')

    @cached_property
    def datetime_start(self):
        return datetime.combine(self.date, self.start)

    @cached_property
    def datetime_end(self):
        return datetime.combine(self.date, self.end)

    @cached_property
    def duration(self):
        return self.datetime_end - self.datetime_start
    duration.short_description = _('duration')

    @property
    def group(self):
        return self.course

    def get_edit_url(self):
        return reverse('leprikon:coursejournalleaderentry_update', args=(self.id,))

    def get_delete_url(self):
        return reverse('leprikon:coursejournalleaderentry_delete', args=(self.id,))