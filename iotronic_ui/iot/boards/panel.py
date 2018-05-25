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

from django.utils.translation import ugettext_lazy as _

import horizon

# from openstack_dashboard.api import keystone
from iotronic_ui.iot import dashboard


class Boards(horizon.Panel):
    name = _("Boards")
    slug = "boards"
    permissions = ('openstack.services.iot', )
    # policy_rules = (("iot", "iot:list_all_boards"),)

    # TO BE REMOVED
    """
    def can_access(self, context):
        if keystone.is_multi_domain_enabled() \
                and not keystone.is_domain_admin(context['request']):
            return False
        return super(Roles, self).can_access(context)
    """


dashboard.Iot.register(Boards)
