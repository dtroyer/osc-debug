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

"""API Action Implementation"""

import logging
import simplejson

from six.moves.urllib import parse as urlparse

from cliff import lister

from keystoneclient import exceptions as ksc_exceptions
from keystoneclient.openstack.common.apiclient import exceptions \
    as ksc_api_exceptions
from openstackclient.common import utils


LOG = logging.getLogger(__name__)


def get_service_catalog_tnr(sc=None):
    """Extract the unique type/name/region from a service catalog

    The current Keystone client ServiceCatalog implemetation does not
    have an easy way to get a list of all types, names or regions so
    we have to do it here.  This may be fragile to future ServiceCatalog
    changes.

    Return a dict of endpoints keyed by service type, service name
    and region.  Missing components are represented by a null string ('')
    """

    if not sc:
        return {}

    data = sc.get_data()
    ep_tnr = {}
    for row in data:
        # print "row: %s" % row
        e_name = row.get('name', '')
        for ep in row['endpoints']:
            # print "ep: %s" % ep
            region = ep.get('region_id', None) or ep.get('region', '')
            key = '|'.join([row['type'], e_name, region])
            ep_tnr[key] = ep
    return ep_tnr


def get_service_catalog_endpoints(sc, endpoint_type=None):
    """Extract a list of service catalog endpoints of a particular type

    Returns a tuple of (service_type, service_name, region_name, endpoint)
    for all combinations, filtered by a single endpoint type
    """

    if not sc:
        return []

    if not endpoint_type:
        endpoint_type = 'public'

    ep_tnr = get_service_catalog_tnr(sc)

    data = []
    for key in ep_tnr.keys():
        e_type, e_name, e_region = key.split('|')

        # Use the ServiceCatalog method so it can handle the API
        # version differences
        ep = sc.url_for(
            service_type=e_type,
            service_name=e_name,
            region_name=e_region,
            endpoint_type=endpoint_type,
        )
        data.append({
            'type': e_type,
            'name': e_name,
            'region': e_region,
            'endpoint': ep,
        })

    return data


SKIP_EXCEPTIONS = (
    ksc_api_exceptions.BadRequest,
    ksc_api_exceptions.NotFound,
    ksc_exceptions.SSLError,
    simplejson.scanner.JSONDecodeError,
)


def get_api_versions(session, url):
    """Query REST server for supported API versions

    The passed in URL is stripped to host:port to query the root
    of the REST server to get available API versions.

    :param api_name: the name of the API, e.g. 'compute', 'image', etc
    :param url: the URL to query
    :rtype: a list of ApiVersion resources available on the server
    """

    # Break down URL
    u = urlparse.urlparse(url)
    tryurl = "%s://%s" % (u.scheme, u.netloc)
    if u.path.endswith('/'):
        # Dump any trailing seperator
        path = u.path[:-1].split('/')
    else:
        path = u.path.split('/')

    for p in path:
        if tryurl.endswith('/'):
            # Dump any trailing seperator
            tryurl = tryurl[:-1]
        tryurl = '/'.join([tryurl, p])
        LOG.info('attempting to get version from: %s', tryurl)
        try:
            resp = session.get(tryurl).json()
        except (SKIP_EXCEPTIONS):
            continue
        except Exception as x:
            LOG.debug("unskipped exception: %s: %s" % (type(x), x))
            continue
        if 'version' in resp:
            # We only got one, make it a list
            versions = [resp['version']]
        else:
            if 'versions' in resp:
                versions = resp['versions']
            else:
                # Handle bad server response
                versions = []

        # Handle Identity^H^H^H^H^HKeystone anomaly
        if 'values' in versions:
            versions = versions['values']

        # See if we found a version struct
        if versions:
            return (versions, tryurl)

    # ended without success
    return (None, url)


# api list [--compute|--identity|--image|--volume|--current] [--supported]
# Returns a list of the API versions reported by the servers
# --supported Returns a list of the API versions supported by the OSC client

class ListAPI(lister.Lister):
    """List API versions supported by servers"""

    log = logging.getLogger(__name__ + '.ListAPI')

    def get_parser(self, prog_name):
        parser = super(ListAPI, self).get_parser(prog_name)
        parser.add_argument(
            '--type',
            metavar='<service-type>',
            help='Select service type',
        )
        parser.add_argument(
            '--name',
            metavar='<service-name>',
            help='Select service name',
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=('List additional fields in output'),
        )
        return parser

    def take_action(self, parsed_args):

        def _format_links(data):
            """Return a formatted links URL (self only)"""
            output = ""
            for s in data:
                if s['rel'] == 'self':
                    output += s['href'] + ", "
            return output[:-2]

        self.log.debug('take_action(%s)' % parsed_args)

        if parsed_args.long:
            columns = (
                "Type",
                "Name",
                "Region",
                "Endpoint",
                "Version",
            )
        else:
            columns = (
                "Type",
                "Name",
                "Region",
            )

        # This is ugly because if auth hasn't happened yet we need
        # to trigger it here.
        sc = self.app.client_manager.session.auth.get_auth_ref(
            self.app.client_manager.session,
        ).service_catalog

        data = get_service_catalog_endpoints(sc, endpoint_type='public')

        for e in reversed(data):
            if parsed_args.type and parsed_args.type != e['type'] \
                    or parsed_args.name and parsed_args.name != e['name']:
                data.remove(e)
                continue

            if parsed_args.long:
                (ver, actual_url) = get_api_versions(
                    self.app.client_manager.session,
                    e['endpoint'],
                )
                if ver:
                    e['version'] = [v['id'] for v in ver]
                else:
                    e['version'] = []
            LOG.info("row: %s" % e)
        return (
            columns,
            (
                utils.get_dict_properties(
                    s,
                    columns,
                    formatters={'Version': utils.format_list},
                ) for s in data
            )
        )
