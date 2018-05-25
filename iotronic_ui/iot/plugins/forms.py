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

import cPickle
import json
import logging

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
# START FROM HERE !!!!!!! openstack_dashboard/api/nova.py
# from iotronicclient.common.apiclient import exceptions as iot_exceptions

from horizon import forms
from horizon import messages

from openstack_dashboard.api import iotronic
from openstack_dashboard import policy

LOG = logging.getLogger(__name__)


class CreatePluginForm(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Plugin Name"))

    """
    public = forms.ChoiceField(
        label=_("Public"),
        choices =[('false', _('False')), ('true', _('True'))],
        widget=forms.Select(
            attrs={'class': 'switchable', 'data-slug': 'slug-public'},
        )
    )
    """

    public = forms.BooleanField(label=_("Public"), required=False)
    callable = forms.BooleanField(label=_("Callable"), required=False)

    code = forms.CharField(
        label=_("Code"),
        widget=forms.Textarea(
            attrs={'class': 'switchable', 'data-slug': 'slug-code'})
    )

    parameters = forms.CharField(
        label=_("Parameters"),
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'switchable',
                   'data-slug': 'slug-parameters-create'}),
        help_text=_("Plugin parameters")
    )

    def handle(self, request, data):

        if not data["parameters"]:
            data["parameters"] = {}
        else:
            data["parameters"] = json.loads(data["parameters"])

        try:
            iotronic.plugin_create(request, data["name"],
                                   data["public"], data["callable"],
                                   data["code"], data["parameters"])

            messages.success(request, _("Plugin created successfully."))

            return True
        # except iot_exceptions.ClientException:
        except Exception:
            # LOG.debug("API REQ EXC: %s", request)
            # LOG.debug("API REQ (DICT): %s", exceptions.__dict__)
            exceptions.handle(request, _('Unable to create plugin.'))


class InjectPluginForm(forms.SelfHandlingForm):

    uuid = forms.CharField(label=_("Plugin ID"), widget=forms.HiddenInput)

    name = forms.CharField(
        label=_('Plugin Name'),
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    onboot = forms.BooleanField(label=_("On Boot"), required=False)

    board_list = forms.MultipleChoiceField(
        label=_("Boards List"),
        widget=forms.SelectMultiple(
            attrs={'class': 'switchable', 'data-slug': 'slug-inject-plugin'}),
        help_text=_("Select boards in this pool ")
    )

    def __init__(self, *args, **kwargs):

        super(InjectPluginForm, self).__init__(*args, **kwargs)
        # input=kwargs.get('initial',{})

        boardslist_length = len(kwargs["initial"]["board_list"])

        self.fields["board_list"].choices = kwargs["initial"]["board_list"]
        self.fields["board_list"].max_length = boardslist_length

    def handle(self, request, data):

        counter = 0

        for board in data["board_list"]:
            for key, value in self.fields["board_list"].choices:
                if key == board:

                    try:
                        inject = iotronic.plugin_inject(request, key,
                                                        data["uuid"],
                                                        data["onboot"])
                        # LOG.debug("API: %s %s", plugin, request)
                        message_text = inject
                        messages.success(request, _(message_text))

                        if counter != len(data["board_list"]) - 1:
                            counter += 1
                        else:
                            return True

                    except Exception:
                        message_text = "Unable to inject plugin on board " \
                                       + str(value) + "."
                        exceptions.handle(request, _(message_text))

                    break


class StartPluginForm(forms.SelfHandlingForm):

    uuid = forms.CharField(label=_("Plugin ID"), widget=forms.HiddenInput)

    name = forms.CharField(
        label=_('Plugin Name'),
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    board_list = forms.MultipleChoiceField(
        label=_("Boards List"),
        widget=forms.SelectMultiple(
            attrs={'class': 'switchable',
                   'data-slug': 'slug-start-boards'}),
        help_text=_("Select boards in this pool ")
    )

    parameters = forms.CharField(
        label=_("Parameters"),
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'switchable',
                   'data-slug': 'slug-startplugin-json'}),
        help_text=_("Plugin parameters")
    )

    def __init__(self, *args, **kwargs):

        super(StartPluginForm, self).__init__(*args, **kwargs)
        # input=kwargs.get('initial',{})

        boardslist_length = len(kwargs["initial"]["board_list"])

        self.fields["board_list"].choices = kwargs["initial"]["board_list"]
        self.fields["board_list"].max_length = boardslist_length

    def handle(self, request, data):

        counter = 0

        if not data["parameters"]:
            data["parameters"] = {}
        else:
            data["parameters"] = json.loads(data["parameters"])

        for board in data["board_list"]:
            for key, value in self.fields["board_list"].choices:
                if key == board:

                    try:
                        action = iotronic.plugin_action(request, key,
                                                        data["uuid"],
                                                        "PluginStart",
                                                        data["parameters"])
                        # LOG.debug("API: %s %s", plugin, request)
                        message_text = action
                        messages.success(request, _(message_text))

                        if counter != len(data["board_list"]) - 1:
                            counter += 1
                        else:
                            return True

                    except Exception:
                        message_text = "Unable to start plugin on board " \
                                       + str(value) + "."
                        exceptions.handle(request, _(message_text))

                    break


class StopPluginForm(forms.SelfHandlingForm):

    uuid = forms.CharField(label=_("Plugin ID"), widget=forms.HiddenInput)

    name = forms.CharField(
        label=_('Plugin Name'),
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    delay = forms.IntegerField(
        label=_("Delay in secs"),
        required=False,
        help_text=_("OPTIONAL: seconds to wait before stopping the plugin")
    )

    board_list = forms.MultipleChoiceField(
        label=_("Boards List"),
        widget=forms.SelectMultiple(
            attrs={'class': 'switchable', 'data-slug': 'slug-stop-boards'}),
        help_text=_("Select boards in this pool ")
    )

    def __init__(self, *args, **kwargs):

        super(StopPluginForm, self).__init__(*args, **kwargs)
        # input=kwargs.get('initial',{})

        boardslist_length = len(kwargs["initial"]["board_list"])

        self.fields["board_list"].choices = kwargs["initial"]["board_list"]
        self.fields["board_list"].max_length = boardslist_length

    def handle(self, request, data):

        counter = 0

        if not data["delay"]:
            data["delay"] = {}
        else:
            data["delay"] = {"delay": data["delay"]}

        for board in data["board_list"]:
            for key, value in self.fields["board_list"].choices:
                if key == board:

                    try:
                        action = iotronic.plugin_action(request, key,
                                                        data["uuid"],
                                                        "PluginStop",
                                                        data["delay"])
                        # LOG.debug("API: %s %s", plugin, request)
                        message_text = action
                        messages.success(request, _(message_text))

                        if counter != len(data["board_list"]) - 1:
                            counter += 1
                        else:
                            return True

                    except Exception:
                        message_text = "Unable to stop plugin on board " \
                                       + str(value) + "."
                        exceptions.handle(request, _(message_text))

                    break


class CallPluginForm(forms.SelfHandlingForm):

    uuid = forms.CharField(label=_("Plugin ID"), widget=forms.HiddenInput)

    name = forms.CharField(
        label=_('Plugin Name'),
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    board_list = forms.MultipleChoiceField(
        label=_("Boards List"),
        widget=forms.SelectMultiple(
            attrs={'class': 'switchable', 'data-slug': 'slug-call-boards'}),
        help_text=_("Select boards in this pool ")
    )

    parameters = forms.CharField(
        label=_("Parameters"),
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'switchable',
                   'data-slug': 'slug-callplugin-json'}),
        help_text=_("Plugin parameters")
    )

    def __init__(self, *args, **kwargs):

        super(CallPluginForm, self).__init__(*args, **kwargs)
        # input=kwargs.get('initial',{})

        boardslist_length = len(kwargs["initial"]["board_list"])

        self.fields["board_list"].choices = kwargs["initial"]["board_list"]
        self.fields["board_list"].max_length = boardslist_length

    def handle(self, request, data):

        counter = 0

        if not data["parameters"]:
            data["parameters"] = {}
        else:
            data["parameters"] = json.loads(data["parameters"])

        for board in data["board_list"]:
            for key, value in self.fields["board_list"].choices:
                if key == board:

                    try:
                        action = iotronic.plugin_action(request, key,
                                                        data["uuid"],
                                                        "PluginCall",
                                                        data["parameters"])

                        message_text = action
                        messages.success(request, _(message_text))

                        if counter != len(data["board_list"]) - 1:
                            counter += 1
                        else:
                            return True

                    except Exception:
                        message_text = "Unable to call plugin on board " \
                                       + str(value) + "."
                        exceptions.handle(request, _(message_text))

                    break


class RemovePluginForm(forms.SelfHandlingForm):

    uuid = forms.CharField(label=_("Plugin ID"), widget=forms.HiddenInput)

    name = forms.CharField(
        label=_('Plugin Name'),
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    board_list = forms.MultipleChoiceField(
        label=_("Boards List"),
        widget=forms.SelectMultiple(
            attrs={'class': 'switchable', 'data-slug': 'slug-remove-boards'}),
        help_text=_("Select boards in this pool ")
    )

    def __init__(self, *args, **kwargs):

        super(RemovePluginForm, self).__init__(*args, **kwargs)
        # input=kwargs.get('initial',{})

        boardslist_length = len(kwargs["initial"]["board_list"])

        self.fields["board_list"].choices = kwargs["initial"]["board_list"]
        self.fields["board_list"].max_length = boardslist_length

    def handle(self, request, data):

        counter = 0

        for board in data["board_list"]:
            for key, value in self.fields["board_list"].choices:
                if key == board:

                    try:
                        iotronic.plugin_remove(request,
                                               key,
                                               data["uuid"])
                        # LOG.debug("API: %s %s", plugin, request)
                        message_text = "Plugin removed successfully from" \
                                       + " board " + str(value) + "."
                        messages.success(request, _(message_text))

                        if counter != len(data["board_list"]) - 1:
                            counter += 1
                        else:
                            return True

                    except Exception:
                        message_text = "Unable to remove plugin from board " \
                                       + str(value) + "."
                        exceptions.handle(request, _(message_text))

                    break


class UpdatePluginForm(forms.SelfHandlingForm):

    uuid = forms.CharField(label=_("Plugin ID"), widget=forms.HiddenInput)
    owner = forms.CharField(label=_("Owner"), widget=forms.HiddenInput)
    name = forms.CharField(label=_("Plugin Name"))
    public = forms.BooleanField(label=_("Public"), required=False)
    callable = forms.BooleanField(label=_("Callable"), required=False)

    code = forms.CharField(
        label=_("Code"),
        widget=forms.Textarea(
            attrs={'class': 'switchable', 'data-slug': 'slug-code'})
    )

    def __init__(self, *args, **kwargs):

        super(UpdatePluginForm, self).__init__(*args, **kwargs)

        # Admin
        if policy.check((("iot", "iot:update_plugins"),), self.request):
            # LOG.debug("ADMIN")
            pass

        # Admin_iot_project
        elif policy.check((("iot", "iot:update_project_plugins"),),
                          self.request):
            # LOG.debug("IOT ADMIN")

            if self.request.user.id != kwargs["initial"]["owner"]:
                # LOG.debug("NO-edit IOT ADMIN")
                self.fields["name"].widget.attrs = {'readonly': 'readonly'}
                self.fields["public"].widget.attrs = {'disabled': 'disabled'}
                self.fields["callable"].widget.attrs = {'disabled': 'disabled'}
                self.fields["code"].widget.attrs = {'readonly': 'readonly'}

        # Other users
        else:
            if self.request.user.id != kwargs["initial"]["owner"]:
                # LOG.debug("IMMUTABLE FIELDS")
                self.fields["name"].widget.attrs = {'readonly': 'readonly'}
                self.fields["public"].widget.attrs = {'disabled': 'disabled'}
                self.fields["callable"].widget.attrs = {'disabled': 'disabled'}
                self.fields["code"].widget.attrs = {'readonly': 'readonly'}

    def handle(self, request, data):
        try:

            data["code"] = cPickle.dumps(str(data["code"]))

            iotronic.plugin_update(request, data["uuid"],
                                   {"name": data["name"],
                                    "public": data["public"],
                                    "callable": data["callable"],
                                    "code": data["code"]})

            messages.success(request, _("Plugin " + str(data["name"]) +
                                        " updated successfully."))
            return True

        except Exception:
            exceptions.handle(request, _('Unable to update plugin.'))
