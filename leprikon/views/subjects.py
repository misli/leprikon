from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy as reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from ..forms.subjects import (
    CourseRegistrationForm, EventRegistrationForm, SubjectFilterForm,
    SubjectForm,
)
from ..models.courses import Course
from ..models.events import Event
from ..models.subjects import (
    Subject, SubjectRegistration, SubjectRegistrationRequest, SubjectType,
)
from .generic import (
    ConfirmCreateView, ConfirmUpdateView, CreateView, DetailView,
    FilteredListView, PdfView, UpdateView,
)


class SubjectTypeMixin(object):
    _models = {
        SubjectType.COURSE: Course,
        SubjectType.EVENT:  Event,
    }

    def get_template_names(self):
        return [
            'leprikon/{}{}.html'.format(self.subject_type.slug, self.template_name_suffix),
            'leprikon/{}{}.html'.format(self.subject_type.subject_type, self.template_name_suffix),
            'leprikon/subject{}.html'.format(self.template_name_suffix),
        ]

    def dispatch(self, request, subject_type, *args, **kwargs):
        self.subject_type = get_object_or_404(SubjectType, slug=subject_type)
        self.model = self._models[self.subject_type.subject_type]
        return super(SubjectTypeMixin, self).dispatch(request, **kwargs)

    def get_queryset(self):
        return super(SubjectTypeMixin, self).get_queryset().filter(subject_type=self.subject_type)



class SubjectListView(SubjectTypeMixin, FilteredListView):
    form_class          = SubjectFilterForm
    preview_template    = 'leprikon/subject_preview.html'
    paginate_by         = 10

    def get_title(self):
        return _('{subject_type} in school year {school_year}').format(
            subject_type    = self.subject_type.plural,
            school_year     = self.request.school_year,
        )

    def get_message_empty(self):
        return _('No {subject_type} matching given search parameters.').format(
            subject_type    = self.subject_type.name,
        )

    def get_form(self):
        return self.form_class(
            request         = self.request,
            subject_type    = self.subject_type,
            data            = self.request.GET,
        )

    def get_queryset(self):
        return self.get_form().get_queryset()



class SubjectListMineView(SubjectListView):

    def get_template_names(self):
        return [
            'leprikon/{}_list_mine.html'.format(self.subject_type.slug),
            'leprikon/{}_list_mine.html'.format(self.subject_type.subject_type),
            'leprikon/subject_list_mine.html',
        ] + super(SubjectListMineView, self).get_template_names()

    def get_title(self):
        return _('My {subject_type} in school year {school_year}').format(
            subject_type = self.subject_type.plural,
            school_year = self.request.school_year,
        )

    def get_queryset(self):
        return super(SubjectListMineView, self).get_queryset().filter(leaders=self.request.leader)



class SubjectDetailView(SubjectTypeMixin, DetailView):

    def get_queryset(self):
        qs = super(SubjectDetailView, self).get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(public=True)
        return qs



class SubjectRegistrationsView(SubjectTypeMixin, DetailView):
    template_name_suffix = '_registrations'

    def get_queryset(self):
        qs = super(SubjectRegistrationsView, self).get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(leaders=self.request.leader)
        return qs



class SubjectUpdateView(SubjectTypeMixin, UpdateView):
    form_class  = SubjectForm

    def get_title(self):
        return _('Change {subject_type} {subject}').format(
            subject_type = self.subject_type.name_akuzativ,
            subject = self.object.name,
        )

    def get_message(self):
        return _('The {} {} has been updated.').format(
            subject_type = self.subject_type.name,
            subject = self.object.name,
        )

    def get_queryset(self):
        qs = self.models[self.subject.subject_type.subject_type].objects.all()
        if not self.request.user.is_staff:
            qs = qs.filter(leaders=self.request.leader)
        return qs



class SubjectRegistrationRequestFormView(ConfirmCreateView):
    back_url        = reverse('leprikon:registration_list')
    model           = SubjectRegistrationRequest
    message         = _('The registration request has been accepted.')

    def get_title(self):
        return _('Registration request for {subject_type} {subject}').format(
            subject_type = self.kwargs['subject_type'].name_akuzativ,
            subject = self.kwargs['subject'].name,
        )

    def get_question(self):
        return _('Do You want us to contact You if someone cancels the registration?')

    def get_instructions(self):
        instructions = _(
            'We apologize, the capacity of {subject_type} {subject} has already been filled.'
        ).format(
            subject_type = self.kwargs['subject_type'].name_genitiv,
            subject = self.kwargs['subject'].name,
        )
        return '<p>{}</p>'.format(instructions)

    def confirmed(self):
        SubjectRegistrationRequest.objects.get_or_create(subject=self.kwargs['subject'], user=self.request.user)



class SubjectRegistrationFormView(CreateView):
    back_url        = reverse('leprikon:registration_list')
    submit_label    = _('Submit registration')
    message         = _('The registration has been accepted.')
    _models = {
        SubjectType.COURSE: Course,
        SubjectType.EVENT:  Event,
    }
    _form_classes = {
        SubjectType.COURSE: CourseRegistrationForm,
        SubjectType.EVENT:  EventRegistrationForm,
    }

    def get_template_names(self):
        return [
            'leprikon/{}_registration_form.html'.format(self.subject_type.slug, self.template_name_suffix),
            'leprikon/{}_registration_form.html'.format(self.subject_type.subject_type, self.template_name_suffix),
            'leprikon/subject_registration_form.html'.format(self.template_name_suffix),
        ]

    def get_title(self):
        return _('Registration for {subject_type} {subject}').format(
            subject_type = self.subject_type.name_akuzativ,
            subject = self.subject.name,
        )

    def dispatch(self, request, subject_type, pk, **kwargs):
        self.subject_type = get_object_or_404(SubjectType, slug=subject_type)
        lookup_kwargs = {
            'subject_type': self.subject_type,
            'id':           int(pk),
        }
        if not self.request.user.is_staff:
            lookup_kwargs['public'] = True
        self.subject = get_object_or_404(Subject, **lookup_kwargs)
        self.request.school_year = self.subject.school_year
        if not self.subject.registration_allowed:
            return SubjectRegistrationRequestFormView.as_view()(
                request, subject_type=self.subject_type, subject=self.subject
            )
        self.model = self._models[self.subject.subject_type.subject_type]
        return super(SubjectRegistrationFormView, self).dispatch(request, **kwargs)

    def get_form_class(self):
        return self._form_classes[self.subject.subject_type.subject_type]

    def get_form_kwargs(self):
        kwargs  = super(SubjectRegistrationFormView, self).get_form_kwargs()
        kwargs['subject'] = self.subject
        kwargs['user'] = self.request.user
        return kwargs



class UserRegistrationMixin(object):
    model = SubjectRegistration

    def get_queryset(self):
        return super(UserRegistrationMixin, self).get_queryset().filter(user=self.request.user)

    def get_template_names(self):
        return [self.template_name] if self.template_name else [
            'leprikon/{}_registration{}.html'.format(self.object.subject.subject_type.slug,
                                                     self.template_name_suffix),
            'leprikon/{}_registration{}.html'.format(self.object.subject.subject_type.subject_type,
                                                     self.template_name_suffix),
            'leprikon/subject_registration{}.html'.format(self.template_name_suffix),
        ]



class SubjectRegistrationConfirmView(UserRegistrationMixin, DetailView):
    template_name_suffix = '_confirm'



class SubjectRegistrationPdfView(UserRegistrationMixin, PdfView):

    def get_template_names(self):
        return [
            'leprikon/{}_registration.rml.html'.format(self.object.subject.subject_type.slug),
            'leprikon/{}_registration.rml.html'.format(self.object.subject.subject_type.subject_type),
            'leprikon/subject_registration.rml.html',
        ]

    def get_printsetup(self):
        return self.object.subject.reg_printsetup or self.object.subject.subject_type.reg_printsetup



class SubjectRegistrationCancelView(UserRegistrationMixin, ConfirmUpdateView):
    template_name_suffix = '_cancel'
    title = _('Registration cancellation request')

    def get_question(self):
        return _('Are you sure You want to cancel the registration "{}"?').format(self.object)

    def get_message(self):
        return _('The cancellation request for {} has been saved.').format(self.object)

    def confirmed(self):
        self.object.cancel_request = True
        self.object.save()
