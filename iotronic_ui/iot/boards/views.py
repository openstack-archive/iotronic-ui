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

from openstack_dashboard.api import iotronic
from openstack_dashboard import policy

from iotronic_ui.iot.boards import forms as project_forms
from iotronic_ui.iot.boards import tables as project_tables
from iotronic_ui.iot.boards import tabs as project_tabs


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = project_tables.BoardsTable
    template_name = 'iot/boards/index.html'
    page_title = _("Boards")

    def get_data(self):
        boards = []

        # FROM
        """
        if policy.check((("identity", "identity:list_roles"),), self.request):
            try:
                boards = iotronic.board_list(self.request, None, None)
                # LOG.debug('IOT BOARDS: %s', boards)
            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve boards list.'))
        else:
            msg = _("Insufficient privilege level to view boards information.")
            messages.info(self.request, msg)
        """

        # TO
        # Admin
        if policy.check((("iot", "iot:list_all_boards"),), self.request):
            try:
                boards = iotronic.board_list(self.request, None, None)

            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve boards list.'))

        # Admin_iot_project
        elif policy.check((("iot", "iot:list_project_boards"),), self.request):
            try:
                boards = iotronic.board_list(self.request, None, None)

            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve user boards list.'))

        # Other users
        else:
            try:
                boards = iotronic.board_list(self.request, None, None)

            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve user boards list.'))

        return boards


class CreateView(forms.ModalFormView):
    template_name = 'iot/boards/create.html'
    modal_header = _("Create Board")
    form_id = "create_board_form"
    form_class = project_forms.CreateBoardForm
    submit_label = _("Create Board")
    submit_url = reverse_lazy("horizon:iot:boards:create")
    success_url = reverse_lazy('horizon:iot:boards:index')
    page_title = _("Create Board")


class UpdateView(forms.ModalFormView):
    template_name = 'iot/boards/update.html'
    modal_header = _("Update Board")
    form_id = "update_board_form"
    form_class = project_forms.UpdateBoardForm
    submit_label = _("Update Board")
    submit_url = "horizon:iot:boards:update"
    success_url = reverse_lazy('horizon:iot:boards:index')
    page_title = _("Update Board")

    @memoized.memoized_method
    def get_object(self):
        try:
            return iotronic.board_get(self.request, self.kwargs['board_id'],
                                      None)
        except Exception:
            redirect = reverse("horizon:iot:boards:index")
            exceptions.handle(self.request,
                              _('Unable to update board.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        board = self.get_object()

        # LOG.debug("MELO BOARD INFO: %s", board)
        location = board.location[0]

        return {'uuid': board.uuid,
                'name': board.name,
                'mobile': board.mobile,
                'owner': board.owner,
                'latitude': location["latitude"],
                'longitude': location["longitude"],
                'altitude': location["altitude"]}


class RemovePluginsView(forms.ModalFormView):
    template_name = 'iot/boards/removeplugins.html'
    modal_header = _("Remove Plugins from board")
    form_id = "remove_boardplugins_form"
    form_class = project_forms.RemovePluginsForm
    submit_label = _("Remove Plugins from board")
    # submit_url = reverse_lazy("horizon:iot:boards:removeplugins")
    submit_url = "horizon:iot:boards:removeplugins"
    success_url = reverse_lazy('horizon:iot:boards:index')
    page_title = _("Remove Plugins from board")

    @memoized.memoized_method
    def get_object(self):
        try:
            return iotronic.board_get(self.request, self.kwargs['board_id'],
                                      None)
        except Exception:
            redirect = reverse("horizon:iot:boards:index")
            exceptions.handle(self.request,
                              _('Unable to remove plugin.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(RemovePluginsView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        board = self.get_object()

        # Populate plugins
        # TO BE DONE.....filter by available on this board!!!
        # plugins = iotronic.plugin_list(self.request, None, None)
        plugins = iotronic.plugins_on_board(self.request, board.uuid)

        plugins.sort(key=lambda b: b.name)

        plugin_list = []
        for plugin in plugins:
            plugin_list.append((plugin.uuid, _(plugin.name)))

        return {'uuid': board.uuid,
                'name': board.name,
                'plugin_list': plugin_list}


class DetailView(tabs.TabView):
    # FROM
    """
    tab_group_class = project_tabs.InstanceDetailTabs
    template_name = 'horizon/common/_detail.html'
    redirect_url = 'horizon:project:instances:index'
    page_title = "{{ instance.name|default:instance.id }}"
    image_url = 'horizon:project:images:images:detail'
    volume_url = 'horizon:project:volumes:volumes:detail'
    """
    # TO
    tab_group_class = project_tabs.BoardDetailTabs
    template_name = 'horizon/common/_detail.html'
    page_title = "{{ board.name|default:board.uuid }}"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        # FROM
        """
        instance = self.get_data()
        if instance.image:
            instance.image_url = reverse(self.image_url,
                                         args=[instance.image['id']])
        instance.volume_url = self.volume_url
        context["instance"] = instance
        context["url"] = reverse(self.redirect_url)
        context["actions"] = self._get_actions(instance)
        """
        # TO
        board = self.get_data()
        context["board"] = board
        context["url"] = reverse(self.redirect_url)
        context["actions"] = self._get_actions(board)

        return context

    # FROM
    """
    def _get_actions(self, instance):
        table = project_tables.InstancesTable(self.request)
        return table.render_row_actions(instance)
    """
    # TO
    def _get_actions(self, board):
        table = project_tables.BoardsTable(self.request)
        return table.render_row_actions(board)

    # FROM
    """
    @memoized.memoized_method
    def get_data(self):
        instance_id = self.kwargs['instance_id']

        try:
            instance = api.nova.server_get(self.request, instance_id)
        except Exception:
            redirect = reverse(self.redirect_url)
            exceptions.handle(self.request,
                              _('Unable to retrieve details for '
                                'instance "%s".') % instance_id,
                              redirect=redirect)
            # Not all exception types handled above will result in a redirect.
            # Need to raise here just in case.
            raise exceptions.Http302(redirect)

        choices = project_tables.STATUS_DISPLAY_CHOICES
        instance.status_label = (
            filters.get_display_label(choices, instance.status))

        try:
            instance.volumes = api.nova.instance_volumes_list(self.request,
                                                              instance_id)
            # Sort by device name
            instance.volumes.sort(key=lambda vol: vol.device)
        except Exception:
            msg = _('Unable to retrieve volume list for instance '
                    '"%(name)s" (%(id)s).') % {'name': instance.name,
                                               'id': instance_id}
            exceptions.handle(self.request, msg, ignore=True)

        try:
            instance.full_flavor = api.nova.flavor_get(
                self.request, instance.flavor["id"])
        except Exception:
            msg = _('Unable to retrieve flavor information for instance '
                    '"%(name)s" (%(id)s).') % {'name': instance.name,
                                               'id': instance_id}
            exceptions.handle(self.request, msg, ignore=True)

        try:
            instance.security_groups = api.network.server_security_groups(
                self.request, instance_id)
        except Exception:
            msg = _('Unable to retrieve security groups for instance '
                    '"%(name)s" (%(id)s).') % {'name': instance.name,
                                               'id': instance_id}
            exceptions.handle(self.request, msg, ignore=True)

        try:
            api.network.servers_update_addresses(self.request, [instance])
        except Exception:
            msg = _('Unable to retrieve IP addresses from Neutron for '
                    'instance "%(name)s" (%(id)s).') % {'name': instance.name,
                                                        'id': instance_id}
            exceptions.handle(self.request, msg, ignore=True)

        return instance
    """

    # TO
    @memoized.memoized_method
    def get_data(self):
        board_id = self.kwargs['board_id']
        try:
            board = iotronic.board_get(self.request, board_id, None)
        except Exception:
            msg = ('Unable to retrieve board %s information') % {'name':
                                                                 board.name}
            exceptions.handle(self.request, msg, ignore=True)
        return board

    # FROM
    """
    def get_tabs(self, request, *args, **kwargs):
        instance = self.get_data()
        return self.tab_group_class(request, instance=instance, **kwargs)
    """

    # TO
    def get_tabs(self, request, *args, **kwargs):
        board = self.get_data()
        return self.tab_group_class(request, board=board, **kwargs)


class BoardDetailView(DetailView):
    redirect_url = 'horizon:iot:boards:index'

    def _get_actions(self, board):
        table = project_tables.BoardsTable(self.request)
        return table.render_row_actions(board)
