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


class CreatePluginLink(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Plugin")
    url = "horizon:iot:plugins:create"
    classes = ("ajax-modal",)
    icon = "plus"
    # policy_rules = (("iot", "iot:create_plugin"),)


class EditPluginLink(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit")
    url = "horizon:iot:plugins:update"
    classes = ("ajax-modal",)
    icon = "pencil"
    # policy_rules = (("iot", "iot:update_plugin"),)

    """
    def allowed(self, request, plugin):
        # LOG.debug("ALLOWED: %s %s %s", self, request, plugin)
        # LOG.debug("user: %s", request.user.id)

        return True
    """


class InjectPluginLink(tables.LinkAction):
    name = "inject"
    verbose_name = _("Inject Plugin")
    url = "horizon:iot:plugins:inject"
    classes = ("ajax-modal",)
    icon = "plus"
    # policy_rules = (("iot", "iot:inject_plugin"),)


class StartPluginLink(tables.LinkAction):
    name = "start"
    verbose_name = _("Start Plugin")
    url = "horizon:iot:plugins:start"
    classes = ("ajax-modal",)
    icon = "plus"
    # policy_rules = (("iot", "iot:start_plugin"),)


class StopPluginLink(tables.LinkAction):
    name = "stop"
    verbose_name = _("Stop Plugin")
    url = "horizon:iot:plugins:stop"
    classes = ("ajax-modal",)
    icon = "plus"
    # policy_rules = (("iot", "iot:stop_plugin"),)


class CallPluginLink(tables.LinkAction):
    name = "call"
    verbose_name = _("Call Plugin")
    url = "horizon:iot:plugins:call"
    classes = ("ajax-modal",)
    icon = "plus"
    # policy_rules = (("iot", "iot:call_plugin"),)


class RemovePluginLink(tables.LinkAction):
    name = "remove"
    verbose_name = _("Remove Plugin from board(s)")
    url = "horizon:iot:plugins:remove"
    classes = ("ajax-modal",)
    icon = "plus"
    # policy_rules = (("iot", "iot:remove_plugin"),)


class DeletePluginsAction(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Plugin",
            u"Delete Plugins",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Plugin",
            u"Deleted Plugins",
            count
        )
    # policy_rules = (("iot", "iot:delete_plugin"),)

    """
    def allowed(self, request, role):
        return api.keystone.keystone_can_edit_role()
    """

    def delete(self, request, plugin_id):
        api.iotronic.plugin_delete(request, plugin_id)


class PluginFilterAction(tables.FilterAction):

    def filter(self, table, plugins, filter_string):
        """Naive case-insensitive search."""
        q = filter_string.lower()
        return [plugin for plugin in plugins
                if q in plugin.name.lower()]


class PluginsTable(tables.DataTable):
    name = tables.WrappingColumn('name', link="horizon:iot:plugins:detail",
                                 verbose_name=_('Plugin Name'))
    uuid = tables.Column('uuid', verbose_name=_('Plugin ID'))
    owner = tables.Column('owner', verbose_name=_('Owner'))
    public = tables.Column('public', verbose_name=_('Public'))
    callable = tables.Column('callable', verbose_name=_('Callable'))

    # Overriding get_object_id method because in IoT service the "id" is
    # identified by the field UUID
    def get_object_id(self, datum):
        # LOG.debug("datum %s", datum)
        return datum.uuid

    # Overriding get_row_actions method because we need to discriminate
    # between Sync and Async plugins
    def get_row_actions(self, datum):
        actions = super(PluginsTable, self).get_row_actions(datum)
        # LOG.debug("ACTIONS: %s %s", actions[0].name, datum.name)

        selected_row_actions = []

        common_actions = ["edit", "inject", "remove", "delete"]

        for action in actions:
            if action.name in common_actions:
                selected_row_actions.append(action)

            elif datum.callable == True and action.name == "call":
                selected_row_actions.append(action)

            elif datum.callable == False and action.name != "call":
                selected_row_actions.append(action)

        return selected_row_actions

    class Meta(object):
        name = "plugins"
        verbose_name = _("plugins")

        row_actions = (EditPluginLink, InjectPluginLink, StartPluginLink,
                       StopPluginLink, CallPluginLink, RemovePluginLink,
                       DeletePluginsAction,)
        table_actions = (PluginFilterAction, CreatePluginLink,
                         DeletePluginsAction)
