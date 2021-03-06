from collections import namedtuple

from django.urls import reverse_lazy as reverse
from django.utils.translation import ugettext_lazy as _

from ...forms.reports.courses import (
    CoursePaymentsForm, CoursePaymentsStatusForm, CourseStatsForm,
)
from ...forms.reports.debtors import DebtorsForm
from ...forms.reports.events import (
    EventPaymentsForm, EventPaymentsStatusForm, EventStatsForm,
)
from ...forms.reports.orderables import (
    OrderablePaymentsForm, OrderablePaymentsStatusForm, OrderableStatsForm,
)
from ..generic import GetFormView, TemplateView


class ReportsListView(TemplateView):
    template_name = 'leprikon/reports/index.html'

    Report = namedtuple('Report', ('title', 'instructions', 'form', 'url'))

    def get_form(self, form_class, **kwargs):
        return form_class(prefix=form_class.__name__, **kwargs)

    def get_context_data(self, *args, **kwargs):
        return super(ReportsListView, self).get_context_data(reports=[
            self.Report(
                title=_('Course payments'),
                instructions='',
                form=self.get_form(CoursePaymentsForm),
                url=reverse('leprikon:report_course_payments'),
            ),
            self.Report(
                title=_('Event payments'),
                instructions='',
                form=self.get_form(EventPaymentsForm),
                url=reverse('leprikon:report_event_payments'),
            ),
            self.Report(
                title=_('Orderable event payments'),
                instructions='',
                form=self.get_form(OrderablePaymentsForm),
                url=reverse('leprikon:report_orderable_payments'),
            ),
            self.Report(
                title=_('Course payments status'),
                instructions='',
                form=self.get_form(CoursePaymentsStatusForm),
                url=reverse('leprikon:report_course_payments_status'),
            ),
            self.Report(
                title=_('Event payments status'),
                instructions='',
                form=self.get_form(EventPaymentsStatusForm),
                url=reverse('leprikon:report_event_payments_status'),
            ),
            self.Report(
                title=_('Orderable event payments status'),
                instructions='',
                form=self.get_form(OrderablePaymentsStatusForm),
                url=reverse('leprikon:report_orderable_payments_status'),
            ),
            self.Report(
                title=_('Course statistics'),
                instructions='',
                form=self.get_form(CourseStatsForm, school_year=self.request.school_year),
                url=reverse('leprikon:report_course_stats'),
            ),
            self.Report(
                title=_('Event statistics'),
                instructions='',
                form=self.get_form(EventStatsForm, school_year=self.request.school_year),
                url=reverse('leprikon:report_event_stats'),
            ),
            self.Report(
                title=_('Orderable event statistics'),
                instructions='',
                form=self.get_form(OrderableStatsForm, school_year=self.request.school_year),
                url=reverse('leprikon:report_orderable_stats'),
            ),
            self.Report(
                title=_('Debtors list'),
                instructions='',
                form=self.get_form(DebtorsForm),
                url=reverse('leprikon:report_debtors'),
            ),
        ])


class ReportBaseView(GetFormView):

    def get_form_kwargs(self):
        kwargs = super(ReportBaseView, self).get_form_kwargs()
        kwargs['prefix'] = self.form_class.__name__
        return kwargs
