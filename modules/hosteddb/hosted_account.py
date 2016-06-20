# -*- coding: utf-8 -*-
import sys
import json
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
from hosteddb.hosted_base import HostedBase
from utils import logger
from hosted_access import HostedAccess

class HostedAccount(HostedBase):
    def __init__(self, account_id=1):
        super(HostedAccount, self).__init__(account_id)

    def __del__(self):
        super(HostedAccount, self).__del__()

    def get_airwatch_credential(self):
        """
        Retrieves information about accessing airwatch credentials.
        Parameter   Notes
            email user email
        Returns: On success, a dict may contains following user information
            {
                "ObjectClass": "websenseCustomerAccount",
                "mdmUrl": The host name of the AirWatch REST API
                "mdmUsername": The user name to access AirWatch REST API
                "mdmPassword": The password to access AirWatch REST API
                "mdmToken": the code to access AirWatch REST API, always in the http header named 'aw-tenant-code'
            }
            or a dict contains error on failure.

        """
        # filter = '{"base": "account=%s", "filter": "(objectClass=websenseCustomerAccount)"}' % self.account_id
        credential = self.get_by_filter(None, "(objectClass=websenseCustomerAccount)")
        # {u'dn': u'account=93,dc=blackspider,dc=com', u'attributes': {u'mdmUrl': u'http://www.baidu.com', u'account': u'93', u'mdmPassword': u'mdmPassword_asdfdadf', u'objectClass': u'websenseCustomerAccount', u'enabledServices': u'wdAV,wdCategories,mobile', u'o': u'yongpeng', u'mdmToken': u'mdmToken_aaa', u'mdmUsername': u'testapi'}, u'href': u'https://None/rs/v-1/account-93'}

        if isinstance(credential, dict) and credential.has_key('attributes'):
            return credential['attributes']
        else:
            return credential

    def get_account_ids(self, **conditions):
        """
        Retrieves all accounts.
        Returns: a str list like ['86', '93']
        """
        conds = conditions
        if not conds.get('objectClass'):
            conds['objectClass'] = 'websenseCustomerAccount'
        accounts = self.get_account_id(**conds)
        if not accounts:
            return []
        if isinstance(accounts, dict):
            return [accounts['attributes']['account']]
        if isinstance(accounts, basestring):
            return [accounts]
        else:
            return [account['attributes']['account'] for account in accounts]

    def get_airwatch_account_ids(self):
        """
        Retrieves all airwatch account numbers.

        Returns: a list like ['86', '93']
        """

        # filter = '{"filter": "(&(objectClass=websenseCustomerAccount)(enabledServices=*MDMi-AW*))"}'
        return self.get_account_ids(enabledServices='*MDMi-AW*')

    def get_account_id(self, **conditions):
        """
        Get account id from RS as the specific condifitions
        """
        conds_str = '(&'
        for k, v in conditions.iteritems():
            tmp_str = '(%s=%s)' % (k, str(v))
            conds_str = ''.join([conds_str, tmp_str])
        conds_str = ''.join([conds_str, ')'])
        result = self.get_by_filter_without_base(None, conds_str)
        return result
        pass

    def get_airwatch_hosted_account_ids(self):
        """
        Get Airwatch hosted account IDs, exclude hybrid accounts
        """
        return self.get_account_ids_2({'enabledServices': '*MDMi-AW*'}, {'enabledServices': '*hyPE*'})
        pass

    def get_account_ids_2(self, conditions_include=None, conditions_exclude=None):
        """
        Retrieves all accounts.
        Param notes:
            conditions_include: conditions query by equals/and operation(&) 
            conditions_exclude: conditions query by not operation(!) 
        Returns: a str list like ['86', '93']
        """
        accounts = self.get_accounts(conditions_include, conditions_exclude)
        if not accounts:
            return []
        if isinstance(accounts, dict):
            return [accounts['attributes']['account']]
        if isinstance(accounts, basestring):
            return [accounts]
        else:
            return [account['attributes']['account'] for account in accounts]

    def get_accounts(self, conditions_include=None, conditions_exclude=None):
        """
        Get accounts from RS as the specific conditions
        Param notes:
            conditions_include: conditions query by equals/and operation(&) 
            conditions_exclude: conditions query by not operation(!) 
        """
        if not conditions_include:
            conditions_include = {}
        if not conditions_include.get('objectClass'):
            conditions_include['objectClass'] = 'websenseCustomerAccount'

        conds_str = '(&'
        for k, v in conditions_include.iteritems():
            tmp_str = '(%s=%s)' % (k, str(v))
            conds_str = ''.join([conds_str, tmp_str])
        conds_exclude_str = ''
        if conditions_exclude:
            conds_exclude_str = '(!'
            for k, v in conditions_exclude.iteritems():
                tmp_str = '(%s=%s)' % (k, str(v))
                conds_exclude_str = ''.join([conds_exclude_str, tmp_str])
            conds_exclude_str = ''.join([conds_exclude_str, ')'])
        conds_str = ''.join([conds_str, conds_exclude_str,')'])
        result = self.get_by_filter_without_base(None, conds_str)
        return result
        pass

    def get_admins(self):
        return self.get_by_filter(None, '(&(objectclass=adminuser))')

    def get_users_by_policyid(self, policyid):
        filter = "(&(objectclass=hosteduser)(policy=%s))" % policyid
        return self.get_all_records_in_order("cn", True, None, filter)

    def get_policyid_by_email(self, email):
        """
        Get policy id from RS by account id
        """
        filter = "(&(objectClass=hosteduser)(mail=%s))" % email
        policy = self.get_by_filter(None, filter)
        if isinstance(policy["attributes"]["policy"], list):
           policyid = int(policy["attributes"]["policy"][0])
        else:
           policyid = int(policy["attributes"]["policy"])
        return policyid
        pass

    def get_vpn_exceptlst_by_policyid(self, policyid):
        """
        Get vpn exception list by policy id and account id
        """
        #{"filter" : "(&(objectclass=hostednetwork)(policy=ppp))", "base" : "account=aaa" }
        filter = "(&(objectclass=hostedNetwork)(policy=%s)(scope=internal))" % policyid
        return self.get_by_filter(None, filter)
        pass

    def get_hosted_networks(self):
        filter = '(&(objectclass=hostedNetwork))'
        return self.get_by_filter(None, filter)

if __name__ == "__main__":
    haccount = HostedAccount(88)
    policy = haccount.get_policyid()
    print policy
    vpnlst = haccount.get_vpn_exceptlst_by_policyid(policy)
    print vpnlst

    hosted_network = haccount.get_hosted_networks()
    print hosted_network
