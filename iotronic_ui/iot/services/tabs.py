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

# from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import tabs

LOG = logging.getLogger(__name__)


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("iot/services/_detail_overview.html")

    def get_context_data(self, request):
        # coordinates = self.tab_group.kwargs['board'].__dict__["location"][0]
        # LOG.debug('IOT INFO: %s', coordinates)

        return {"service": self.tab_group.kwargs['service'],
                "is_superuser": request.user.is_superuser}


class ServiceDetailTabs(tabs.TabGroup):
    slug = "service_details"
    # tabs = (OverviewTab, LogTab, ConsoleTab, AuditTab)
    tabs = (OverviewTab,)
    sticky = True
