# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import cPickle
import logging

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
# from horizon import messages
from horizon import tables
from horizon import tabs
from horizon.utils import memoized

from openstack_dashboard.api import iotronic, keystone
from openstack_dashboard import policy

from iotronic_ui.iot.plugins import forms as project_forms
from iotronic_ui.iot.plugins import tables as project_tables
from iotronic_ui.iot.plugins import tabs as project_tabs

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = project_tables.PluginsTable
    template_name = 'iot/plugins/index.html'
    page_title = _("Plugins")

    def get_data(self):
        plugins = []
        users = []

        # Admin
        if policy.check((("iot", "iot:list_all_plugins"),), self.request):
            try:
                plugins = iotronic.plugin_list(self.request, None, None,
                                               all_plugins=True)
                users = keystone.user_list(self.request)

            except Exception:
                exceptions.handle(self.request, _('Unable to retrieve plugins \
                                  list.'))

        # Admin_iot_project
        elif policy.check((("iot", "iot:list_project_plugins"),),
                          self.request):
            try:
                plugins = iotronic.plugin_list(self.request, None, None,
                                               with_public=True)

            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve user plugins list.'))

        # Other users
        else:
            try:
                plugins = iotronic.plugin_list(self.request, None, None,
                                               with_public=True)

            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve user plugins list.'))

        # Replace owner column values (user.id) with user.name (only Admin
        # can see human-readable names)
        for plugin in plugins:
            for user in users:
                if plugin.owner == user.id:
                    plugin.owner = user.name
                    break

        return plugins


class CreateView(forms.ModalFormView):
    template_name = 'iot/plugins/create.html'
    modal_header = _("Create Plugin")
    form_id = "create_plugin_form"
    form_class = project_forms.CreatePluginForm
    submit_label = _("Create Plugin")
    submit_url = reverse_lazy("horizon:iot:plugins:create")
    success_url = reverse_lazy('horizon:iot:plugins:index')
    page_title = _("Create Plugin")


class InjectView(forms.ModalFormView):
    template_name = 'iot/plugins/inject.html'
    modal_header = _("Inject Plugin")
    form_id = "inject_plugin_form"
    form_class = project_forms.InjectPluginForm
    submit_label = _("Inject Plugin")
    # submit_url = reverse_lazy("horizon:iot:plugins:inject")
    submit_url = "horizon:iot:plugins:inject"
    success_url = reverse_lazy('horizon:iot:plugins:index')
    page_title = _("Inject Plugin")

    @memoized.memoized_method
    def get_object(self):
        try:
            return iotronic.plugin_get(self.request, self.kwargs['plugin_id'],
                                       None)
        except Exception:
            redirect = reverse("horizon:iot:plugins:index")
            exceptions.handle(self.request,
                              _('Unable to get plugin information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(InjectView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        plugin = self.get_object()

        # Populate boards
        boards = iotronic.board_list(self.request, "online", None, None)
        boards.sort(key=lambda b: b.name)

        board_list = []
        for board in boards:
            board_list.append((board.uuid, _(board.name)))

        return {'uuid': plugin.uuid,
                'name': plugin.name,
                'board_list': board_list}


class StartView(forms.ModalFormView):
    template_name = 'iot/plugins/start.html'
    modal_header = _("Start Plugin")
    form_id = "start_plugin_form"
    form_class = project_forms.StartPluginForm
    submit_label = _("Start Plugin")
    # submit_url = reverse_lazy("horizon:iot:plugins:start")
    submit_url = "horizon:iot:plugins:start"
    success_url = reverse_lazy('horizon:iot:plugins:index')
    page_title = _("Start Plugin")

    @memoized.memoized_method
    def get_object(self):
        try:
            return iotronic.plugin_get(self.request, self.kwargs['plugin_id'],
                                       None)
        except Exception:
            redirect = reverse("horizon:iot:plugins:index")
            exceptions.handle(self.request,
                              _('Unable to get plugin information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(StartView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        plugin = self.get_object()

        # Populate boards
        boards = iotronic.board_list(self.request, "online", None, None)
        boards.sort(key=lambda b: b.name)

        board_list = []
        for board in boards:
            board_list.append((board.uuid, _(board.name)))

        return {'uuid': plugin.uuid,
                'name': plugin.name,
                'board_list': board_list}


class StopView(forms.ModalFormView):
    template_name = 'iot/plugins/stop.html'
    modal_header = _("Stop Plugin")
    form_id = "stop_plugin_form"
    form_class = project_forms.StopPluginForm
    submit_label = _("Stop Plugin")
    # submit_url = reverse_lazy("horizon:iot:plugins:stop")
    submit_url = "horizon:iot:plugins:stop"
    success_url = reverse_lazy('horizon:iot:plugins:index')
    page_title = _("Stop Plugin")

    @memoized.memoized_method
    def get_object(self):
        try:
            return iotronic.plugin_get(self.request, self.kwargs['plugin_id'],
                                       None)
        except Exception:
            redirect = reverse("horizon:iot:plugins:index")
            exceptions.handle(self.request,
                              _('Unable to get plugin information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(StopView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        plugin = self.get_object()

        # Populate boards
        boards = iotronic.board_list(self.request, "online", None, None)
        boards.sort(key=lambda b: b.name)

        board_list = []
        for board in boards:
            board_list.append((board.uuid, _(board.name)))

        return {'uuid': plugin.uuid,
                'name': plugin.name,
                'board_list': board_list}


class CallView(forms.ModalFormView):
    template_name = 'iot/plugins/call.html'
    modal_header = _("Call Plugin")
    form_id = "call_plugin_form"
    form_class = project_forms.CallPluginForm
    submit_label = _("Call Plugin")
    # submit_url = reverse_lazy("horizon:iot:plugins:call")
    submit_url = "horizon:iot:plugins:call"
    success_url = reverse_lazy('horizon:iot:plugins:index')
    page_title = _("Call Plugin")

    @memoized.memoized_method
    def get_object(self):
        try:
            return iotronic.plugin_get(self.request, self.kwargs['plugin_id'],
                                       None)
        except Exception:
            redirect = reverse("horizon:iot:plugins:index")
            exceptions.handle(self.request,
                              _('Unable to get plugin information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(CallView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        plugin = self.get_object()

        # Populate boards
        boards = iotronic.board_list(self.request, "online", None, None)
        boards.sort(key=lambda b: b.name)

        board_list = []
        for board in boards:
            board_list.append((board.uuid, _(board.name)))

        return {'uuid': plugin.uuid,
                'name': plugin.name,
                'board_list': board_list}


class RemoveView(forms.ModalFormView):
    template_name = 'iot/plugins/remove.html'
    modal_header = _("Remove Plugin")
    form_id = "remove_plugin_form"
    form_class = project_forms.RemovePluginForm
    submit_label = _("Remove Plugin")
    # submit_url = reverse_lazy("horizon:iot:plugins:remove")
    submit_url = "horizon:iot:plugins:remove"
    success_url = reverse_lazy('horizon:iot:plugins:index')
    page_title = _("Remove Plugin")

    @memoized.memoized_method
    def get_object(self):
        try:
            return iotronic.plugin_get(self.request, self.kwargs['plugin_id'],
                                       None)
        except Exception:
            redirect = reverse("horizon:iot:plugins:index")
            exceptions.handle(self.request,
                              _('Unable to get plugin information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(RemoveView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        plugin = self.get_object()

        # Populate boards
        boards = iotronic.board_list(self.request, "online", None, None)
        boards.sort(key=lambda b: b.name)

        board_list = []
        for board in boards:
            board_list.append((board.uuid, _(board.name)))

        return {'uuid': plugin.uuid,
                'name': plugin.name,
                'board_list': board_list}


class UpdateView(forms.ModalFormView):
    template_name = 'iot/plugins/update.html'
    modal_header = _("Update Plugin")
    form_id = "update_plugin_form"
    form_class = project_forms.UpdatePluginForm
    submit_label = _("Update Plugin")
    submit_url = "horizon:iot:plugins:update"
    success_url = reverse_lazy('horizon:iot:plugins:index')
    page_title = _("Update Plugin")

    @memoized.memoized_method
    def get_object(self):
        try:
            return iotronic.plugin_get(self.request, self.kwargs['plugin_id'],
                                       None)
        except Exception:
            redirect = reverse("horizon:iot:plugins:index")
            exceptions.handle(self.request,
                              _('Unable to get plugin information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        plugin = self.get_object()

        # Deserialize the code of the plugin
        plugin.code = cPickle.loads(str(plugin.code))

        return {'uuid': plugin.uuid,
                'owner': plugin.owner,
                'name': plugin.name,
                'public': plugin.public,
                'callable': plugin.callable,
                'code': plugin.code}


class DetailView(tabs.TabView):

    tab_group_class = project_tabs.PluginDetailTabs
    template_name = 'horizon/common/_detail.html'
    page_title = "{{ plugin.name|default:plugin.uuid }}"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)

        plugin = self.get_data()
        context["plugin"] = plugin
        context["url"] = reverse(self.redirect_url)
        context["actions"] = self._get_actions(plugin)

        return context

    def _get_actions(self, plugin):
        table = project_tables.PluginsTable(self.request)
        return table.render_row_actions(plugin)

    @memoized.memoized_method
    def get_data(self):
        plugin_id = self.kwargs['plugin_id']
        try:
            plugin = iotronic.plugin_get(self.request, plugin_id, None)
        except Exception:
            msg = ('Unable to retrieve plugin %s information') % {'name':
                                                                  plugin.name}
            exceptions.handle(self.request, msg, ignore=True)
        return plugin

    def get_tabs(self, request, *args, **kwargs):
        plugin = self.get_data()
        return self.tab_group_class(request, plugin=plugin, **kwargs)


class PluginDetailView(DetailView):
    redirect_url = 'horizon:iot:plugins:index'

    def _get_actions(self, plugin):

        # Deserialize the code of the plugin
        plugin.code = cPickle.loads(str(plugin.code))

        table = project_tables.PluginsTable(self.request)
        return table.render_row_actions(plugin)
