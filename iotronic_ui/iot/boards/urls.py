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

from django.conf.urls import url

from iotronic_ui.iot.boards import views


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^create/$', views.CreateView.as_view(), name='create'),
    url(r'^(?P<board_id>[^/]+)/update/$', views.UpdateView.as_view(),
        name='update'),
    url(r'^(?P<board_id>[^/]+)/enableservice/$',
        views.EnableServiceView.as_view(), name='enableservice'),
    url(r'^(?P<board_id>[^/]+)/disableservice/$',
        views.DisableServiceView.as_view(), name='disableservice'),
    url(r'^(?P<board_id>[^/]+)/attachport/$',
        views.AttachPortView.as_view(), name='attachport'),
    url(r'^(?P<board_id>[^/]+)/detachport/$',
        views.DetachPortView.as_view(), name='detachport'),
    url(r'^(?P<board_id>[^/]+)/enablewebservice/$',
        views.EnableWebServiceView.as_view(), name='enablewebservice'),
    url(r'^(?P<board_id>[^/]+)/disablewebservice/$',
        views.DisableWebServiceView.as_view(), name='disablewebservice'),
    url(r'^(?P<board_id>[^/]+)/removeplugins/$',
        views.RemovePluginsView.as_view(), name='removeplugins'),
    url(r'^(?P<board_id>[^/]+)/detail/$', views.BoardDetailView.as_view(),
        name='detail'),
]
