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

# from collections import OrderedDict
# import threading

from iotronicclient import client as iotronic_client
# from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# from horizon import exceptions
from horizon.utils.memoized import memoized  # noqa

from openstack_dashboard.api import base
# from openstack_dashboard.api import keystone


# TESTING
import logging
LOG = logging.getLogger(__name__)


@memoized
def iotronicclient(request):
    """Initialization of Iotronic client."""

    endpoint = base.url_for(request, 'iot')
    # insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    # cacert = getattr(settings, 'OPENSTACK_SSL_CACERT', None)

    return iotronic_client.Client('1', endpoint, token=request.user.token.id)


# BOARD MANAGEMENT
def board_list(request, status=None, detail=None, project=None):
    """List boards."""
    return iotronicclient(request).board.list(status, detail, project)


def board_get(request, board_id, fields):
    """Get board info."""
    return iotronicclient(request).board.get(board_id, fields)


def board_create(request, code, mobile, location, type, name):
    """Create board."""
    params = {"code": code,
              "mobile": mobile,
              "location": location,
              "type": type,
              "name": name}
    iotronicclient(request).board.create(**params)


def board_update(request, board_id, patch):
    """Update board."""
    iotronicclient(request).board.update(board_id, patch)


def board_delete(request, board_id):
    """Delete board."""
    iotronicclient(request).board.delete(board_id)


# PLUGIN MANAGEMENT (Cloud Side)
def plugin_list(request, detail=None, project=None, with_public=False,
                all_plugins=False):
    """List plugins."""
    return iotronicclient(request).plugin.list(detail, project,
                                               with_public=with_public,
                                               all_plugins=all_plugins)


def plugin_get(request, plugin_id, fields):
    """Get plugin info."""
    plugin = iotronicclient(request).plugin.get(plugin_id, fields)
    return plugin


def plugin_create(request, name, public, callable, code, parameters):
    """Create plugin."""
    params = {"name": name,
              "public": public,
              "callable": callable,
              "code": code,
              "parameters": parameters}
    iotronicclient(request).plugin.create(**params)


def plugin_update(request, plugin_id, patch):
    """Update plugin."""
    iotronicclient(request).plugin.update(plugin_id, patch)


def plugin_delete(request, plugin_id):
    """Delete plugin."""
    return iotronicclient(request).plugin.delete(plugin_id)


# PLUGIN MANAGEMENT (Board Side)
def plugin_inject(request, board_id, plugin_id, onboot):
    """Inject plugin on board(s)."""
    return iotronicclient(request).plugin_injection.plugin_inject(board_id,
                                                                  plugin_id,
                                                                  onboot)


def plugin_action(request, board_id, plugin_id, action, params={}):
    """Start/Stop/Call actions on board(s)."""
    return iotronicclient(request).plugin_injection.plugin_action(
        board_id, plugin_id, action, params)


def plugin_remove(request, board_id, plugin_id):
    """Remove plugin from board."""
    iotronicclient(request).plugin_injection.plugin_remove(board_id,
                                                           plugin_id)


def plugins_on_board(request, board_id):
    """Plugins on board."""
    plugins = iotronicclient(request).plugin_injection.plugins_on_board(
        board_id)

    detailed_plugins = []
    # fields = {"name", "public", "callable"}
    fields = {"name"}
    for plugin in plugins:
        details = iotronicclient(request).plugin.get(plugin.plugin, fields)
        detailed_plugins.append({"name": details._info["name"],
                                 "id": plugin.plugin})

    return detailed_plugins


# SERVICE MANAGEMENT
def service_list(request, detail=None):
    """List services."""
    return iotronicclient(request).service.list(detail)


def service_get(request, service_id, fields):
    """Get service info."""
    return iotronicclient(request).service.get(service_id, fields)


def service_create(request, name, port, protocol):
    """Create service."""
    params = {"name": name,
              "port": port,
              "protocol": protocol}
    iotronicclient(request).service.create(**params)


def service_update(request, service_id, patch):
    """Update service."""
    iotronicclient(request).service.update(service_id, patch)


def service_delete(request, service_id):
    """Delete service."""
    iotronicclient(request).service.delete(service_id)


def services_on_board(request, board_id, detail=False):
    """List services on board."""
    services = iotronicclient(request).exposed_service.services_on_board(
        board_id)

    if detail:
        detailed_services = []
        fields = {"name", "port", "protocol"}

        for service in services:
            details = iotronicclient(request).service.get(
                service._info["service"], fields)

            detailed_services.append({"uuid": service._info["service"],
                                      "name": details._info["name"],
                                      "public_port":
                                          service._info["public_port"],
                                      "port": details._info["port"],
                                      "protocol": details._info["protocol"]})

        return detailed_services

    else:
        return services


def service_action(request, board_id, service_id, action):
    """Action on service."""
    return iotronicclient(request).exposed_service.service_action(board_id,
                                                                  service_id,
                                                                  action)


def restore_services(request, board_id):
    """Restore services."""
    return iotronicclient(request).exposed_service.restore_services(board_id)


# PORTS MANAGEMENT
def port_list(request, board_id):
    """Get ports attached to a board."""
    return iotronicclient(request).port.list()


def attach_port(request, board_id, network_id, subnet_id):
    """Attach port to a subnet for a board."""
    return iotronicclient(request).portonboard.attach_port(board_id,
                                                           network_id,
                                                           subnet_id)


def detach_port(request, board_id, port_id):
    """Detach port from the board."""
    iotronicclient(request).portonboard.detach_port(board_id, port_id)


# FLEETS MANAGEMENT
def fleet_list(request, detail=None):
    """Get fleets list."""
    return iotronicclient(request).fleet.list()


def fleet_get(request, fleet_id, fields):
    """Get fleet info."""
    return iotronicclient(request).fleet.get(fleet_id, fields)


def fleet_create(request, name, description):
    """Create fleet."""
    params = {"name": name,
              "description": description}

    iotronicclient(request).fleet.create(**params)


def fleet_delete(request, fleet_id):
    """Delete fleet."""
    iotronicclient(request).fleet.delete(fleet_id)


def fleet_update(request, fleet_id, patch):
    """Update fleet."""
    iotronicclient(request).fleet.update(fleet_id, patch)


def fleet_get_boards(request, fleet_id):
    """Get fleet boards."""
    return iotronicclient(request).fleet.boards_in_fleet(fleet=fleet_id)


# WEBSERVICES MANAGEMENT
def webservice_list(request, detail=None):
    """Get web services list."""
    return iotronicclient(request).webservice.list()


def webservice_enabled_list(request):
    """Get enabled web services list."""
    return iotronicclient(request).enabledwebservice.list()


def webservice_get_enabled_info(request, board_id, detail=None):
    """Get the information of the enabled webservices."""
    ws_info = []

    ws_enabled = iotronicclient(request).enabledwebservice.list()

    for ws in ws_enabled:
        if ws.board_uuid == board_id:
            ws_info = ws
            break

    return ws_info


def webservices_on_board(request, board_id, fields=None):
    """Get web services on board list."""
    webservices = iotronicclient(request).webserviceonboard.list(board_id,
                                                                 fields)

    detailed_webservices = []
    # fields = {"name", "port", "uuid"}

    for ws in webservices:
        detailed_webservices.append({"name": ws._info["name"],
                                     "port": ws._info["port"],
                                     "uuid": ws._info["uuid"]})

    return detailed_webservices


def webservice_get(request, webservice_id, fields):
    """Get web service info."""
    return iotronicclient(request).webservice.get(webservice_id, fields)


def webservice_expose(request, board_id, name, port, secure):
    """Expose a web service."""
    return iotronicclient(request).webserviceonboard.expose(board_id,
                                                            name,
                                                            port,
                                                            secure)


def webservice_unexpose(request, webservice_id):
    """Unexpose a web service from a board."""
    return iotronicclient(request).webservice.delete(webservice_id)


def webservice_enable(request, board, dns, zone, email):
    """Enable web service."""
    return iotronicclient(request).webserviceonboard.enable_webservice(board,
                                                                       dns,
                                                                       zone,
                                                                       email)


def webservice_disable(request, board):
    """Disable web service."""
    return iotronicclient(request).webserviceonboard.disable_webservice(board)


def boards_no_webservice(request):
    """Get all the boards that have not webservice enabled."""

    boards_no_ws_enabled = []

    board_list = iotronicclient(request).board.list()
    board_list.sort(key=lambda b: b.name)

    board_ws_list = iotronicclient(request).enabledwebservice.list()

    for board in board_list:
        for i in range(len(board_ws_list)):
            if board.uuid == board_ws_list[i].board_uuid:
                break
            elif ((board.uuid != board_ws_list[i].board_uuid) and
                 (i==len(board_ws_list)-1)):
                boards_no_ws_enabled.append((board.uuid, _(board.name)))

    # LOG.debug('COMPLEMENTARY %s', boards_no_ws_enabled)
    return boards_no_ws_enabled
