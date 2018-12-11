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


class ExposeWebserviceForm(forms.SelfHandlingForm):

    uuid = forms.CharField(label=_("Board ID"), widget=forms.HiddenInput)

    name = forms.CharField(
        label=_('Board Name'),
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    zone = forms.CharField(label=_("Zone"),
                           widget=forms.TextInput(attrs={'readonly':
                                                         'readonly'}))

    ws_name = forms.CharField(label=_("Web Service Name"))

    port = forms.IntegerField(
        label=_("Port"),
        help_text=_("The local port used by the service")
    )

    secure = forms.BooleanField(label=_("Secure"), initial=True)

    def __init__(self, *args, **kwargs):
        super(ExposeWebserviceForm, self).__init__(*args, **kwargs)

    def handle(self, request, data):
        try:
            iotronic.webservice_expose(request, data["uuid"],
                                       data["ws_name"], data["port"],
                                       data["secure"])

            messages.success(request, _("Web Service " + str(data["name"]) +
                                        " exposed successfully on port " +
                                        str(data["port"]) + "."))
            return True

        except Exception:
            exceptions.handle(request, _('Unable to expose web service.'))


class UnexposeWebserviceForm(forms.SelfHandlingForm):

    uuid = forms.CharField(label=_("Board ID"), widget=forms.HiddenInput)

    name = forms.CharField(
        label=_('Board Name'),
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    ws_onboard = forms.MultipleChoiceField(
        label=_("Web Services on board"),
        widget=forms.SelectMultiple(
            attrs={'class': 'switchable',
                   'data-slug': 'slug-select-webservices'}),
        help_text=_("Select a webservice from the list")
    )

    def __init__(self, *args, **kwargs):

        super(UnexposeWebserviceForm, self).__init__(*args, **kwargs)
        self.fields["ws_onboard"].choices = kwargs["initial"]["ws_onboard"]

    def handle(self, request, data):

        counter = 0
        for ws in data["ws_onboard"]:
            try:
                iotronic.webservice_unexpose(request, ws)

                message_text = "Web Service(s) unexposed successfully."
                messages.success(request, _(message_text))

                if counter != len(data["ws_onboard"]) - 1:
                    counter += 1
                else:
                    return True

            except Exception:
                message_text = "Unable to unexpose web service."
                exceptions.handle(request, _(message_text))
