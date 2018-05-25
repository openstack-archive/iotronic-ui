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

from iotronic_ui.iot.services import forms as project_forms
from iotronic_ui.iot.services import tables as project_tables
from iotronic_ui.iot.services import tabs as project_tabs


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = project_tables.ServicesTable
    template_name = 'iot/services/index.html'
    page_title = _("Services")

    def get_data(self):
        services = []

        # Admin
        if policy.check((("iot", "iot:list_all_services"),), self.request):
            try:
                services = iotronic.service_list(self.request, None)

            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve services list.'))

        # Admin_iot_project
        elif policy.check((("iot", "iot:list_project_services"),),
                          self.request):
            try:
                services = iotronic.service_list(self.request, None)

            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve user services list.'))

        # Other users
        else:
            try:
                services = iotronic.service_list(self.request, None)

            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve user services list.'))

        return services


class CreateView(forms.ModalFormView):
    template_name = 'iot/services/create.html'
    modal_header = _("Create Service")
    form_id = "create_service_form"
    form_class = project_forms.CreateServiceForm
    submit_label = _("Create Service")
    submit_url = reverse_lazy("horizon:iot:services:create")
    success_url = reverse_lazy('horizon:iot:services:index')
    page_title = _("Create Service")


class UpdateView(forms.ModalFormView):
    template_name = 'iot/services/update.html'
    modal_header = _("Update Service")
    form_id = "update_service_form"
    form_class = project_forms.UpdateServiceForm
    submit_label = _("Update Service")
    submit_url = "horizon:iot:services:update"
    success_url = reverse_lazy('horizon:iot:services:index')
    page_title = _("Update Service")

    @memoized.memoized_method
    def get_object(self):
        try:
            return iotronic.service_get(self.request,
                                        self.kwargs['service_id'],
                                        None)
        except Exception:
            redirect = reverse("horizon:iot:services:index")
            exceptions.handle(self.request,
                              _('Unable to get service information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        service = self.get_object()

        return {'uuid': service.uuid,
                'name': service.name,
                'port': service.port,
                'protocol': service.protocol}


class ActionView(forms.ModalFormView):
    template_name = 'iot/services/action.html'
    modal_header = _("Service Action")
    form_id = "service_action_form"
    form_class = project_forms.ServiceActionForm
    submit_label = _("Service Action")
    # submit_url = reverse_lazy("horizon:iot:services:action")
    submit_url = "horizon:iot:services:action"
    success_url = reverse_lazy('horizon:iot:services:index')
    page_title = _("Service Action")

    @memoized.memoized_method
    def get_object(self):
        try:
            return iotronic.service_get(self.request,
                                        self.kwargs['service_id'],
                                        None)
        except Exception:
            redirect = reverse("horizon:iot:services:index")
            exceptions.handle(self.request,
                              _('Unable to get service information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(ActionView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        service = self.get_object()

        # Populate boards
        boards = iotronic.board_list(self.request, "online", None, None)
        boards.sort(key=lambda b: b.name)

        board_list = []
        for board in boards:
            board_list.append((board.uuid, _(board.name)))

        return {'uuid': service.uuid,
                'name': service.name,
                'board_list': board_list}


class DetailView(tabs.TabView):
    tab_group_class = project_tabs.ServiceDetailTabs
    template_name = 'horizon/common/_detail.html'
    page_title = "{{ service.name|default:service.uuid }}"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        service = self.get_data()
        context["service"] = service
        context["url"] = reverse(self.redirect_url)
        context["actions"] = self._get_actions(service)

        return context

    def _get_actions(self, service):
        table = project_tables.ServicesTable(self.request)
        return table.render_row_actions(service)

    @memoized.memoized_method
    def get_data(self):
        service_id = self.kwargs['service_id']
        try:
            service = iotronic.service_get(self.request, service_id, None)
        except Exception:
            s = service.name
            msg = ('Unable to retrieve service %s information') % {'name': s}
            exceptions.handle(self.request, msg, ignore=True)
        return service

    def get_tabs(self, request, *args, **kwargs):
        service = self.get_data()
        return self.tab_group_class(request, service=service, **kwargs)


class ServiceDetailView(DetailView):
    redirect_url = 'horizon:iot:services:index'

    def _get_actions(self, service):
        table = project_tables.ServicesTable(self.request)
        return table.render_row_actions(service)
