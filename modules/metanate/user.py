# -*- coding: utf-8 -*-
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')

from utils import logger
from utils.error import MDMiHttpError
from utils.error import MDMiInvalidParameterError

from hosteddb.hosted_user import HostedUser

from metanate.base import MetanateBase

class MetanateUser(MetanateBase):
    def __init__(self, account_id, transaction=None, host=None, port=443):
        """Parameters:
            account_id: like 86, 93
            transaction: an instance of metanate.transaction.begin
            host: the metanate server's hostname or ip
            port: the port of metanate service
        """
        super(self.__class__, self).__init__(account_id, transaction, host, port)

    def __del__(self):
        super(self.__class__, self).__del__()

    def add_user(self, dn, mail, object_guid=None, **kwargs):
        """
        add an user in metanate
        Parameters:
            dn: the ldap dn of user
            mail: email, like xli@websense.com
            object_guid: the attribute of uid in RS
            **kwargs: other key-values to perform. The valid keys are (cn,mail,o,dn).
        """
        if not object_guid:
            object_guid = self.generate_guid()
        return self.replace_user(dn, mail, object_guid, 'add', **kwargs)

    def remove_user(self, dn, object_guid):
        """
        remove an user from metanate
        Parameters:
            dn: the dn of user in ldap
            object_guid: 
            **kwargs: other key-values to perform. The valid keys are (cn,mail,o,dn).
        """
        if not dn:
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'dn should not empty or None')

        dic = {'dn': dn, 'objectguid': [object_guid], 'objectclass': ['User']}

        return self._process_once('remove', **dic)

    def replace_user(self, dn, mail, object_guid, method_name='replace', **kwargs):
        """
        replace an user in metanate, this method will delete account's other users.
            use this method carefully.
        Parameters:
            dn: the ldap dn of user
            mail: email, like xli@websense.com
            object_guid: the attribute of uid in RS
            method_name: add user -> add
                         replace user -> replace
                         remove user -> remove
                         the default value is replace
            **kwargs: other key-values to perform. The valid keys are (cn,mail,o,dn).
        """
        if not dn:
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'dn should not empty or None')

        dic = self._parse_args_to_dict(kwargs)

        dic['dn'] = dn
        if not dic.has_key('cn'):
            dic['cn'] = dn

        if mail:
            if dic.has_key('mail'):
                if dic.has_key('mailalias'):
                    dic['mailalias'].extend(dic['mail'])
                else:
                    dic['mailalias'] = [dic['mail']]

            dic['mail'] = [mail]

        if dic.has_key('objectclass'):
            if 'User' not in dic['objectclass']:
                dic['objectclass'].append('User')
        else:
            dic['objectclass'] = ['User']

        if not dic.has_key('objectguid') or not dic['objectguid']:
            if object_guid:
                dic['objectguid'] = [object_guid]
            else:
                dic['objectguid'] = self.generate_guid()

        return self._process_once(method_name, **dic)

    def _retrieve_user(self, **kwargs):
        rs = self._process_once('retrieve')
        if not kwargs:
            logger.warning('the retrieve condition is empty or none, it will return all users in metanate')
            return rs

        # get a key and value from kwargs
        key, value = self._get_key_value_from_dict(kwargs)
        logger.info('metanate retrieve key and value are: %s - %s', key, value)
        if not key:
            logger.error('parameter did not contain "dn", "cn" or "objectguid"')
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'parameter did not contain "dn", "cn" or "objectguid"')

        for r in rs.content:
            if isinstance(r, tuple) and len(r) == 2 and isinstance(r[1], dict):
                if key == 'dn':
                    if r[0] == value:
                        return r
                else:
                    r1 = self._convert_dict_key_to_lower(r[1])
                    if r1.has_key(key) and isinstance(r1[key], list) and value in r1[key]:
                        return r

        logger.error('cannot find user with condition: %s', kwargs)
        return None

    def retrieve_user_by_mail(self, mail):
        """retrieve a user by email from MDM groups
        Parameters:
            email: user's email address
        """
        if not mail:
            logger.error('the user email parameter is empty or none')
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'The user email parameter is empty or none')

        return self._retrieve_user(mail=mail)

    def retrieve_user_by_dn(self, dn):
        """retrieve a user by dn from MDM groups
        Parameters:
            dn: user's ldap dn
        """
        if not dn:
            logger.error('the dn parameter is empty or none')
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'The dn parameter is empty or none')

        return self._retrieve_user(dn=dn)

    def retrieve_user_by_guid(self, object_guid):
        """retrieve a user by ObjectGUID from MDM groups
        Parameters:
            object_guid: user's ObjectGUID, in RS it is UID
        """
        if not object_guid:
            logger.error('the objectGUID parameter is empty or none')
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'The objectGUID parameter is empty or none')

        return self._retrieve_user(objectguid=object_guid)

    def _modify_user(self, condition, **kwargs):
        """
        modify a user in metanate
        Parameters:
            condition: a dict, the keys of it maybe one or more items in ('mail', 'dn', objectguid')`
            **kwargs: contains the values to modify to. The valid keys are (cn,mail,o,dn).
        """
        if not condition or not isinstance(condition, dict):
            logger.error('the search condition is empty or none')
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'The search condition is empty or none')

        # get a key and value from condition
        key, value = self._get_key_value_from_dict(condition)
        if not key:
            logger.error('condition parameter did not contain "dn", "cn" or "objectguid"')
            raise MDMiInvalidParameterError(601, 'Invalid Parameter',
                    'condition parameter: %s did not contain "dn", "cn" or "objectguid"' % condition)

        try:
            if not self.transaction:
                r = self.rest.create_session(object_class='Users')
                logger.info('metanate operation CREATESESSION for Users, result: %s', r)

            # to retrieve user from metanate
            rs = self.rest.retrieve()
            rr = None
            for r in rs.content:
                if r and isinstance(r, tuple) and len(r) == 2 and isinstance(r[1], dict):
                    r1 = self._convert_dict_key_to_lower(r[1])
                    if key == 'dn':
                        if value == r[0]:
                            rr = r
                            break
                    elif r1.has_key(key) and isinstance(r1[key], list) and value in r1[key]:
                        rr = r
                        break

            if not rr:
                if condition.has_key('mail'):
                    hosted_user = HostedUser(self.account_id)
                    # TODO get user from RS by user email
                    rr = hosted_user.get_user(condition['mail'])

                if condition.has_key('dn'):
                    # TODO needs it to get user from RS by dn?
                    # rr = hosted_user.get_user_by_opdn(condition['dn'])
                    pass

                if condition.has_key('objectguid'):
                    # TODO needs it to get user from RS by objectguid?
                    # rr = hosted_user.get_user_by_uid(condition['objectguid'])
                    pass

                if not rr:
                    logger.error('can not find user with condition: %s' % condition)
                    raise MDMiHttpError(404, 'Not Found', 'can not find user with condition: %s' % condition)

                if rr.has_key('attributes'):
                    rr = rr['attributes']
                if rr.has_key('opdn'):
                    rr = (rr.pop('opdn'), rr)
                else:
                    rr = (rr['cn'].join(['cn=', ',ou=Users,dc=awmdm,dc=com']), rr)

                # generate guid if the user do not have one.
                if not rr[1].has_key('uid'):
                    rr[1]['objectguid'] = self.generate_guid()
                else:
                    rr[1]['objectguid'] = rr[1].pop('uid')

            # do remove user from metanate
            if not self.transaction:
                r = self.rest.remove(dn=rr[0], **rr[1])
                logger.info('metanate operation REMOVE on data %s, result: %s', rr, r)
            else:
                logger.info('metanate operation REMOVE was in transaction')
                self._process_once('remove', 'Users', dn=rr[0], **rr[1])

            # replace value
            to_dic = self._parse_args_to_dict(kwargs)
            dic = self._parse_args_to_dict(rr[1])
            for k, v in to_dic.iteritems():
                dic[k] = v

            if not dic.has_key('dn'):
                # replace dn
                cn_ = rr[1]['cn']
                if isinstance(cn_, (list, tuple)):
                    cn_ = cn_[0]
                if cn_ == dic['cn'][0]:
                    dic['dn'] = rr[0]
                else:
                    dn = rr[0]
                    pos = dn.find('cn')
                    if pos >= 0:
                        tmp = dn[pos:]
                        end = tmp.find(',')
                        if end > 0:
                            dic['dn'] = dic['cn'][0].join(['cn=', dn[end:]])
                        else:
                            dic['dn'] = dic['cn'][0]
                    else:
                        dic['dn'] = dn
            elif isinstance(dic['dn'], (list, tuple)):
                    dic['dn'] = dic['dn'][0]

            # to add user to metanate
            if not self.transaction:
                r = self.rest.add(**dic)
                logger.info('metanate operation ADD on data %s, result: %s', dic, r)
            else:
                logger.info('metanate operation ADD was in transaction')
                r = self._process_once('add', 'Users', **dic)

            if not self.transaction:
                r = self.rest.commit()
                logger.info('metanate operation COMMIT, result: %s', r)

            return r
        finally:
            if not self.transaction:
                r = self.rest.close_session()
                logger.info('metanate operation CLOSESESSION, result: %s', r)

    def modify_user_by_mail(self, user_email, **kwargs):
        """
        modify a user in metanate
        Parameters:
            user_email: email address, like xli@websense.com
            **kwargs: contains the values to modify to. The valid keys are (cn,mail,o,dn).
        """
        return self._modify_user({'mail': user_email}, **kwargs)

    def modify_user_by_dn(self, user_dn, **kwargs):
        """
        modify a user in metanate
        Parameters:
            dn: the dn of user
            **kwargs: contains the values to modify to. The valid keys are (cn,mail,o,dn).
        """
        return self._modify_user({'dn': user_dn}, **kwargs)

    def modify_user_by_guid(self, object_guid, **kwargs):
        """
        modify a user in metanate
        Parameters:
            object_guid: objectGUID of user
            **kwargs: contains the values to modify to. The valid keys are (cn,mail,o,dn).
        """
        return self._modify_user({'objectguid': object_guid}, **kwargs)

    def add_airwatch_user(self, cn, group, mail, **kwargs):
        """
        Deprecated: add an airwatch user into metanate
        Parameters:
            cn: common name like 'xli'
            group: group name like 'dev group'
            mail: email, like xli@websense.com
            **kwargs: contains the values to modify to.
        """
        return self.replace_airwatch_user(cn, group, mail, self.generate_guid(), 'add', **kwargs)

    def remove_airwatch_user(self, cn, group, object_guid):
        """
        Deprecated: remove an airwatch user from metanate
        Parameters:
            cn: common name like 'xli'
            group: group name like 'dev group'
        """
        if not cn or not group:
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'cn and group should not empty or None')

        dic = {}

        dic['dn'] = 'cn={cn},ou=Users,ou={ou},dc=awmdm,dc=com'.format(cn=cn, ou=group)
        if dic.has_key('cn'):
            if cn not in dic['cn']:
                dic['cn'].append(cn)
        else:
            dic['cn'] = [cn]

        if dic.has_key('objectclass'):
            if 'User' not in dic['objectclass']:
                dic['objectclass'].append('User')
        else:
            dic['objectclass'] = ['User']

        dic['objectguid'] = [object_guid]

        return self._process_once('remove', **dic)

    def replace_airwatch_user(self, cn, group, mail, object_guid, method_name='replace', **kwargs):
        """
        Deprecated: replace an airwatch user in metanate, this method will delete account's other users.
            use this method carefully.
        Parameters:
            cn: common name like 'xli'
            group: group name like 'dev group'
            mail: email, like xli@websense.com
        """
        if not cn or not group:
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'cn and group should not empty or None')

        dic = self._parse_args_to_dict(kwargs)

        dn = 'cn={cn},ou=Users,ou={ou},dc=awmdm,dc=com'.format(cn=cn, ou=group)
        if dic.has_key('cn'):
            if cn not in dic['cn']:
                dic['cn'].append(cn)
        else:
            dic['cn'] = [cn]

        if dic.has_key('memberof'):
            if dic.has_key('group_dn') and dic['group_dn']:
                g = dic.pop('group_dn')
            else:
                g = 'cn={group},cn=Users,dc=awmdm,dc=com'.format(group=group)
            if g not in dic['memberof']:
                dic['memberof'].append(g)
        else:
            if dic.has_key('group_dn') and dic['group_dn']:
                dic['memberof'] = dic.pop('group_dn')
            else:
                dic['memberof'] = 'cn={group},cn=Users,dc=awmdm,dc=com'.format(group=group)

        if dic.has_key('group_dn'):
            dic.pop('group_dn')

        return self.replace_user(dn, mail, object_guid, method_name, **dic)

    def modify_airwatch_user(self, user_email, **kwargs):
        """Deprecated"""
        dic = self._parse_args_to_dict(kwargs)
        if dic.has_key('memberof'):
            if isinstance(dic['memberof'], list) or isinstance(dic['memberof'], tuple):
                l = list(dic['memberof'])
            else:
                l = [dic['memberof']]

            dic['memberof'] = []
            for m in l:
                dic['memberof'].append(str(m).join(['cn=', ',cn=Users,dc=awmdm,dc=com']))

        return self.modify_user_by_mail(user_email, **dic)
