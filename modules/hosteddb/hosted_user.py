# -*- coding: utf-8 -*-
import sys
import json
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
from hosteddb.hosted_base import HostedBase
from hosteddb.hosted_base import BASE_INFINITE, MAX_RS_RESULT_SIZE
from utils import logger

class HostedUser(HostedBase):
    def __init__(self, account_id):
        super(HostedUser, self).__init__(account_id)

    def __del__(self):
        pass

    def _generate_attrs(self, extra):
        attrs = ["cn", "opdn", "mail", "uid", "account", "syncSource"]
        if isinstance(extra, (list, tuple)):
            attrs.extend(extra)
        elif isinstance(extra, basestring):
            attrs.append(extra)

        return attrs

    def get_user(self, email, extra_attrs=None):
        """
        Retrieves information about the specified user.
        Parameter   Notes
            email user email
        Returns: On success, a dict may contains following user information
            {
                "dn": "mail=enduser1@ntpr.com,account=86,dc=blackspider,dc=com",
                "attributes": {
                    "account": "86",
                    "cn": "Mr EndUser1",
                    "objectClass": "hostedUser",
                    "endUserStatus": "Active",
                    "o": "Neat&tidy Piano Removers",
                    "accountType": "webdefence",
                    "mail": "enduser1@ntpr.com"
                },
                "href": "https://wrest/rs/v-1/account-86/mail-enduser1%40ntpr.com"
            }
            or a dict contains error on failure.
        """
        # filter = '{"base": "account=%s", "filter": "(&(objectClass=person)(mail=%s)(endUserStatus=Active))"}' % (self.account_id, email)
        return self.get_by_filter(extra_attrs, "(&(objectClass=person)(mail=%s)(endUserStatus=Active))", email)

    def get_users_by_mail_list(self, mail_list, extra_attrs=None):
        """
        Retrieves information about the specified users.
        Parameter   Notes
            mail_list: user email list
        Returns: On success, a list may contains following user information
            [{
                "dn": "mail=enduser1@ntpr.com,account=86,dc=blackspider,dc=com",
                "attributes": {
                    "account": "86",
                    "cn": "Mr EndUser1",
                    "objectClass": "hostedUser",
                    "endUserStatus": "Active",
                    "o": "Neat&tidy Piano Removers",
                    "accountType": "webdefence",
                    "mail": "enduser1@ntpr.com"
                },
                "href": "https://wrest/rs/v-1/account-86/mail-enduser1%40ntpr.com"
            }]
            or raise an exception.
        """
        if mail_list and isinstance(mail_list, (list, tuple)):
            mail_condition = ['(mail=%s)'] * len(mail_list)
        else:
            logger.error('the argment mail_list is not a list or tuple')
            return None

        # mail_filter = ')(mail='.join(mail_list)
        # mail_filter = mail_filter.join(['(|(mail=', '))'])
        # filter = '{"base": "account=%s", "filter": "(&(objectClass=person)(endUserStatus=Active)%s)"}' % (self.account_id, mail_filter)
        result = self.get_by_filter(extra_attrs, "(&(objectClass=person)(endUserStatus=Active)(|%s))" % ''.join(mail_condition), *mail_list)
        if result and not isinstance(result, list):
            return [result]
        return result

    def get_admin(self, email, extra_attrs=None):
        """
        Retrieves information about the specified admin user.
        Parameter   Notes
            email admin user email
        Returns: On success, a dict may contains following user information
            {
                "dn": "cn=cmburns@ntpr.com (admin),account=86,dc=blackspider,dc=com",
                "attributes": {
                    "account": "86",
                    "cn": "cmburns@ntpr.com (admin)",
                    "objectClass": "adminUser",
                    "o": "Neat&tidy Piano Removers",
                    "sn": "Burns",
                    "portalUser": "TRUE",
                    "mail": "cmburns@ntpr.com",
                    "permissions": "385878079"
                },
                "href": "https://wrest/rs/v-1/account-86/cn-cmburns%40ntpr.com%20%28admin%29"
            }
            or a dict contains error on failure.
        """
        # filter = '{"filter": "(&(objectClass=adminUser)(mail=%s))"}' % email
        return self.get_by_filter_without_base(extra_attrs, "(&(objectClass=adminUser)(mail=%s))", email)

    def get_admin_by_cn(self, cn, extra_attrs=None):
        """
        Retrieves information about the specified admin user.
        Parameter   Notes
            cn admin user cn
        Returns: On success, a dict may contains following user information
            {
                "dn": "cn=cmburns@ntpr.com (admin),account=86,dc=blackspider,dc=com",
                "attributes": {
                    "account": "86",
                    "cn": "cmburns@ntpr.com (admin)",
                    "objectClass": "adminUser",
                    "o": "Neat&tidy Piano Removers",
                    "sn": "Burns",
                    "portalUser": "TRUE",
                    "mail": "cmburns@ntpr.com",
                    "permissions": "385878079"
                },
                "href": "https://wrest/rs/v-1/account-86/cn-cmburns%40ntpr.com%20%28admin%29"
            }
            or a dict contains error on failure.
        """
        # filter = '{"filter": "(&(objectClass=adminUser)(mail=%s))"}' % email
        return self.get_by_filter_without_base(extra_attrs, "(&(objectClass=adminUser)(cn=%s))", cn)

    def get_user_by_type(self, email, type='hostedUser', extra_attrs=None):
        # type = "hybridUser"
        # filter= '{"base": "account=%s", "filter": "(&(objectClass=person)(mail=%s)(objectClass=%s)(!(objectClass=adminUser))(endUserStatus=Active))"}' % (self.account_id, email, type)
        return self.get_by_filter(extra_attrs, "(&(objectClass=person)(mail=%s)(objectClass=%s)(!(objectClass=adminUser))(endUserStatus=Active))", email, type)

    def get_user_by_type_without_base(self, email, type='hostedUser', extra_attrs=None):
        # type = "hybridUser"
        # filter= '{"filter": "(&(objectClass=person)(mail=%s)(objectClass=%s)(!(objectClass=adminUser))(endUserStatus=Active))"}' % (self.account_id, email, type)
        return self.get_by_filter_without_base(extra_attrs, "(&(objectClass=person)(mail=%s)(objectClass=%s)(!(objectClass=adminUser))(endUserStatus=Active))", email, type)

    def auth_admin(self, adminauth=None):
        """
        authenticate admin

        params:
            adminauth : authentication code of the admin
        """
        if not adminauth:
            return False  # invalid input

        resource = '/rs/v-1'
        headers = self.rest.generate_default_header()
        headers['Authorization'] = 'Basic ' + adminauth
        result = self.rest.do_access(resource=resource, method_name='GET', data=None, headers=headers)
        if result.code == 200:  # passed
            try:
                status = json.loads(result.content)
                if status['active'] == 1:  # double check
                    return True
                else:
                    return False
            except Exception, e:
                logger.error('authenticate admin response unknow, ' + e)
                return False
        else:  # invalid admin
            logger.error('authenticate admin result: Unauthorized!')
            return False

    def get_user_by_opdn(self, opdn, extra_attrs=None):
        """
        Retrieve users info by opdn
        Parameters:
            opdn: user's opdn in RS
        Returns: a list of RS user info
        """
        # filter = '{"base": "account=%s", "filter": "(&(objectClass=person)(memberOf=%s)(endUserStatus=Active))"}' % (self.account_id, self.escapeLDAP(group_dn))
        return self.get_by_filter(extra_attrs, "(&(objectClass=person)(opdn=%s)(endUserStatus=Active))", opdn)

    def get_user_by_uid(self, uid, extra_attrs=None):
        """
        Retrieve users info by uid
        Parameters:
            uid: user's uid in RS
        Returns: a list of RS user info
        """
        # filter = '{"base": "account=%s", "filter": "(&(objectClass=person)(memberOf=%s)(endUserStatus=Active))"}' % (self.account_id, self.escapeLDAP(group_dn))
        return self.get_by_filter(extra_attrs, "(&(objectClass=person)(uid=%s)(endUserStatus=Active))", uid)

    def get_users_by_group_dn(self, group_dn, extra_attrs=None):
        """
        Retrieve users info by group DN
        Parameters:
            group_dn: group DN in RS
        Returns: a list of RS user info
        """
        # filter = '{"base": "account=%s", "filter": "(&(objectClass=person)(memberOf=%s)(endUserStatus=Active))"}' % (self.account_id, self.escapeLDAP(group_dn))
        #result = self.get_by_filter(extra_attrs, "(&(objectClass=person)(memberOf=%s)(endUserStatus=Active))", group_dn)
        #if result and not isinstance(result, list):
        #    return [result]
        #return result
        return self.get_all_records_in_order('cn', True, extra_attrs, "(&(objectClass=person)(memberOf=%s)(endUserStatus=Active))", group_dn)

    def get_users(self, extra_attrs=None):
        """
        Retrieve users
        Returns: a list of RS user info
        """
        # filter = '{"base": "account=%s", "filter": "(&(objectClass=person)(endUserStatus=Active))"}' % self.account_id
        #result = self.get_by_filter(extra_attrs, "(&(objectClass=person)(endUserStatus=Active))")
        #if result and not isinstance(result, list):
        #    return [result]
        #return result
        return self.get_all_records_in_order('cn', True, extra_attrs, "(&(objectClass=person)(endUserStatus=Active))")

    def add_user(self, mail, name):
        """
        Add a portal user into RS
        Parameters:
            mail: user's email address
            name: user name, it will be cn in RS
        Returns: 
        """
        # curl -X PUT -k https://cn=mailcontrol%20\(admin\),account=1,dc=blackspider,dc=com:7Nz+BXcOXW3ZTXgZptPmRg@cog01o:8085/rs/v-1/account-93/mail-test143@ntpr.com  -d '{"attributes":{"cn":"test143", "account":"93", "objectClass":"hostedUser","endUserStatus":"Active","mail":"test143@ntpr.com","accountType":"webdefence", "syncSource":"MDM", "uid":"3/fzQ90SREyyTP40BspQEQ==", "opdn":"cn=test143,ou=Users,ou=websense138,dc=awmdm,dc=com"}}'
        resource = '/rs/v-%d/account-%s/mail-%s' % (self.version, self.account_id, mail)
        # info = '{"attributes":{"cn":"%s", "account":"%s", "objectClass":"hostedUser","endUserStatus":"Active","mail":"%s","accountType":"webdefence"}}' % (name, self.account_id, mail)
        info = json.dumps({"attributes":{"cn":name, "account":self.account_id, "objectClass":"hostedUser", "endUserStatus":"Active", "mail":mail, "accountType":"webdefence"}})
        result = self.rest.do_access(resource, method_name="PUT", data=info)
        return result

    def delete_user(self, mail):
        """
        Add a portal user into RS
        Parameters:
            mail: user's email address
            name: user name, it will be cn in RS
        Returns: 
        """
        # curl -X PUT -k https://cn=mailcontrol%20\(admin\),account=1,dc=blackspider,dc=com:7Nz+BXcOXW3ZTXgZptPmRg@cog01o:8085/rs/v-1/account-93/mail-test143@ntpr.com  -d '{"attributes":{"cn":"test143", "account":"93", "objectClass":"hostedUser","endUserStatus":"Active","mail":"test143@ntpr.com","accountType":"webdefence", "syncSource":"MDM", "uid":"3/fzQ90SREyyTP40BspQEQ==", "opdn":"cn=test143,ou=Users,ou=websense138,dc=awmdm,dc=com"}}'
        resource = '/rs/v-%d/account-%s/mail-%s' % (self.version, self.account_id, mail)
        # info = '{"attributes":{"cn":"%s", "account":"%s", "objectClass":"hostedUser","endUserStatus":"Active","mail":"%s","accountType":"webdefence"}}' % (name, self.account_id, mail)
        result = self.rest.do_access(resource, method_name="DELETE")
        return result

    def get_users_have_no_group(self, extra_attrs=None):
        """
        Retrive users not in any group
        Returns:
            a list of RS user info
        """

        #result = self.get_by_filter(extra_attrs, "(&(objectClass=person)(endUserStatus=Active)(!(memberOf=*)))")
        #if result and not isinstance(result, list):
        #    return [result]
        #return result
        return self.get_all_records_in_order('cn', True, extra_attrs, "(&(objectClass=person)(endUserStatus=Active)(!(memberOf=*)))")
