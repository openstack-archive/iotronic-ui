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

# from openstack_dashboard.api import iotronic
from openstack_dashboard import api
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

        # Admin
        if policy.check((("iot", "iot:list_all_boards"),), self.request):
            try:
                boards = api.iotronic.board_list(self.request, None, None)

            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve boards list.'))

        # Admin_iot_project
        elif policy.check((("iot", "iot:list_project_boards"),), self.request):
            try:
                boards = api.iotronic.board_list(self.request, None, None)

            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve user boards list.'))

        # Other users
        else:
            try:
                boards = api.iotronic.board_list(self.request, None, None)

            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve user boards list.'))

        for board in boards:
            board_services = api.iotronic.services_on_board(self.request,
                                                            board.uuid,
                                                            True)

            # TO BE REMOVED
            # We are filtering the services that starts with "webservice"
            # ------------------------------------------------------------
            filter_ws = []
            for service in board_services:
                if ((service["name"] != "webservice") and 
                   (service["name"] != "webservice_ssl")):
                    filter_ws.append(service)

            board_services = filter_ws
            # ------------------------------------------------------------

            # board.__dict__.update(dict(services=board_services))
            board._info.update(dict(services=board_services))

            if board.fleet != None:            
                fleet_info = api.iotronic.fleet_get(self.request,
                                                    board.fleet,
                                                    None)

                board.fleet_name = fleet_info.name
            else:
                board.fleet_name = None

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
            return api.iotronic.board_get(self.request,
                                          self.kwargs['board_id'],
                                          None)
        except Exception:
            redirect = reverse("horizon:iot:boards:index")
            exceptions.handle(self.request,
                              _('Unable to get board information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        board = self.get_object()
        location = board.location[0]

        return {'uuid': board.uuid,
                'name': board.name,
                'mobile': board.mobile,
                'owner': board.owner,
                'fleet_id': board.fleet,
                'latitude': location["latitude"],
                'longitude': location["longitude"],
                'altitude': location["altitude"]}


class EnableServiceView(forms.ModalFormView):
    template_name = 'iot/boards/enableservice.html'
    modal_header = _("Enable Service(s)")
    form_id = "service_enable_form"
    form_class = project_forms.EnableServiceForm
    submit_label = _("Enable")
    # submit_url = reverse_lazy("horizon:iot:boards:enableservice")
    submit_url = "horizon:iot:boards:enableservice"
    success_url = reverse_lazy('horizon:iot:boards:index')
    page_title = _("Action")

    @memoized.memoized_method
    def get_object(self):
        try:
            return api.iotronic.board_get(self.request,
                                          self.kwargs['board_id'],
                                          None)

        except Exception:
            redirect = reverse("horizon:iot:boards:index")
            exceptions.handle(self.request,
                              _('Unable to get board information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(EnableServiceView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        board = self.get_object()

        # Populate available services
        cloud_services = api.iotronic.service_list(self.request, None)
        board_services = api.iotronic.services_on_board(self.request,
                                                        board.uuid,
                                                        True)

        service_list = []

        for cloud_service in cloud_services:

            if len(board_services) == 0:
                service_list.append((cloud_service._info["uuid"],
                                    _(cloud_service._info["name"])))
            else:
                counter = 0
                for board_service in board_services:
                    if board_service["uuid"] == cloud_service._info["uuid"]:
                        break
                    elif counter != len(board_services) - 1:
                        counter += 1
                    else:
                        service_list.append((cloud_service._info["uuid"],
                                            _(cloud_service._info["name"])))

        return {'uuid': board.uuid,
                'name': board.name,
                'service_list': service_list}


"""
class DisableServiceView(forms.ModalFormView):
    template_name = 'iot/boards/disableservice.html'
    modal_header = _("Disable Service(s)")
    form_id = "service_disable_form"
    form_class = project_forms.DisableServiceForm
    submit_label = _("Disable")
    # submit_url = reverse_lazy("horizon:iot:boards:disableservice")
    submit_url = "horizon:iot:boards:disableservice"
    success_url = reverse_lazy('horizon:iot:boards:index')
    page_title = _("Action")

    @memoized.memoized_method
    def get_object(self):
        try:
            return api.iotronic.board_get(self.request,
                                          self.kwargs['board_id'],
                                          None)

        except Exception:
            redirect = reverse("horizon:iot:boards:index")
            exceptions.handle(self.request,
                              _('Unable to get board information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(DisableServiceView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        board = self.get_object()

        # Populate available services
        cloud_services = api.iotronic.service_list(self.request, None)
        board_services = api.iotronic.services_on_board(self.request,
                                                        board.uuid,
                                                        True)

        service_list = []


        # BEFORE filtering necessity
        # for cloud_service in cloud_services:
        #     for board_service in board_services:
        #         if board_service["uuid"] == cloud_service._info["uuid"]:
        #             service_list.append((cloud_service._info["uuid"],
        #                                 _(cloud_service._info["name"])))

        # AFTER filtering necessity
        # We are filtering the services that starts with "webservice"
        # ------------------------------------------------------------

        for cloud_service in cloud_services:
            for board_service in board_services:
                if ((board_service["uuid"] == cloud_service._info["uuid"]) and
                   ((board_service["name"] != "webservice") and
                   (board_service["name"] != "webservice_ssl"))): 
                    service_list.append((cloud_service._info["uuid"],
                                        _(cloud_service._info["name"])))
        # ------------------------------------------------------------

        return {'uuid': board.uuid,
                'name': board.name,
                'service_list': service_list}
"""


class AttachPortView(forms.ModalFormView):
    template_name = 'iot/boards/attachport.html'
    modal_header = _("Attach")
    form_id = "attach_boardport_form"
    form_class = project_forms.AttachPortForm
    submit_label = _("Attach")
    # submit_url = reverse_lazy("horizon:iot:boards:attachport")
    submit_url = "horizon:iot:boards:attachport"
    success_url = reverse_lazy('horizon:iot:boards:index')
    page_title = _("Attach port")

    @memoized.memoized_method
    def get_object(self):
        try:
            return api.iotronic.board_get(self.request,
                                          self.kwargs['board_id'],
                                          None)
        except Exception:
            redirect = reverse("horizon:iot:boards:index")
            exceptions.handle(self.request,
                              _('Unable to get board information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(AttachPortView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        board = self.get_object()

        # Populate networks
        networks = api.neutron.network_list(self.request)
        net_choices = []

        for net in networks:
            for subnet in net["subnets"]:
                net_choices.append((net["id"] + ':' + subnet["id"],
                                   _(net["name"] + ':' + subnet["name"])))

        return {'uuid': board.uuid,
                'name': board.name,
                'networks_list': net_choices}


class DetachPortView(forms.ModalFormView):
    template_name = 'iot/boards/detachport.html'
    modal_header = _("Detach")
    form_id = "detach_boardport_form"
    form_class = project_forms.DetachPortForm
    submit_label = _("Detach")
    # submit_url = reverse_lazy("horizon:iot:boards:detachport")
    submit_url = "horizon:iot:boards:detachport"
    success_url = reverse_lazy('horizon:iot:boards:index')
    page_title = _("Detach port")

    @memoized.memoized_method
    def get_object(self):
        try:
            return api.iotronic.board_get(self.request,
                                          self.kwargs['board_id'],
                                          None)
        except Exception:
            redirect = reverse("horizon:iot:boards:index")
            exceptions.handle(self.request,
                              _('Unable to get board information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(DetachPortView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        board = self.get_object()

        ports = api.iotronic.port_list(self.request, board.uuid)

        # TO BE REMOVED (change it once the port_list per board is
        # completed and tested !
        # ################################################################
        # LOG.debug("PORTS: %s", ports)

        filtered_ports = []
        for port in ports:
            if port._info["board_uuid"] == board.uuid:
                filtered_ports.append((port._info["uuid"],
                                      _(port._info["ip"])))

        ports = filtered_ports
        # ################################################################

        # Populate board ports
        return {'uuid': board.uuid,
                'name': board.name,
                'ports': ports}


class EnableWebServiceView(forms.ModalFormView):
    template_name = 'iot/boards/enablewebservice.html'
    modal_header = _("Enable Web Service(s)")
    form_id = "webservice_enable_form"
    form_class = project_forms.EnableWebServiceForm
    submit_label = _("Enable")
    # submit_url = reverse_lazy("horizon:iot:boards:enablewebservice")
    submit_url = "horizon:iot:boards:enablewebservice"
    success_url = reverse_lazy('horizon:iot:boards:index')
    page_title = _("Enable")

    @memoized.memoized_method
    def get_object(self):
        try:
            return api.iotronic.board_get(self.request,
                                          self.kwargs['board_id'],
                                          None)

        except Exception:
            redirect = reverse("horizon:iot:boards:index")
            exceptions.handle(self.request,
                              _('Unable to get board information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(EnableWebServiceView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        board = self.get_object()

        return {'uuid': board.uuid,
                'name': board.name}


class DisableWebServiceView(forms.ModalFormView):
    template_name = 'iot/boards/disablewebservice.html'
    modal_header = _("Disable Web Service(s)")
    form_id = "webservice_disable_form"
    form_class = project_forms.DisableWebServiceForm
    submit_label = _("Disable")
    # submit_url = reverse_lazy("horizon:iot:boards:disablewebservice")
    submit_url = "horizon:iot:boards:disablewebservice"
    success_url = reverse_lazy('horizon:iot:boards:index')
    page_title = _("Disable")

    @memoized.memoized_method
    def get_object(self):
        try:
            return api.iotronic.board_get(self.request,
                                          self.kwargs['board_id'],
                                          None)

        except Exception:
            redirect = reverse("horizon:iot:boards:index")
            exceptions.handle(self.request,
                              _('Unable to get board information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(DisableWebServiceView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        board = self.get_object()

        return {'uuid': board.uuid,
                'name': board.name}


class RemovePluginsView(forms.ModalFormView):
    template_name = 'iot/boards/removeplugins.html'
    modal_header = _("Remove Plugins from board")
    form_id = "remove_boardplugins_form"
    form_class = project_forms.RemovePluginsForm
    submit_label = _("Remove")
    # submit_url = reverse_lazy("horizon:iot:boards:removeplugins")
    submit_url = "horizon:iot:boards:removeplugins"
    success_url = reverse_lazy('horizon:iot:boards:index')
    page_title = _("Remove Plugins from board")

    @memoized.memoized_method
    def get_object(self):
        try:
            return api.iotronic.board_get(self.request,
                                          self.kwargs['board_id'],
                                          None)
        except Exception:
            redirect = reverse("horizon:iot:boards:index")
            exceptions.handle(self.request,
                              _('Unable to get board information.'),
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
        # plugins = api.iotronic.plugin_list(self.request, None, None)
        plugins = api.iotronic.plugins_on_board(self.request, board.uuid)

        plugins.sort(key=lambda b: b["name"])

        plugin_list = []
        for plugin in plugins:
            plugin_list.append((plugin["id"], _(plugin["name"])))

        return {'uuid': board.uuid,
                'name': board.name,
                'plugin_list': plugin_list}


class RemoveServicesView(forms.ModalFormView):
    template_name = 'iot/boards/removeservices.html'
    modal_header = _("Remove Services from board")
    form_id = "remove_boardservices_form"
    form_class = project_forms.RemoveServicesForm
    submit_label = _("Remove")
    # submit_url = reverse_lazy("horizon:iot:boards:removeservices")
    submit_url = "horizon:iot:boards:removeservices"
    success_url = reverse_lazy('horizon:iot:boards:index')
    page_title = _("Remove Services from board")

    @memoized.memoized_method
    def get_object(self):
        try:
            return api.iotronic.board_get(self.request,
                                          self.kwargs['board_id'],
                                          None)
        except Exception:
            redirect = reverse("horizon:iot:boards:index")
            exceptions.handle(self.request,
                              _('Unable to get board information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(RemoveServicesView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        board = self.get_object()

        # Populate services
        services = api.iotronic.services_on_board(self.request,
                                                  board.uuid,
                                                  True)
        services.sort(key=lambda b: b["name"])

        service_list = []
        for service in services:
            # service_list.append((service["uuid"], _(service["name"])))

            # TO BE REMOVED
            # ###########################################################
            # We are filtering the services that starts with "webservice"
            if ((service["name"] != "webservice") and
               (service["name"] != "webservice_ssl")):
                service_list.append((service["uuid"], _(service["name"])))
            # ###########################################################

        return {'uuid': board.uuid,
                'name': board.name,
                'service_list': service_list}


class DetailView(tabs.TabView):
    tab_group_class = project_tabs.BoardDetailTabs
    template_name = 'horizon/common/_detail.html'
    page_title = "{{ board.name|default:board.uuid }}"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        board = self.get_data()
        context["board"] = board
        context["url"] = reverse(self.redirect_url)
        context["actions"] = self._get_actions(board)

        return context

    def _get_actions(self, board):
        table = project_tables.BoardsTable(self.request)
        return table.render_row_actions(board)

    @memoized.memoized_method
    def get_data(self):

        board = []

        board_id = self.kwargs['board_id']
        try:

            board_ports = []

            board = api.iotronic.board_get(self.request, board_id, None)

            # FIX this problem with the new APIs
            # (remove the "if" clause with a better approach)
            # #################################################################
            ports = api.iotronic.port_list(self.request, board_id)

            for port in ports:
                if port._info["board_uuid"] == board_id:
                    board_ports.append(port._info)
            board._info.update(dict(ports=board_ports))
            # #################################################################

            board_services = api.iotronic.services_on_board(self.request,
                                                            board_id, True)
            board._info.update(dict(services=board_services))

            board_plugins = api.iotronic.plugins_on_board(self.request,
                                                          board_id)
            board._info.update(dict(plugins=board_plugins))

            board_webservices = api.iotronic.webservices_on_board(self.request,
                                                                  board_id)
            board._info.update(dict(webservices=board_webservices))

            # Adding fleet name
            if board.fleet != None:
                fleet_info = api.iotronic.fleet_get(self.request,
                                                    board.fleet,
                                                    None)

                board.fleet_name = fleet_info.name
            else:
                board.fleet_name = None

            # LOG.debug("BOARD: %s\n\n%s", board, board._info)

        except Exception:
            msg = ('Unable to retrieve board %s information') % {'name':
                                                                 board.name}
            exceptions.handle(self.request, msg, ignore=True)
        return board

    def get_tabs(self, request, *args, **kwargs):
        board = self.get_data()
        return self.tab_group_class(request, board=board, **kwargs)


class BoardDetailView(DetailView):
    redirect_url = 'horizon:iot:boards:index'

    def _get_actions(self, board):
        table = project_tables.BoardsTable(self.request)
        return table.render_row_actions(board)
