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

import mock

from oscdebug.tests import base
from oscdebug.v1 import auth


class TestAuthTypeShow(base.TestCommand):

    def setUp(self):
        super(TestAuthTypeShow, self).setUp()

        # Get the command object to test
        self.cmd = auth.ShowAuthType(self.app, None)

    def test_auth_type_show(self):
        arglist = [
            'password',
        ]
        verifylist = [
            ('auth_type', 'password'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        collist = ('name', 'options')
        self.assertEqual(collist, columns)
        datalist = (
            'password',
            mock.ANY,
        )
        self.assertEqual(datalist, data)
