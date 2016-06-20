# -*- coding: utf-8 -*-
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
import json

from hosteddb.hosted_base import HostedBase
from hosteddb.hosted_base import BASE_INFINITE, MAX_RS_RESULT_SIZE
from utils import logger

class HostedGroup(HostedBase):
    def __init__(self, account_id):
        super(HostedGroup, self).__init__(account_id)

    def __del__(self):
        super(HostedGroup, self).__del__()

    def _generate_attrs(self, extra):
        attrs = ["uid", "cn", "groupName", "syncSource"]
        if isinstance(extra, (list, tuple)):
            attrs.extend(extra)
        elif isinstance(extra, basestring):
            attrs.append(extra)

        return attrs

    # curl -k -X POST -d '{"base":"account=86","filter":"(&(objectClass=groupofNames))"}' \
    # https://cn=mailcontrol%20\(admin\),account=1,dc=blackspider,dc=com:7Nz+BXcOXW3ZTXgZptPmRg@cog01o:8085/rs/v-1/search
    def get_group_by_name(self, group_name, extra_attrs=None):
        """
        Retrieves information about the specified group.
        Parameter   Notes
            group_name: the name of group
        Returns: On success, a dict may contains following user information
            {
                "href": "https://cog01o:8085/rs/v-1/account-86/cn-86Group54%5C%3DYCX6",
                "attributes": {
                    "cn": "86Group54=YCX6"
                    "member": [
                        "https://cog01o:8085/rs/v-1/account-86/mail-enduser341%40ntpr.com",
                        "https://cog01o:8085/rs/v-1/account-86/mail-enduser38%40ntpr.com",
                    ],
                    "groupId": "1046"
                    "groupName": "Group54"
                    "objectClass": "hostedGroup"
                },
                "dn": "cn=86Group54\\3DYCX6,account=86,dc=blackspider,dc=com"
            }
            or a dict contains error on failure.
        """
        # filter = '{"base":"account=%s","filter":"(&(objectClass=groupofNames)(groupName=%s))" }' % (self.account_id, group_name)
        return self.get_by_filter(extra_attrs, "(&(objectClass=groupofNames)(groupName=%s))", group_name)

    def get_group_by_id(self, group_id, extra_attrs=None):
        """
        Retrieves information about the specified group.
        Parameter   Notes
            group_id: the id of group
        Returns: On success, a dict may contains following user information
            {
                "href": "https://cog01o:8085/rs/v-1/account-86/cn-86Group54%5C%3DYCX6",
                "attributes": {
                    "cn": "86Group54=YCX6"
                    "member": [
                        "https://cog01o:8085/rs/v-1/account-86/mail-enduser341%40ntpr.com",
                        "https://cog01o:8085/rs/v-1/account-86/mail-enduser38%40ntpr.com",
                    ],
                    "groupId": "1046"
                    "groupName": "Group54"
                    "objectClass": "hostedGroup"
                },
                "dn": "cn=86Group54\\3DYCX6,account=86,dc=blackspider,dc=com"
            }
            or a dict contains error on failure.
        """
        # filter = '{"base":"account=%s","filter":"(&(objectClass=groupofNames)(groupId=%s))" }' % (self.account_id, group_id)
        return self.get_by_filter(extra_attrs, "(&(objectClass=groupofNames)(groupId=%s))", group_id)

    def get_portal_managed_groups_by_user_dn(self, user_dn, extra_attrs=None):
        """
        Retrieves portal managed (syncSource is not 'MDM') group by user DN.
        Parameter   Notes
            user_dn: the DN of RS user
        Returns: On success, a list may contains following information
            [{
                "href": "https://cog01o:8085/rs/v-1/account-86/cn-86Group54%5C%3DYCX6",
                "attributes": {
                    "cn": "86Group54=YCX6"
                    "member": [
                        "https://cog01o:8085/rs/v-1/account-86/mail-enduser341%40ntpr.com",
                        "https://cog01o:8085/rs/v-1/account-86/mail-enduser38%40ntpr.com",
                    ],
                    "groupId": "1046"
                    "groupName": "Group54"
                    "objectClass": "hostedGroup"
                },
                "dn": "cn=86Group54\\3DYCX6,account=86,dc=blackspider,dc=com"
            }]
        """
        # filter = '{"base":"account=%s","filter":"(&(objectClass=groupofNames)(member=%s)(!(syncSource=MDM)))" }' % (self.account_id, user_dn)
        result = self.get_by_filter(extra_attrs, "(&(objectClass=groupofNames)(member=%s)(!(syncSource=MDM)))", user_dn)
        if result and not isinstance(result, list):
            return [result]
        return result

    def get_groups(self, extra_attrs=None):
        """
        Retrieves all available RS groups in the current account.
        Retruns: a list contains RS group info
        """
        # filter = '{"base":"account=%s", "filter":"(&(objectClass=groupofNames))"}' %self.account_id
        #result = self.get_by_filter(extra_attrs, "(&(objectClass=groupofNames))")
        #if result and not isinstance(result, list):
        #    return [result]
        #return result
        return self.get_all_records_in_order('cn', True, extra_attrs, "(&(objectClass=groupofNames))")

    def add_group(self, name, members):
        """
        Add a portal group into RS
        Parameters:
            mail: user's email address
            name: user name, it will be cn in RS
        Returns: 
        """
        # curl -X PUT -k https://cn=mailcontrol%20\(admin\),account=1,dc=blackspider,dc=com:7Nz+BXcOXW3ZTXgZptPmRg@cog01o:8085/rs/v-1/account-93/cn-endtestgroup1  -d '{"attributes":{"cn":"endtestgroup1", "objectClass":"hostedGroup", "groupName": "endtestgroup1", "member":["mail=endtestuser5@ntpr.com,account=93,dc=blackspider,dc=com"]}}'
        resource = '/rs/v-%d/account-%s/cn-%s' % (self.version, self.account_id, name)
        # info = '{"attributes":{"cn":"%s", "objectClass":"hostedGroup", "groupName": "%s", "member":[%s]}}' % (name, name, ','.join(['"%s"' % i for i in members]) if isinstance(members, (list, tuple)) else '"%s"' % members)
        info = json.dumps({"attributes":{"cn":name, "objectClass":"hostedGroup", "groupName": name, "member":members}})
        result = self.rest.do_access(resource, method_name="PUT", data=info)
        return result

    def delete_group(self, name):
        """
        Add a portal group into RS
        Parameters:
            mail: user's email address
            name: user name, it will be cn in RS
        Returns: 
        """
        # curl -X PUT -k https://cn=mailcontrol%20\(admin\),account=1,dc=blackspider,dc=com:7Nz+BXcOXW3ZTXgZptPmRg@cog01o:8085/rs/v-1/account-93/cn-endtestgroup1  -d '{"attributes":{"cn":"endtestgroup1", "objectClass":"hostedGroup", "groupName": "endtestgroup1", "member":["mail=endtestuser5@ntpr.com,account=93,dc=blackspider,dc=com"]}}'
        resource = '/rs/v-%d/account-%s/cn-%s' % (self.version, self.account_id, name)
        # info = '{"attributes":{"cn":"%s", "objectClass":"hostedGroup", "groupName": "%s", "member":[%s]}}' % (name, name, ','.join(['"%s"' % i for i in members]) if isinstance(members, (list, tuple)) else '"%s"' % members)
        result = self.rest.do_access(resource, method_name="DELETE")
        return result
