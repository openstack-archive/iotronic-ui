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
from django.utils.translation import ungettext_lazy

from horizon import tables

from openstack_dashboard import api

LOG = logging.getLogger(__name__)


class CreateFleetLink(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Fleet")
    url = "horizon:iot:fleets:create"
    classes = ("ajax-modal",)
    icon = "plus"
    # policy_rules = (("iot", "iot:create_fleet"),)


class EditFleetLink(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit")
    url = "horizon:iot:fleets:update"
    classes = ("ajax-modal",)
    icon = "pencil"
    # policy_rules = (("iot", "iot:update_fleet"),)


class DeleteFleetsAction(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Fleet",
            u"Delete Fleets",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Fleet",
            u"Deleted Fleets",
            count
        )
    # policy_rules = (("iot", "iot:delete_fleet"),)

    def delete(self, request, fleet_id):
        api.iotronic.fleet_delete(request, fleet_id)


class FleetFilterAction(tables.FilterAction):

    def filter(self, table, fleets, filter_string):
        # Naive case-insensitive search.
        q = filter_string.lower()
        return [fleet for fleet in fleets
                if q in fleet.name.lower()]


class FleetsTable(tables.DataTable):
    name = tables.WrappingColumn('name', link="horizon:iot:fleets:detail",
                                 verbose_name=_('Fleet Name'))
    description = tables.Column('description', verbose_name=_('Description'))

    # Overriding get_object_id method because in IoT fleet the "id" is
    # identified by the field UUID
    def get_object_id(self, datum):
        return datum.uuid

    class Meta(object):
        name = "fleets"
        verbose_name = _("fleets")
        row_actions = (EditFleetLink, DeleteFleetsAction)
        table_actions = (FleetFilterAction, CreateFleetLink,
                         DeleteFleetsAction)
