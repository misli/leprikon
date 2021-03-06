from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminRadioSelect
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from ..models.events import Event, EventDiscount, EventRegistration
from ..models.schoolyear import SchoolYear
from ..models.subjects import SubjectType
from ..utils import currency
from .pdf import PdfExportAdminMixin
from .subjects import (
    SubjectBaseAdmin, SubjectPaymentBaseAdmin, SubjectRegistrationBaseAdmin,
)


@admin.register(Event)
class EventAdmin(SubjectBaseAdmin):
    subject_type_type = SubjectType.EVENT
    registration_model = EventRegistration
    list_display = (
        'id', 'code', 'name', 'subject_type', 'get_groups_list', 'get_leaders_list',
        'event_date',
        'place', 'public', 'registration_allowed_icon',
        'get_registrations_link',
        'get_journal_link', 'icon', 'note',
    )
    list_export = (
        'id', 'school_year', 'code', 'name', 'department', 'subject_type', 'registration_type',
        'get_groups_list', 'get_leaders_list', 'get_age_groups_list', 'get_target_groups_list',
        'start_date', 'start_time', 'end_date', 'end_time',
        'place', 'public', 'price',
        'min_participants_count', 'max_participants_count', 'min_group_members_count', 'max_group_members_count',
        'min_registrations_count', 'max_registrations_count',
        'get_approved_registrations_count', 'get_unapproved_registrations_count', 'note',
    )
    date_hierarchy = 'start_date'
    actions = (
        'publish', 'unpublish',
        'copy_to_school_year',
    )

    def publish(self, request, queryset):
        Event.objects.filter(id__in=[reg['id'] for reg in queryset.values('id')]).update(public=True)
        self.message_user(request, _('Selected events were published.'))
    publish.short_description = _('Publish selected events')

    def unpublish(self, request, queryset):
        Event.objects.filter(id__in=[reg['id'] for reg in queryset.values('id')]).update(public=False)
        self.message_user(request, _('Selected events were unpublished.'))
    unpublish.short_description = _('Unpublish selected events')

    def copy_to_school_year(self, request, queryset):
        class SchoolYearForm(forms.Form):
            school_year = forms.ModelChoiceField(
                label=_('Target school year'),
                help_text=_('All selected events will be copied to selected school year.'),
                queryset=SchoolYear.objects.all(),
            )
        if request.POST.get('post', 'no') == 'yes':
            form = SchoolYearForm(request.POST)
            if form.is_valid():
                school_year = form.cleaned_data['school_year']
                for event in queryset.all():
                    event.copy_to_school_year(school_year)
                self.message_user(request, _('Selected events were copied to school year {}.').format(school_year))
                return
        else:
            form = SchoolYearForm()

        adminform = admin.helpers.AdminForm(
            form,
            [(None, {'fields': list(form.base_fields)})],
            {},
            None,
            model_admin=self,
        )

        return render(request, 'leprikon/admin/action_form.html', dict(
            title=_('Select target school year'),
            opts=self.model._meta,
            adminform=adminform,
            media=self.media + adminform.media,
            action='copy_to_school_year',
            action_checkbox_name=admin.helpers.ACTION_CHECKBOX_NAME,
            select_across=request.POST['select_across'],
            selected=request.POST.getlist(admin.helpers.ACTION_CHECKBOX_NAME),
        ))
    copy_to_school_year.short_description = _('Copy selected events to another school year')

    def get_message_recipients(self, request, queryset):
        return get_user_model().objects.filter(
            leprikon_registrations__subject__in=queryset,
        ).distinct()


@admin.register(EventRegistration)
class EventRegistrationAdmin(PdfExportAdminMixin, SubjectRegistrationBaseAdmin):
    subject_type_type = SubjectType.EVENT
    actions = ('add_discounts',)
    list_display = (
        'variable_symbol', 'download_tag', 'subject_name', 'participants_list_html', 'price',
        'event_discounts', 'event_payments',
        'created_with_by', 'approved_with_by', 'payment_requested_with_by',
        'cancelation_requested_with_by', 'canceled_with_by',
        'note', 'random_number',
    )

    def add_discounts(self, request, queryset):
        ABSOLUTE = 'A'
        RELATIVE = 'R'

        class DiscountForm(forms.Form):
            discount_type = forms.ChoiceField(
                label=_('Discount type'),
                choices=(
                    (ABSOLUTE, _('absolute amount')),
                    (RELATIVE, _('relative amount in percents'))
                ),
                widget=AdminRadioSelect(),
            )
            amount = forms.DecimalField(label=_('Amount or number of percents'))
            explanation = EventDiscount._meta.get_field('explanation').formfield()

        if request.POST.get('post', 'no') == 'yes':
            form = DiscountForm(request.POST)
            if form.is_valid():
                EventDiscount.objects.bulk_create(
                    EventDiscount(
                        registration=registration,
                        amount=(
                            form.cleaned_data['amount']
                            if form.cleaned_data['discount_type'] == ABSOLUTE
                            else (
                                registration.price - sum(
                                    discount.amount
                                    for discount in registration.all_discounts
                                )
                            ) * form.cleaned_data['amount'] / 100
                        ),
                        explanation=form.cleaned_data['explanation'],
                    )
                    for registration in queryset.all()
                )
                self.message_user(request, _(
                    'The discounts have been created for selected registrations.'
                ))
                return
        else:
            form = DiscountForm()

        adminform = admin.helpers.AdminForm(
            form,
            [(None, {'fields': list(form.base_fields)})],
            {},
            None,
            model_admin=self,
        )

        return render(request, 'leprikon/admin/action_form.html', dict(
            title=_('Add discounts'),
            opts=self.model._meta,
            adminform=adminform,
            media=self.media + adminform.media,
            action='add_discounts',
            action_checkbox_name=admin.helpers.ACTION_CHECKBOX_NAME,
            select_across=request.POST['select_across'],
            selected=request.POST.getlist(admin.helpers.ACTION_CHECKBOX_NAME),
        ))
    add_discounts.short_description = _('Add discounts to selected registrations')

    def event_discounts(self, obj):
        return format_html(
            '<a href="{href_list}"><b>{amount}</b></a>'
            ' &nbsp; <a class="popup-link" href="{href_add}" style="background-position: 0 0" title="{title_add}">'
            '<img src="{icon_add}" alt="+"/></a>',
            href_list=reverse('admin:leprikon_eventdiscount_changelist') + '?registration={}'.format(obj.id),
            amount=currency(obj.payment_status.discount),
            href_add=reverse('admin:leprikon_eventdiscount_add') + '?registration={}'.format(obj.id),
            icon_add=static('admin/img/icon-addlink.svg'),
            title_add=_('add discount'),
        )
    event_discounts.allow_tags = True
    event_discounts.short_description = _('event discounts')

    def event_payments(self, obj):
        return format_html(
            '<a class="popup-link" style="color: {color}" href="{href_list}" title="{title}"><b>{amount}</b></a>'
            ' &nbsp; <a class="popup-link" href="{href_add}" style="background-position: 0 0" title="{title_add}">'
            '<img src="{icon_add}" alt="+"/></a>',
            color=obj.payment_status.color,
            href_list=reverse('admin:leprikon_subjectpayment_changelist') + '?registration={}'.format(obj.id),
            title=obj.payment_status.title,
            amount=currency(obj.payment_status.paid),
            href_add=reverse('admin:leprikon_subjectpayment_add') + '?registration={}'.format(obj.id),
            icon_add=static('admin/img/icon-addlink.svg'),
            title_add=_('add payment'),
        )
    event_payments.allow_tags = True
    event_payments.short_description = _('event payments')


@admin.register(EventDiscount)
class EventDiscountAdmin(PdfExportAdminMixin, SubjectPaymentBaseAdmin):
    list_display = ('accounted', 'registration', 'subject', 'amount_html', 'explanation')
    list_export = ('accounted', 'registration', 'subject', 'amount', 'explanation')
