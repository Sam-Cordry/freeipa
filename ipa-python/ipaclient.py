#! /usr/bin/python -E
# Authors: Rob Crittenden <rcritten@redhat.com>
#
# Copyright (C) 2007    Red Hat
# see file 'COPYING' for use and warranty information
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; version 2 or later
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

#!/usr/bin/python

import sys
sys.path.append("/usr/share/ipa")

from ipaserver import funcs
import ipa.rpcclient as rpcclient
import user
import ipa
import config

class IPAClient:

    def __init__(self,local=None):
        self.local = local
        ipa.config.init_config()
        if local:
            self.transport = funcs.IPAServer()
            # client needs to call set_principal(user@REALM)
        else:
            self.transport = rpcclient.RPCClient()

    def set_principal(self,princ):
        """Set the name of the principal that will be used for
           LDAP proxy authentication"""
        if self.local:
            self.transport.set_principal(princ)

    def get_user(self,uid,sattrs=None):
        """Get a specific user by uid. If sattrs is set then only those
           attributes will be returned."""
        result = self.transport.get_user(uid,sattrs)
        return user.User(result)

    def add_user(self,user):
        """Add a user. user is a dict of attribute/value pairs"""

        realm = config.config.get_realm()

        # FIXME: This should be dynamic and can include just about anything
        # Let us add in some missing attributes
        if user.get('homedirectory') is None:
                user['homedirectory'] ='/home/%s' % user['uid']
        if user.get('gecos') is None:
                user['gecos'] = user['uid']

        # FIXME: This can be removed once the DS plugin is installed
        user['uidnumber'] ='501'

        # FIXME: What is the default group for users?
        user['gidnumber'] ='501'
        user['krbprincipalname'] = "%s@%s" % (user['uid'], realm)
        user['cn'] = "%s %s" % (user['givenname'], user['sn'])
        if user.get('gn'):
                del user['gn']

        result = self.transport.add_user(user)
        return result

    def get_all_users(self):
        """Get as a list of User objects all users in the directory"""
        result = self.transport.get_all_users()

        all_users = []
        for (attrs) in result:
            if attrs is not None:
                all_users.append(user.User(attrs))

        return all_users

    def get_add_schema(self):
        """Prototype for the GUI. Specify in the directory fields to
           be displayed and what data to get for new users."""
        result = self.transport.get_add_schema()
        return result

    def find_users(self, criteria, sattrs=None):
        """Find users whose uid matches the criteria. Wildcards are 
           acceptable. Returns a list of User objects."""
        result = self.transport.find_users(criteria, sattrs)

        users = []
        for (attrs) in result:
            if attrs is not None:
                users.append(user.User(attrs))

        return users

    def update_user(self,olduser,newuser):
        """Update a user entry. olduser is a dict of attribute/value pairs
           of the original entry. newuser is a dict of attribute/value pairs
           of the new entry."""

        realm = config.config.get_realm()

        result = self.transport.update_user(olduser,newuser)
        return result

    def mark_user_deleted(self,uid):
        """Set a user as inactive by uid."""

        realm = config.config.get_realm()

        result = self.transport.mark_user_deleted(uid)
        return result
