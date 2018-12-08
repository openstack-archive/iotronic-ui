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


class CreateFleetForm(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Fleet Name"))

    description = forms.CharField(
        label=_("Description"),
        widget=forms.Textarea(
            attrs={'class': 'switchable', 'data-slug': 'slug-description'})
    )

    def handle(self, request, data):
        try:
            iotronic.fleet_create(request, data["name"],
                                    data["description"])

            messages.success(request, _("Fleet " + str(data["name"]) +
                                        " created successfully."))
            return True

        except Exception:
            exceptions.handle(request, _('Unable to create fleet.'))


class UpdateFleetForm(forms.SelfHandlingForm):
    uuid = forms.CharField(label=_("Fleet ID"), widget=forms.HiddenInput)
    name = forms.CharField(label=_("Fleet Name"))
    description = forms.CharField(
        label=_("Description"),
        widget=forms.Textarea(
            attrs={'class': 'switchable', 'data-slug': 'slug-description'})
    )

    def __init__(self, *args, **kwargs):

        super(UpdateFleetForm, self).__init__(*args, **kwargs)

        # Admin
        if policy.check((("iot", "iot:update_fleets"),), self.request):
            # LOG.debug("ADMIN")
            pass

        # Manager or Admin of the iot project
        elif (policy.check((("iot", "iot_manager"),), self.request) or
              policy.check((("iot", "iot_admin"),), self.request)):
            # LOG.debug("NO-edit IOT ADMIN")
            pass

        # Other users
        else:
            if self.request.user.id != kwargs["initial"]["owner"]:
                # LOG.debug("IMMUTABLE FIELDS")
                self.fields["name"].widget.attrs = {'readonly': 'readonly'}
                self.fields["description"].widget.attrs = {'readonly': 'readonly'}

    def handle(self, request, data):
        try:
            iotronic.fleet_update(request, data["uuid"],
                                    {"name": data["name"],
                                     "description": data["description"]})

            messages.success(request, _("Fleet updated successfully."))
            return True

        except Exception:
            exceptions.handle(request, _('Unable to update fleet.'))
