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

import json
import mock

from openstackclient.tests import fakes as osc_fakes

from oscdebug.tests import base
from oscdebug.v1 import api


fake_endpoint = {
    'type': 'ttt',
    'name': 'nnn',
    'region': 'rrr',
    'endpoint': 'eee',
}

FAPI_v2 = {
    "status": "stable",
    "updated": "2013-03-06T00:00:00Z",
    "media-types": [
        {
            "base": "application/json",
            "type": "application/vnd.openstack.identity-v2.0+json"
        },
        {
            "base": "application/xml",
            "type": "application/vnd.openstack.identity-v2.0+xml"
        }
    ],
    "id": "v2.0",
    "links": [
        {
            "href": "http://10.130.50.11:5000/v2.0/",
            "rel": "self"
        },
        {
            "href": "http://docs.openstack.org/api/openstack-identity-service/2.0/content/",  # noqa
            "type": "text/html",
            "rel": "describedby"
        },
        {
            "href": "http://docs.openstack.org/api/openstack-identity-service/2.0/identity-dev-guide-2.0.pdf",  # noqa
            "type": "application/pdf",
            "rel": "describedby"
        }
    ]
}

FAPI_v3 = {
    "status": "stable",
    "updated": "2013-03-06T00:00:00Z",
    "media-types": [
        {
            "base": "application/json",
            "type": "application/vnd.openstack.identity-v3+json"
        },
        {
            "base": "application/xml",
            "type": "application/vnd.openstack.identity-v3+xml"
        }
    ],
    "id": "v3.0",
    "links": [
        {
            "href": "http://10.130.50.11:35357/v3/",
            "rel": "self"
        }
    ]
}

FAPI_All = {
    "versions": [
        FAPI_v2,
        FAPI_v3,
    ]
}

fake_identity_version_single = {
    'versions': {
        'values': [
            {
                "status": "stable",
                "updated": "2013-03-06T00:00:00Z",
                "media-types": [
                    {
                        "base": "application/json",
                        "type": "application/vnd.openstack.identity-v3+json"
                    },
                    {
                        "base": "application/xml",
                        "type": "application/vnd.openstack.identity-v3+xml"
                    }
                ],
                "id": "v3.0",
                "links": [
                    {
                        "href": "http://10.130.50.11:5000/v3/",
                        "rel": "self"
                    }
                ]
            }
        ]
    }
}


class TestApiList(base.TestCommand):

    def setUp(self):
        super(TestApiList, self).setUp()

        self.app.client_manager.session = mock.MagicMock()

        # Mock get_api_versions
        json_mock = mock.MagicMock(
            json=mock.MagicMock(return_value=FAPI_All),
        )

        self.app.client_manager.session.get.return_value = json_mock

        # Get the command object to test
        self.cmd = api.ListAPI(self.app, None)

    def test_api_list_no_options(self):
        pass

    @mock.patch('oscdebug.v1.api.get_api_versions')
    @mock.patch('oscdebug.v1.api.get_service_catalog_endpoints')
    def test_api_list_long(self, gsce_mock, gav_mock):
        gsce_mock.return_value = [fake_endpoint]
        gav_mock.return_value = osc_fakes.FakeResponse(
            data=json.dumps(FAPI_All)
        )

        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        # columns, data = self.cmd.take_action(parsed_args)

        # print "data: %s" % \
        #     self.app.client_manager.session.get.assert_called_with(1)
        # assertEqual(True, False)

        # collist = (
        #     "Type",
        #     "Name",
        #     "Region",
        #     "Endpoint",
        #     "Version",
        # )
        # self.assertEqual(collist, columns)
        # datalist = (
        #     'password',
        #     mock.ANY,
        # )
        # self.assertEqual(datalist, list(data))
