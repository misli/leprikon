from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

import colorsys

from cms.models import CMSPlugin
from cms.models.fields import PageField
from collections import namedtuple
from datetime import date, datetime, time, timedelta
from django.core.urlresolvers import reverse_lazy as reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.encoding import smart_text, force_text
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from djangocms_text_ckeditor.fields import HTMLField
from filer.fields.file import FilerFileField
from filer.fields.image import FilerImageField
from json import loads

from ..conf import settings
from ..utils import get_mailer, currency, comma_separated

from .fields import DAY_OF_WEEK, DayOfWeekField
from .fields import ColorField, BirthNumberField, PostalCodeField, PriceField

from .question import Question
from .agegroup import AgeGroup
from .place import Place
from .roles import Leader, Participant
from .school import School
from .schoolyear import SchoolYear
from .startend import StartEndMixin
from .utils import PaymentStatus


@python_2_unicode_compatible
class ClubGroup(models.Model):
    name    = models.CharField(_('name'), max_length=150)
    plural  = models.CharField(_('plural'), max_length=150)
    color   = ColorField(_('color'))
    order   = models.IntegerField(_('order'), blank=True, default=0)

    class Meta:
        app_label           = 'leprikon'
        ordering            = ('order',)
        verbose_name        = _('club group')
        verbose_name_plural = _('club groups')

    def __str__(self):
        return self.name

    @cached_property
    def font_color(self):
        (h, s, v) = colorsys.rgb_to_hsv(
            int(self.color[1:3], 16) / 255.0,
            int(self.color[3:5], 16) / 255.0,
            int(self.color[5:6], 16) / 255.0,
        )
        if v > .5:
            v = 0
        else:
            v = 1
        if s > .5:
            s = 0
        else:
            s = 1
        (r, g, b) = colorsys.hsv_to_rgb(h, s, v)
        return '#{:02x}{:02x}{:02x}'.format(
            int(r*255),
            int(g*255),
            int(b*255),
        )



@python_2_unicode_compatible
class Club(models.Model):
    school_year = models.ForeignKey(SchoolYear, verbose_name=_('school year'), related_name='clubs')
    name        = models.CharField(_('name'), max_length=150)
    description = HTMLField(_('description'), blank=True, default='')
    groups      = models.ManyToManyField(ClubGroup, verbose_name=_('groups'), related_name='clubs')
    place       = models.ForeignKey(Place, verbose_name=_('place'), related_name='clubs', blank=True, null=True)
    age_groups  = models.ManyToManyField(AgeGroup, verbose_name=_('age groups'), related_name='clubs', blank=True)
    leaders     = models.ManyToManyField(Leader, verbose_name=_('leaders'), related_name='clubs', blank=True)
    price       = PriceField(_('price'))
    unit        = models.CharField(_('unit'), max_length=150)
    public      = models.BooleanField(_('public'), default=False)
    reg_active  = models.BooleanField(_('active registration'), default=False)
    photo       = FilerImageField(verbose_name=_('photo'), related_name='+', blank=True, null=True)
    page        = PageField(verbose_name=_('page'), related_name='+', blank=True, null=True)
    min_count   = models.IntegerField(_('minimal count'), blank=True, null=True)
    max_count   = models.IntegerField(_('maximal count'), blank=True, null=True)
    risks       = HTMLField(_('risks'), blank=True)
    plan        = HTMLField(_('plan'), blank=True)
    evaluation  = HTMLField(_('evaluation'), blank=True)
    note        = models.CharField(_('note'), max_length=300, blank=True, default='')
    questions   = models.ManyToManyField(Question, verbose_name=_('additional questions'),
                    blank=True,
                    help_text=_('Add additional questions to be asked in the registration form.'))

    class Meta:
        app_label           = 'leprikon'
        ordering            = ('name',)
        verbose_name        = _('club')
        verbose_name_plural = _('clubs')

    def __str__(self):
        return '{} {}'.format(self.school_year, self.name)

    @cached_property
    def all_groups(self):
        return list(self.groups.all())

    @cached_property
    def all_age_groups(self):
        return list(self.age_groups.all())

    @cached_property
    def all_leaders(self):
        return list(self.leaders.all())

    @cached_property
    def all_times(self):
        return list(self.times.all())

    @cached_property
    def all_periods(self):
        return list(self.periods.all())

    @cached_property
    def all_questions(self):
        return list(self.questions.all())

    @cached_property
    def all_attachments(self):
        return list(self.attachments.all())

    @cached_property
    def all_registrations(self):
        return list(self.registrations.all())

    @cached_property
    def all_journal_entries(self):
        return list(self.journal_entries.all())

    def get_current_period(self):
        return self.periods.filter(end__gte=date.today()).first() or self.periods.last()

    def get_absolute_url(self):
        return reverse('leprikon:club_detail', args=(self.id,))

    def get_public_registration_url(self):
        return reverse('leprikon:club_registration_public', args=(self.id,))

    def get_registration_url(self, participant):
        return reverse('leprikon:club_registration_form', kwargs={'club': self.id, 'participant': participant.id})

    def get_edit_url(self):
        return reverse('admin:leprikon_club_change', args=(self.id,))

    def get_groups_list(self):
        return comma_separated(self.all_groups)
    get_groups_list.short_description = _('groups list')

    def get_leaders_list(self):
        return comma_separated(self.all_leaders)
    get_leaders_list.short_description = _('leaders list')

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



@python_2_unicode_compatible
class ClubTime(StartEndMixin, models.Model):
    club        = models.ForeignKey(Club, verbose_name=_('club'), related_name='times')
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
class ClubPeriod(StartEndMixin, models.Model):
    club        = models.ForeignKey(Club, verbose_name=_('club'), related_name='periods')
    name        = models.CharField(_('name'), max_length=150)
    start       = models.DateField(_('start date'))
    end         = models.DateField(_('end date'))

    class Meta:
        app_label           = 'leprikon'
        ordering            = ('club__name', 'start')
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
        return self.club.journal_entries.filter(date__gte=self.start, date__lte=self.end)

    @cached_property
    def all_journal_entries(self):
        return list(self.journal_entries.all())

    @cached_property
    def all_registrations(self):
        return list(self.club.registrations.filter(created__lt=self.end))

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
                    reg.participant in entry.all_participants
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
            ) for leader in self.club.all_leaders
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



@python_2_unicode_compatible
class ClubAttachment(models.Model):
    club    = models.ForeignKey(Club, verbose_name=_('club'), related_name='attachments')
    file    = FilerFileField(related_name='+')
    order   = models.IntegerField(_('order'), blank=True, default=0)

    class Meta:
        app_label           = 'leprikon'
        ordering            = ('order',)
        verbose_name        = _('attachment')
        verbose_name_plural = _('attachments')

    def __str__(self):
        return force_text(self.file)



@python_2_unicode_compatible
class ClubRegistration(models.Model):
    slug            = models.SlugField(editable=False)
    created         = models.DateTimeField(_('time of registration'), editable=False, auto_now_add=True)
    club            = models.ForeignKey(Club, verbose_name=_('club'), related_name='registrations')
    participant     = models.ForeignKey(Participant, verbose_name=_('participant'), related_name='club_registrations')
    age_group       = models.ForeignKey(AgeGroup, verbose_name=_('age group'), related_name='+')
    citizenship     = models.CharField(_('citizenship'),  max_length=50)
    insurance       = models.CharField(_('insurance'),    max_length=50)
    school          = models.ForeignKey(School, verbose_name=_('school'), related_name='club_registrations', blank=True, null=True)
    school_other    = models.CharField(_('other school'), max_length=150, blank=True, default='')
    school_class    = models.CharField(_('class'),        max_length=30,  blank=True, default='')
    health          = models.TextField(_('health'), blank=True, default='')
    answers         = models.TextField(_('additional answers'), blank=True, default='{}', editable=False)
    cancel_request  = models.BooleanField(_('cancel request'), default=False)
    canceled        = models.DateField(_('date of cancellation'), blank=True, null=True)
    discount        = PriceField(_('discount'), default=0)
    explanation     = models.TextField(_('discount explanation'), blank=True, default='')

    class Meta:
        app_label           = 'leprikon'
        verbose_name        = _('club registration')
        verbose_name_plural = _('club registrations')
        unique_together     = (('club', 'participant'),)

    def __str__(self):
        return _('{participant} - {subject}').format(
            participant = self.participant,
            subject     = self.club,
        )

    def get_answers(self):
        return loads(self.answers)

    @property
    def subject(self):
        return self.club

    @cached_property
    def all_periods(self):
        if self.canceled:
            return list(self.club.periods.filter(end__gt=self.created, start__lt=self.canceled))
        else:
            return list(self.club.periods.filter(end__gt=self.created))

    @cached_property
    def all_payments(self):
        return list(self.payments.all())

    @cached_property
    def school_name(self):
        return self.school and smart_text(self.school) or self.school_other

    @cached_property
    def school_and_class(self):
        if self.school_name and self.school_class:
            return '{}, {}'.format(self.school_name, self.school_class)
        else:
            return self.school_name or self.school_class or ''

    @cached_property
    def all_recipients(self):
        recipients = set()
        if self.participant.user.email:
            recipients.add(self.participant.user.email)
        for parent in self.participant.all_parents:
            if parent.email:
                recipients.add(parent.email)
        return recipients

    def get_payments(self, d=None):
        if d:
            return filter(lambda p: p.date <= d, self.all_payments)
        else:
            return self.all_payments

    def get_paid(self, d=None):
        return sum(p.amount for p in self.get_payments(d))

    @cached_property
    def period_payment_statuses(self):
        return self.get_payment_statuses()

    PeriodPaymentStatus = namedtuple('PeriodPaymentStatus', ('period', 'status'))
    def get_period_payment_statuses(self, d=None):
        price       = self.club.price
        paid        = self.get_paid(d)
        discount    = self.discount
        for period in self.all_periods:
            yield self.PeriodPaymentStatus(
                period  = period,
                status  = PaymentStatus(
                    price       = price,
                    discount    = discount,
                    paid        = min(price - discount, paid),
                ),
            )
            paid = max(paid - (price - discount), 0)
            discount = 0 # discount if one for all periods

    @cached_property
    def payment_statuses(self):
        return self.get_payment_statuses()

    PaymentStatuses = namedtuple('PaymentStatuses', ('partial', 'total'))
    def get_payment_statuses(self, d=None):
        if d is None:
            d = date.today()
        price = self.club.price
        partial_price   = price * len(filter(lambda p: p.start <= d, self.all_periods))
        total_price     = price * len(self.all_periods)
        paid            = self.get_paid(d)
        return self.PaymentStatuses(
            partial = PaymentStatus(price = partial_price, discount = self.discount, paid = paid),
            total   = PaymentStatus(price = total_price,   discount = self.discount, paid = paid),
        )

    def get_absolute_url(self):
        return reverse('leprikon:club_registration_pdf', kwargs={'slug':self.slug})

    def send_mail(self):
        get_mailer('ClubRegistration')().send_mail(self)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(smart_text(self))
        if self.canceled:
            self.cancel_request = False
        super(ClubRegistration, self).save(*args, **kwargs)



@python_2_unicode_compatible
class ClubPayment(models.Model):
    registration    = models.ForeignKey(ClubRegistration, verbose_name=_('registration'), related_name='payments', on_delete=models.PROTECT)
    date            = models.DateField(_('payment date'))
    amount          = PriceField(_('amount'))

    class Meta:
        app_label           = 'leprikon'
        verbose_name        = _('club payment')
        verbose_name_plural = _('club payments')

    def __str__(self):
        return '{registration}, {amount}'.format(
            registration    = self.registration,
            amount          = currency(self.amount),
        )



def get_default_agenda():
    return '<p>{}</p>'.format(_('instruction on OSH'))

@python_2_unicode_compatible
class ClubJournalEntry(StartEndMixin, models.Model):
    club        = models.ForeignKey(Club, verbose_name=_('club'), related_name='journal_entries', editable=False)
    date        = models.DateField(_('date'))
    start       = models.TimeField(_('start time'), blank=True, null=True,
                    help_text=_('Leave empty, if the club does not take place'))
    end         = models.TimeField(_('end time'), blank=True, null=True,
                    help_text=_('Leave empty, if the club does not take place'))
    agenda      = HTMLField(_('session agenda'), default=get_default_agenda)
    participants = models.ManyToManyField(Participant, verbose_name=_('participants'),
                    blank=True, related_name='journal_entries')

    class Meta:
        app_label           = 'leprikon'
        ordering            = ('date', 'start', 'end')
        verbose_name        = _('journal entry')
        verbose_name_plural = _('journal entries')

    def __str__(self):
        return '{club}, {date}'.format(
            club    = self.club.name,
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
    def all_participants(self):
        return list(self.participants.all())

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
            if le.timesheet.leader in self.club.all_leaders
        )

    @cached_property
    def all_alternates(self):
        return list(
            le.timesheet.leader for le in self.all_leader_entries
            if le.timesheet.leader not in self.club.all_leaders
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
        super(ClubJournalEntry, self).save(*args, **kwargs)

    def get_edit_url(self):
        return reverse('leprikon:clubjournalentry_update', args=(self.id,))

    def get_delete_url(self):
        return reverse('leprikon:clubjournalentry_delete', args=(self.id,))



@python_2_unicode_compatible
class ClubJournalLeaderEntry(StartEndMixin, models.Model):
    club_entry  = models.ForeignKey(ClubJournalEntry, verbose_name=_('club journal entry'), related_name='leader_entries', editable=False)
    timesheet   = models.ForeignKey('leprikon.Timesheet', verbose_name=_('timesheet'), related_name='club_entries', editable=False)
    start       = models.TimeField(_('start time'))
    end         = models.TimeField(_('end time'))

    class Meta:
        app_label   = 'leprikon'
        verbose_name        = _('club journal leader entry')
        verbose_name_plural = _('club journal leader entries')
        unique_together     = (('club_entry', 'timesheet'),)

    def __str__(self):
        return '{}'.format(self.duration)

    @cached_property
    def date(self):
        return self.club_entry.date
    date.short_description = _('date')
    date.admin_order_field = 'club_entry__date'

    @cached_property
    def club(self):
        return self.club_entry.club
    club.short_description = _('club')

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
        return self.club

    def get_edit_url(self):
        return reverse('leprikon:clubjournalleaderentry_update', args=(self.id,))

    def get_delete_url(self):
        return reverse('leprikon:clubjournalleaderentry_delete', args=(self.id,))



class LeprikonClubListPlugin(CMSPlugin):
    school_year = models.ForeignKey(SchoolYear, verbose_name=_('school year'),
                    blank=True, null=True)
    age_groups  = models.ManyToManyField(AgeGroup, verbose_name=_('age groups'),
                    blank=True,
                    help_text=_('Keep empty to skip filtering by age groups.'))
    groups      = models.ManyToManyField(ClubGroup, verbose_name=_('club groups'),
                    blank=True,
                    help_text=_('Keep empty to skip filtering by groups.'))
    leaders     = models.ManyToManyField(Leader, verbose_name=_('leaders'),
                    blank=True,
                    help_text=_('Keep empty to skip filtering by leaders.'))
    template    = models.CharField(_('template'), max_length=100,
                    choices=settings.LEPRIKON_CLUBLIST_TEMPLATES,
                    default=settings.LEPRIKON_CLUBLIST_TEMPLATES[0][0],
                    help_text=_('The template used to render plugin.'))

    class Meta:
        app_label = 'leprikon'

    def copy_relations(self, oldinstance):
        self.groups     = oldinstance.groups.all()
        self.age_groups = oldinstance.age_groups.all()
        self.leaders    = oldinstance.leaders.all()



class LeprikonFilteredClubListPlugin(CMSPlugin):
    school_year = models.ForeignKey(SchoolYear, verbose_name=_('school year'),
                    blank=True, null=True)

    class Meta:
        app_label = 'leprikon'


