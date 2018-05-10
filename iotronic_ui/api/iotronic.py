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
# from django.utils.translation import ugettext_lazy as _

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
    boards = iotronicclient(request).board.list(status, detail, project)
    return boards


def board_get(request, board_id, fields):
    """Get board info."""
    board = iotronicclient(request).board.get(board_id, fields)
    return board


def board_create(request, code, mobile, location, type, name):
    """Create board."""
    params = {"code": code,
              "mobile": mobile,
              "location": location,
              "type": type,
              "name": name}
    board = iotronicclient(request).board.create(**params)
    return board


def board_update(request, board_id, patch):
    """Update board."""
    board = iotronicclient(request).board.update(board_id, patch)
    return board


def board_delete(request, board_id):
    """Delete board."""
    board = iotronicclient(request).board.delete(board_id)
    return board


# PLUGIN MANAGEMENT (Cloud Side)
def plugin_list(request, detail=None, project=None, with_public=False,
                all_plugins=False):
    """List plugins."""
    plugins = iotronicclient(request).plugin.list(detail, project, \
                                                  with_public=with_public, \
                                                  all_plugins=all_plugins)
    return plugins


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
    plugin = iotronicclient(request).plugin.create(**params)
    return plugin


def plugin_update(request, plugin_id, patch):
    """Update plugin."""
    plugin = iotronicclient(request).plugin.update(plugin_id, patch)
    return plugin


def plugin_delete(request, plugin_id):
    """Delete plugin."""
    plugin = iotronicclient(request).plugin.delete(plugin_id)
    return plugin


# PLUGIN MANAGEMENT (Board Side)
def plugin_inject(request, board_id, plugin_id, onboot):
    """Inject plugin on board(s)."""
    plugin = iotronicclient(request).plugin_injection. \
                                     plugin_inject(board_id, \
                                                   plugin_id, \
                                                   onboot)
    return plugin


def plugin_action(request, board_id, plugin_id, action, params={}):
    """Start/Stop/Call actions on board(s)."""
    plugin = iotronicclient(request).plugin_injection. \
                                     plugin_action(board_id,
                                                   plugin_id,
                                                   action,
                                                   params)
    return plugin


def plugin_remove(request, board_id, plugin_id):
    """Inject plugin on board(s)."""
    plugin = iotronicclient(request).plugin_injection. \
                                     plugin_remove(board_id, plugin_id)
    return plugin


def plugins_on_board(request, board_id):
    """Plugins on board."""
    plugins = iotronicclient(request).plugin_injection. \
                                      plugins_on_board(board_id)

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
    services = iotronicclient(request).service.list(detail)
    return services


def service_get(request, service_id, fields):
    """Get service info."""
    service = iotronicclient(request).service.get(service_id, fields)
    return service


def service_create(request, name, port, protocol):
    """Create service."""
    params = {"name": name,
              "port": port,
              "protocol": protocol}
    service = iotronicclient(request).service.create(**params)
    return service


def service_update(request, service_id, patch):
    """Update service."""
    service = iotronicclient(request).service.update(service_id, patch)
    return service


def service_delete(request, service_id):
    """Delete service."""
    service = iotronicclient(request).service.delete(service_id)
    return service


def services_on_board(request, board_id, detail=False):
    """List services on board."""
    services = iotronicclient(request).exposed_service \
                                      .services_on_board(board_id)

    if detail:
        detailed_services = []
        fields = {"name", "port", "protocol"}

        for service in services:
            details = iotronicclient(request). \
                      service.get(service._info["service"], fields)

            detailed_services.append({"name": details._info["name"],
                                      "public_port":
                                          service._info["public_port"],
                                      "port": details._info["port"],
                                      "protocol": details._info["protocol"]})

        return detailed_services

    else:
        return services


def service_action(request, board_id, service_id, action):
    """Action on service."""
    service_action = iotronicclient(request).exposed_service. \
                     service_action(board_id, service_id, action)
    return service_action


def restore_services(request, board_id):
    """Restore services."""
    service_restore = iotronicclient(request).exposed_service. \
                      restore_services(board_id)
    return service_restore

