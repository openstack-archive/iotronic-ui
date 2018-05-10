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

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard.api import iotronic
from openstack_dashboard import policy

LOG = logging.getLogger(__name__)


class CreateServiceForm(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Service Name"))
    port = forms.IntegerField(
        label=_("Port"),
        help_text=_("Service port")
    )

    protocol = forms.ChoiceField(
        label=_("Protocol"),
        choices=[('TCP', _('TCP')), ('UDP', _('UDP'))],
        widget=forms.Select(
            attrs={'class': 'switchable', 'data-slug': 'slug-protocol'},
        )
    )

    def handle(self, request, data):
        try:
            # LOG.error("DATA: %s", data)
            service = iotronic.service_create(request, data["name"],
                                          data["port"], data["protocol"])
            messages.success(request, _("Service created successfully."))

            return service
        except Exception:
            exceptions.handle(request, _('Unable to create service.'))


class UpdateBoardForm(forms.SelfHandlingForm):
    uuid = forms.CharField(label=_("Service ID"), widget=forms.HiddenInput)
    name = forms.CharField(label=_("Service Name"))
    port = forms.IntegerField(label=_("Port"))
    protocol = forms.ChoiceField(
        label=_("Protocol"),
        choices=[('TCP', _('TCP')), ('UDP', _('UDP'))],
        widget=forms.Select(
            attrs={'class': 'switchable', 'data-slug': 'slug-protocol'},
        )
    )

    def __init__(self, *args, **kwargs):

        super(UpdateBoardForm, self).__init__(*args, **kwargs)

        # Admin
        if policy.check((("iot", "iot:update_services"),), self.request):
            # LOG.debug("MELO ADMIN")
            pass

        # Manager or Admin of the iot project
        elif (policy.check((("iot", "iot_manager"),), self.request) or
              policy.check((("iot", "iot_admin"),), self.request)):
            # LOG.debug("MELO NO-edit IOT ADMIN")
            pass

        # Other users
        else:
            if self.request.user.id != kwargs["initial"]["owner"]:
                # LOG.debug("MELO IMMUTABLE FIELDS")
                self.fields["name"].widget.attrs = {'readonly': 'readonly'}
                self.fields["port"].widget.attrs = {'readonly': 'readonly'}
                self.fields["protocol"].widget.attrs = {'readonly': 'readonly'}

    def handle(self, request, data):
        try:
            iotronic.service_update(request, data["uuid"],
                                  {"name": data["name"],
                                   "port": data["port"],
                                   "protocol": data["protocol"]})

            messages.success(request, _("Service updated successfully."))
            return True
        except Exception:
            exceptions.handle(request, _('Unable to update service.'))


class ServiceActionForm(forms.SelfHandlingForm):

    uuid = forms.CharField(label=_("Plugin ID"), widget=forms.HiddenInput)

    name = forms.CharField(
        label=_('Service Name'),
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    board_list = forms.MultipleChoiceField(
        label=_("Boards List"),
        widget=forms.SelectMultiple(
            attrs={'class': 'switchable', 'data-slug': 'slug-select-boards'}),
        help_text=_("Select boards in this pool")
    )

    action = forms.ChoiceField(
        label=_("Action"),
        choices=[('ServiceEnable', _('Enable')), ('ServiceDisable', _('Disable')), ('ServiceRestore', _('Restore'))],
        widget=forms.Select(
            attrs={'class': 'switchable', 'data-slug': 'slug-action'},
        )
    )

    def __init__(self, *args, **kwargs):

        super(ServiceActionForm, self).__init__(*args, **kwargs)
        # input=kwargs.get('initial',{})

        boardslist_length = len(kwargs["initial"]["board_list"])

        self.fields["board_list"].choices = kwargs["initial"]["board_list"]
        # self.fields["board_list"].max_length = boardslist_length

    def handle(self, request, data):

        counter = 0

        for board in data["board_list"]:
            for key, value in self.fields["board_list"].choices:
                if key == board:

                    try:
                        action = None
                        action = iotronic.service_action(request, key,
                                                        data["uuid"],
                                                        data["action"])

                        message_text = "Action executed successfully on " \
                                       "board " + str(value) + "."
                        messages.success(request, _(message_text))

                        if counter != len(data["board_list"]) - 1:
                            counter += 1
                        else:
                            return action
                    except Exception:
                        message_text = "Unable to execute action on board " \
                                       + str(value) + "."
                        exceptions.handle(request, _(message_text))

                    break


class RemoveServicesForm(forms.SelfHandlingForm):

    uuid = forms.CharField(label=_("Service ID"), widget=forms.HiddenInput)

    name = forms.CharField(
        label=_('Service Name'),
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    port = forms.IntegerField(
        label=_("Port"),
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    protocol = forms.ChoiceField(
        label=_("Protocol"),
        choices=[('TCP', _('TCP')), ('UDP', _('UDP'))],
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    def __init__(self, *args, **kwargs):

        super(RemoveServicesForm, self).__init__(*args, **kwargs)
        # input=kwargs.get('initial',{})


    def handle(self, request, data):

        try:
            message_text = "Service "+str(data["name"])+" deleted successfully."

            iotronic.service_delete(request, data["uuid"])
            messages.success(request, _(message_text))
            return True
        except Exception:
            message_text = "Unable to delete service "+str(data["name"])+"."
            exceptions.handle(request, _(message_text))
