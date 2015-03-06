#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import sys

from oscdebug.tests import base
from oscdebug.tests import fakes
from oscdebug.v1 import plugin

# Load the plugin init module for the plugin list and show commands
import oscdebug.plugin
plugin_name = 'oscdebug'
plugin_client = 'oscdebug.plugin'


class FakePluginV1Client(object):
    def __init__(self, **kwargs):
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']


class TestPluginV1(base.TestCommand):
    def setUp(self):
        super(TestPluginV1, self).setUp()

        self.app.client_manager.oscdebug = FakePluginV1Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )


class TestPluginList(TestPluginV1):

    def setUp(self):
        super(TestPluginList, self).setUp()

        self.app.ext_modules = [
            sys.modules[plugin_client],
        ]

        # Get the command object to test
        self.cmd = plugin.ListPlugin(self.app, None)

    def test_plugin_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        collist = ('Name', 'Versions', 'Module')
        self.assertEqual(columns, collist)
        datalist = (
            plugin_name,
            oscdebug.plugin.API_VERSIONS.keys(),
            plugin_client,
        )
        for d in data:
            if d[0] == plugin_name:
                self.assertEqual(datalist, d)


class TestPluginShow(TestPluginV1):

    def setUp(self):
        super(TestPluginShow, self).setUp()

        self.app.ext_modules = [
            sys.modules[plugin_client],
        ]

        # Get the command object to test
        self.cmd = plugin.ShowPlugin(self.app, None)

    def test_plugin_show(self):
        arglist = [
            plugin_name,
        ]
        verifylist = [
            ('name', plugin_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        collist = ('1', 'module', 'name')
        self.assertEqual(columns, collist)
        datalist = (
            oscdebug.plugin.API_VERSIONS['1'],
            plugin_client,
            plugin_name,
        )
        self.assertEqual(data, datalist)
