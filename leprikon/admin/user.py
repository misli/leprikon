from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from django import forms
from django.conf.urls import url as urls_url
from django.contrib.admin import helpers
from django.contrib.auth import get_user_model, login
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.encoding import smart_text
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from ..forms.user import UserAdminCreateForm


class UserAdmin(_UserAdmin):
    actions = ('merge', 'send_message')
    add_form = UserAdminCreateForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email'),
        }),
    )

    def merge(self, request, queryset):
        class MergeForm(forms.Form):
            target = forms.ModelChoiceField(
                label=_('Target user'),
                help_text=_('All information will be merged into selected account.'),
                queryset=queryset,
            )
        if request.POST.get('post', 'no') == 'yes':
            form = MergeForm(request.POST)
            if form.is_valid():
                target = form.cleaned_data['target']
                for user in queryset.all():
                    if user == target:
                        continue
                    if not target.first_name and user.first_name:
                        target.first_name = user.first_name
                    if not target.last_name and user.last_name:
                        target.last_name = user.last_name
                    if not target.email and user.email:
                        target.email = user.email
                    try:
                        leader = user.leprikon_leader
                    except:
                        leader = None
                    if leader:
                        leader.user = target
                        leader.save()
                    for participant in user.leprikon_participants.all():
                        participant.user = target
                        participant.save()
                    for parent in user.leprikon_parents.all():
                        parent.user = target
                        parent.save()
                    user.delete()
                target.save()
                self.message_user(request, _('Selected users were merged into user {}.').format(target))
                return
        else:
            form = MergeForm()
        return render_to_response('leprikon/admin/merge.html', {
            'title':    _('Select target user for merge'),
            'question': _('Are you sure you want to merge selected users into one? '
                          'All participants, parents, registrations and other related information '
                          'will be added to the target user account and the remaining users will be deleted.'),
            'queryset': queryset,
            'objects_title':    _('Users'),
            'form_title':       _('Select target account for merge'),
            'opts': self.model._meta,
            'form': form,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        }, context_instance=RequestContext(request))
    merge.short_description = _('Merge selected user accounts')

    def get_list_display(self, request):
        return ['id'] \
            + list(super(UserAdmin, self).get_list_display(request)) \
            + ['parents_link', 'participants_link', 'login_as_link']

    def get_search_fields(self, request):
        return list(super(UserAdmin, self).get_search_fields(request))+[
            'leprikon_parents__first_name',
            'leprikon_parents__last_name',
            'leprikon_parents__email',
            'leprikon_participants__first_name',
            'leprikon_participants__last_name',
            'leprikon_participants__email',
        ]

    def get_urls(self):
        urls = super(UserAdmin, self).get_urls()
        login_as_view = self.admin_site.admin_view(user_passes_test(lambda u: u.is_superuser)(self.login_as))
        return [
            urls_url(r'(?P<user_id>\d+)/login-as/$', login_as_view, name='auth_user_login_as'),
        ] + urls

    def login_as(self, request, user_id):
        user = get_object_or_404(get_user_model(), id=user_id)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return HttpResponseRedirect(reverse('leprikon:summary'))

    def login_as_link(self, obj):
        return '<a href="{url}">{text}</a>'.format(
            url     = reverse('admin:auth_user_login_as', args=[obj.id]),
            text    = _('login')
        )
    login_as_link.allow_tags = True
    login_as_link.short_description = _('login')

    @cached_property
    def parents_url(self):
        return reverse('admin:leprikon_parent_changelist')

    def parents_link(self, obj):
        return '<a href="{url}?user__id={user}">{names}</a>'.format(
            url     = self.parents_url,
            user    = obj.id,
            names   = ', '.join(smart_text(parent) for parent in obj.leprikon_parents.all()),
        )
    parents_link.allow_tags = True
    parents_link.short_description = _('parents')

    @cached_property
    def participants_url(self):
        return reverse('admin:leprikon_participant_changelist')

    def participants_link(self, obj):
        return '<a href="{url}?user__id={user}">{names}</a>'.format(
            url     = self.participants_url,
            user    = obj.id,
            names   = ', '.join(smart_text(participant) for participant in obj.leprikon_participants.all()),
        )
    participants_link.allow_tags = True
    participants_link.short_description = _('participants')

    def send_message(self, request, queryset):
        return HttpResponseRedirect('{url}?recipients={recipients}'.format(
            url         = reverse('admin:leprikon_message_add'),
            recipients  = ','.join(str(u.id) for u in queryset.all()),
        ))
    send_message.short_description = _('Send message')

