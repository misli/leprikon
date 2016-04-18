from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from django.core.urlresolvers import reverse_lazy as reverse
from django.db.models import Q
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from ..models import MessageRecipient
from ..forms.messages import MessageFilterForm

from .generic import BackViewMixin, FilteredListView, DetailView


class MessageListView(FilteredListView):
    model               = MessageRecipient
    form_class          = MessageFilterForm
    preview_template    = 'leprikon/message_preview.html'
    template_name       = 'leprikon/message_list.html'
    message_empty       = _('No messages matching given query.')
    paginate_by         = 10

    def get_title(self):
        return _('Messages')

    def get_queryset(self):
        qs = self.request.user.leprikon_messages.all()
        form = self.get_form()
        if form.is_valid():
            qs = form.filter_queryset(self.request, qs)
        return qs


class MessageDetailView(BackViewMixin, DetailView):
    back_url = reverse('leprikon:message_list')
    model = MessageRecipient

    def get_object(self):
        obj = super(MessageDetailView, self).get_object()
        if obj.received is None:
            obj.received = now()
            obj.save()
        return obj

