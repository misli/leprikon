from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from cms.models.fields import PageField
from django.db import models
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from djangocms_text_ckeditor.fields import HTMLField
from filer.fields.image import FilerImageField

from ..conf import settings

from .agegroup import AgeGroup
from .school import School
from .schoolyear import SchoolYear
from .fields import BirthNumberField, PostalCodeField



@python_2_unicode_compatible
class Leader(models.Model):
    user            = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_('user'), related_name='leprikon_leader')
    description     = HTMLField(_('description'), blank=True, default='')
    photo           = FilerImageField(verbose_name=_('photo'), related_name='+', blank=True, null=True)
    page            = PageField(verbose_name=_('page'), related_name='+', blank=True, null=True)
    school_years    = models.ManyToManyField(SchoolYear, verbose_name=_('school years'), related_name='leaders')

    class Meta:
        app_label           = 'leprikon'
        ordering            = ('user__first_name', 'user__last_name')
        verbose_name        = _('leader')
        verbose_name_plural = _('leaders')

    def __str__(self):
        return self.full_name

    @cached_property
    def first_name(self):
        return self.user.first_name

    @cached_property
    def last_name(self):
        return self.user.last_name

    @cached_property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @cached_property
    def all_contacts(self):
        return list(self.contacts.all())

    @cached_property
    def all_public_contacts(self):
        return list(self.contacts.filter(public=True))

    @cached_property
    def all_clubs(self):
        return list(self.clubs.all())

    @cached_property
    def all_events(self):
        return list(self.events.all())

    @cached_property
    def all_school_years(self):
        return list(self.school_years.all())

    def get_alternate_leader_entries(self, school_year):
        from .clubs import ClubJournalLeaderEntry
        return ClubJournalLeaderEntry.objects.filter(
            timesheet__leader               = self,
            club_entry__club__school_year   = school_year,
        ).exclude(club_entry__club__in = self.clubs.all())



@python_2_unicode_compatible
class Contact(models.Model):
    leader          = models.ForeignKey(Leader, verbose_name=_('leader'), related_name='contacts')
    contact_type    = models.CharField(_('contact type'), max_length=30,
                        choices=settings.LEPRIKON_CONTACT_TYPES)
    contact         = models.CharField(_('contact'), max_length=250)
    order           = models.IntegerField(_('order'), blank=True, default=0)
    public          = models.BooleanField(_('public'), default=False)

    CONTACT_TYPES   = dict(settings.LEPRIKON_CONTACT_TYPES)

    class Meta:
        app_label           = 'leprikon'
        ordering            = ('order',)
        verbose_name        = _('contact')
        verbose_name_plural = _('contacts')

    def __str__(self):
        return '{}, {}: {}'.format(self.leader.full_name, self.contact_type_name, self.contact)

    @cached_property
    def contact_type_name(self):
        return self.CONTACT_TYPES[self.contact_type]



@python_2_unicode_compatible
class Parent(models.Model):
    user            = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'),
                        related_name='leprikon_parents')
    first_name      = models.CharField(_('first name'),   max_length=30)
    last_name       = models.CharField(_('last name'),    max_length=30)
    street          = models.CharField(_('street'),       max_length=150)
    city            = models.CharField(_('city'),         max_length=150)
    postal_code     = PostalCodeField(_('postal code'))
    email           = models.EmailField(_('email address'), blank=True, default='')
    phone           = models.CharField(_('phone'), max_length=30)

    class Meta:
        app_label           = 'leprikon'
        verbose_name        = _('parent')
        verbose_name_plural = _('parents')

    def __str__(self):
        return self.full_name

    @cached_property
    def address(self):
        return '{}, {}, {}'.format(self.street, self.city, self.postal_code)

    @cached_property
    def contact(self):
        if self.email and self.phone:
            return '{}, {}'.format(self.phone, self.email)
        else:
            return self.email or self.phone or ''

    @cached_property
    def all_participants(self):
        return list(self.participants.all())

    @cached_property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)



@python_2_unicode_compatible
class Participant(models.Model):
    user            = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'),
                        related_name='leprikon_participants')
    age_group       = models.ForeignKey(AgeGroup, verbose_name=_('age group'), related_name='+')
    first_name      = models.CharField(_('first name'),   max_length=30)
    last_name       = models.CharField(_('last name'),    max_length=30)
    birth_num       = BirthNumberField(_('birth number'), unique=True)
    street          = models.CharField(_('street'),       max_length=150)
    city            = models.CharField(_('city'),         max_length=150)
    postal_code     = PostalCodeField(_('postal code'))
    email           = models.EmailField(_('email address'), blank=True, default='')
    phone           = models.CharField(_('phone'),        max_length=30,  blank=True, default='')
    citizenship     = models.CharField(_('citizenship'),  max_length=50)
    insurance       = models.CharField(_('insurance'),    max_length=50)
    school          = models.ForeignKey(School, verbose_name=_('school'), related_name='participants', blank=True, null=True)
    school_other    = models.CharField(_('other school'), max_length=150, blank=True, default='')
    school_class    = models.CharField(_('class'),        max_length=30,  blank=True, default='')
    health          = models.TextField(_('health'), blank=True, default='')

    class Meta:
        app_label           = 'leprikon'
        verbose_name        = _('participant')
        verbose_name_plural = _('participants')

    def __str__(self):
        return _('{first_name} {last_name} ({birth_num})').format(
            first_name  = self.first_name,
            last_name   = self.last_name,
            birth_num   = self.birth_num,
        )

    @cached_property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @cached_property
    def address(self):
        return '{}, {}, {}'.format(self.street, self.city, self.postal_code)

    @cached_property
    def contact(self):
        if self.email and self.phone:
            return '{}, {}'.format(self.phone, self.email)
        else:
            return self.email or self.phone or ''

    @cached_property
    def school_name(self):
        return self.school and smart_text(self.school) or self.school_other

    @cached_property
    def school_and_class(self):
        if self.school_name and self.school_class:
            return '{}, {}'.format(self.school_name, self.school_class)
        else:
            return self.school_name or self.school_class or ''

