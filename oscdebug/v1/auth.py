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

"""Authentication Debug action implementation"""

import logging
import six

from cliff import lister
from cliff import show

from openstackclient.api import auth


class ListAuthType(lister.Lister):
    """List authentication types (plugins)"""

    auth_required = False
    log = logging.getLogger(__name__ + '.ListAuthType')

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)

        data = []
        for p in auth.PLUGIN_LIST:
            data.append((
                p.name,
                p.entry_point.__str__().split(' = ')[1],
            ))

        columns = ('Name', 'Entry Point')
        return (columns, data)


class ShowAuth(show.ShowOne):
    """Display authentication argument details"""

    auth_required = False
    log = logging.getLogger(__name__ + '.ShowAuth')

    def get_parser(self, prog_name):
        parser = super(ShowAuth, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)

        auth = {}

        # App
        app_attrs = ['default_domain']
        for a in app_attrs:
            v = getattr(self.app, a, None)
            if v:
                auth[a] = v

        opt_attrs = ['os_auth_type', 'os_auth_url',
                     'os_default_domain', 'os_domain_id', 'os_domain_name',
                     'os_project_id', 'os_project_name',
                     'os_user_domain_id', 'os_user_domain-name',
                     'os_user_id', 'os_username',
                     'os_url', 'os_token',
                     'os_trust_id', 'os_region_name']
        for a in opt_attrs:
            v = getattr(self.app.options, a, None)
            if v:
                auth[a] = v

        return zip(*sorted(six.iteritems(auth)))


class ShowAuthType(show.ShowOne):
    """Display authentication type details"""

    auth_required = False
    log = logging.getLogger(__name__ + '.ShowAuthType')

    def get_parser(self, prog_name):
        parser = super(ShowAuthType, self).get_parser(prog_name)
        parser.add_argument(
            'auth_type',
            metavar='<name>',
            help='Authentication type to display',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)

        data = {}

        for p in auth.PLUGIN_LIST:
            if parsed_args.auth_type == p.name:
                data['name'] = p.name

                opts = p.plugin.get_options()
                opt_list = []
                for o in opts:
                    opt_list.append(o.dest.lower().replace('_', '-'))
                data['options'] = ', '.join(opt_list)

        return zip(*sorted(six.iteritems(data)))
