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

from django import template
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import tables

from openstack_dashboard import api

LOG = logging.getLogger(__name__)


class ExposeWebserviceLink(tables.LinkAction):
    name = "expose"
    verbose_name = _("Expose")
    url = "horizon:iot:webservices:expose"
    classes = ("ajax-modal",)
    icon = "plus"
    # policy_rules = (("iot", "iot:expose_webservice"),)


class UnexposeWebserviceLink(tables.LinkAction):
    name = "unexpose"
    verbose_name = _("Unexpose")
    url = "horizon:iot:webservices:unexpose"
    classes = ("ajax-modal",)
    icon = "plus"
    # policy_rules = (("iot", "iot:unexpose_webservice"),)


"""
class DisableWebservicesAction(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Disable",
            u"Disable Web Services",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Disabled Web Service",
            u"Disabled Web Services",
            count
        )
    # policy_rules = (("iot", "iot:disable_webservice"),)

    def delete(self, request, board_id):
        api.iotronic.webservice_disable(request, board_id)
"""


class WebserviceFilterAction(tables.FilterAction):

    def filter(self, table, webservices, filter_string):
        # Naive case-insensitive search.
        q = filter_string.lower()
        return [webservice for webservice in webservices
                if q in webservice.name.lower()]


def show_webservices(board_info):
    template_name = 'iot/webservices/_cell_webservices.html'
    context = board_info._info
    # LOG.debug("CONTEXT: %s", context)
    return template.loader.render_to_string(template_name,
                                            context)


class WebservicesTable(tables.DataTable):

    """
    uuid = tables.WrappingColumn('uuid',
                                 link="horizon:iot:webservices:detail",
                                 verbose_name=_('UUID'))
    """
    board = tables.Column('name', verbose_name=_('Board Name'))

    board_uuid = tables.Column('board_uuid', 
                               verbose_name=_('Board UUID'),
                               hidden=True)

    webservices = tables.Column(show_webservices,
                                verbose_name=_('Web Services'))

    http = tables.Column('http_port', verbose_name=_('HTTP'))
    https = tables.Column('https_port', verbose_name=_('HTTPS'))

    # Overriding get_object_id method because in IoT webservice the "id" is
    # identified by the field UUID
    def get_object_id(self, datum):
        # LOG.debug('SELF: %s', self)
        return datum.board_uuid

    class Meta(object):
        name = "webservices"
        verbose_name = _("Web Services")
        """
        row_actions = (ExposeWebserviceLink,
                       UnexposeWebserviceLink,
                       DisableWebservicesAction)
        table_actions = (WebserviceFilterAction, DisableWebservicesAction)
        """
        row_actions = (ExposeWebserviceLink,
                       UnexposeWebserviceLink)
        table_actions = (WebserviceFilterAction,)
