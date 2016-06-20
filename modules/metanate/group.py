# -*- coding: utf-8 -*-
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')

from utils import logger
from utils.error import MDMiHttpError
from utils.error import MDMiInvalidParameterError

from metanate.base import MetanateBase

class MetanateGroup(MetanateBase):
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

    def add_group(self, dn, object_guid=None, **kwargs):
        """add an group in metanate
        Parameters:
            dn: the ldap dn of group
            object_guid: the id of the group
        """
        if not dn:
            logger.error('the format of group dn: %s is not valid', dn)
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'the format of group dn: %s is not valid' % dn)

        if not object_guid:
            object_guid = self.generate_guid()
            
        return self.replace_group(dn, object_guid, 'add', **kwargs)

    def remove_group(self, dn, object_guid):
        """remove an group from metanate
        Parameters:
            dn: dn of group in ldap
            object_guid: the id of the group
        """
        if not dn:
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'dn should not empty or None')

        dic = {'dn': dn, 'objectguid': [object_guid], 'objectclass': ['Group']}

        return self._process_once('remove', 'Groups', **dic)

    def replace_group(self, dn, object_guid, method_name='replace', **kwargs):
        """remove an account's all groups, and add a new one which specified in arguments.
        Parameters:
            dn: dn of group in ldap
            object_guid: the id of the group
            method_name: this can be add, remove, replace, default is replace.
            **kwargs: can be groupname='groupname1'
        """
        if not dn:
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'dn should not empty or None')

        dic = self._parse_args_to_dict(kwargs)

        dic['dn'] = dn
        if not dic.has_key('cn'):
            dic['cn'] = dn

        if dic.has_key('objectclass'):
            dic['objectclass'].append('Group')
        else:
            dic['objectclass'] = ['Group']

        if not dic.has_key('objectguid') or not dic['objectguid']:
            if object_guid:
                dic['objectguid'] = [object_guid]
            else:
                dic['objectguid'] = self.generate_guid()

        return self._process_once(method_name, 'Groups', **dic)

    def _retrieve_group(self, sync_source='MDM', **kwargs):
        rs = self._process_once('retrieve', 'Groups', sync_source)

        if not kwargs:
            logger.warning('the retrieve condition is empty or none, it will return all groups in metanate')
            return rs

        # get a key and value from kwargs
        key, value = self._get_key_value_from_dict(kwargs)
        if not key:
            logger.error('parameter did not contain "dn", "cn" or "objectguid"')
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'parameter did not contain "dn", "cn" or "objectguid"')

        for r in rs.content:
            if isinstance(r, tuple) and len(r) == 2 and isinstance(r[1], dict):
                if key == 'dn':
                    if r[0].lower() == value.lower():
                        return r
                else:
                    r1 = self._convert_dict_key_to_lower(r[1])
                    if r1.has_key(key):
                        if isinstance(r1[key], list):
                            if key == 'objectguid':
                                if value in r1[key]:
                                    return r
                            else: # cn is case insensitive
                                r2 = [i.lower() if isinstance(i, basestring) else i for i in r1[key]]
                                if value.lower() in r2:
                                    return r
                        elif isinstance(r1[key], basestring):
                            if key == 'objectguid':
                                if r1[key] == value:
                                    return r
                            else: # cn is case insensitive
                                if r1[key].lower() == value.lower():
                                    return r

        logger.error('cannot find group with condition: %s', kwargs)
        return None

    def retrieve_group_by_dn(self, dn):
        """retrieve a group by dn from MDM or Directory groups
        Parameters:
            dn: dn of group in ldap
        """
        r = self.retrieve_directory_group_by_dn(dn=dn)
        if r:
            return r
        return self.retrieve_mdm_group_by_dn(dn=dn)

    def retrieve_group_by_guid(self, object_guid):
        """retrieve a group by ObjectGUID from MDM or Directory groups
        Parameters:
            object_guid: the id of the group
        """
        r = self.retrieve_directory_group_by_guid(object_guid=object_guid)
        if r:
            return r
        return self.retrieve_mdm_group_by_guid(object_guid=object_guid)

    def retrieve_group_by_name(self, name):
        """retrieve a group by cn from MDM or Directory groups
        Parameters:
            cn: cn of group in ldap
        """
        r = self.retrieve_directory_group_by_name(name=name)
        if r:
            return r
        return self.retrieve_mdm_group_by_name(name=name)

    def retrieve_directory_group_by_dn(self, dn):
        """retrieve a group by dn from Directory groups
        Parameters:
            dn: dn of group in ldap
        """
        if not dn:
            logger.error('the group dn parameter is empty or none')
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'The group dn parameter is empty or none')

        return self._retrieve_group(sync_source='Directory', dn=dn)

    def retrieve_directory_group_by_guid(self, object_guid):
        """retrieve a group by ObjectGUID from Directory groups
        Parameters:
            object_guid: the id of the group
        """
        if not object_guid:
            logger.error('the group objectGUID parameter is empty or none')
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'The group objectGUID parameter is empty or none')

        return self._retrieve_group(sync_source='Directory', objectguid=object_guid)

    def retrieve_directory_group_by_name(self, name):
        """retrieve a group by cn from Directory groups
        Parameters:
            cn: cn of group in ldap
        """
        if not name:
            logger.error('the group name parameter is empty or none')
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'The group name parameter is empty or none')

        return self._retrieve_group(sync_source='Directory', cn=name)

    def retrieve_mdm_group_by_dn(self, dn):
        """retrieve a group by dn from MDM groups
        Parameters:
            dn: dn of group in ldap
        """
        if not dn:
            logger.error('the group dn parameter is empty or none')
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'The group dn parameter is empty or none')

        return self._retrieve_group(dn=dn)

    def retrieve_mdm_group_by_guid(self, object_guid):
        """retrieve a group by ObjectGUID from MDM groups
        Parameters:
            object_guid: the id of the group
        """
        if not object_guid:
            logger.error('the group objectGUID parameter is empty or none')
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'The group objectGUID parameter is empty or none')

        return self._retrieve_group(objectguid=object_guid)

    def retrieve_mdm_group_by_name(self, name):
        """retrieve a group by cn from MDM groups
        Parameters:
            cn: cn of group in ldap
        """
        if not name:
            logger.error('the group name parameter is empty or none')
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'The group name parameter is empty or none')

        return self._retrieve_group(cn=name)

    def _modify_group(self, condition, **kwargs):
        """modify a group in metanate
        Parameters:
            condition: condition for searching group, such as dn='', cn='', objectguid=''
            kwargs: contains the values to modify to
        """
        if not condition:
            logger.error('the group condition parameter is empty or none')
            raise MDMiInvalidParameterError(601, 'Invalid Parameter',
                    'condition parameter: %s did not contain "dn", "cn" or "objectguid"' % condition)

        if not kwargs:
            logger.error('the group changed value parameter is empty or none')
            raise MDMiInvalidParameterError(601, 'Invalid Parameter',
                    'do not contain new value for group in parameter: %s' % kwargs)

        # get a key and value from condition
        key, value = self._get_key_value_from_dict(condition)
        if not key:
            logger.error('condition parameter did not contain "dn", "cn" or "objectguid"')
            raise MDMiInvalidParameterError(601, 'Invalid Parameter',
                    'condition parameter: %s did not contain "dn", "cn" or "objectguid"' % condition)

        try:
            if not self.transaction:
                r = self.rest.create_session(object_class='Groups')
                logger.info('metanate operation CREATESESSION for Groups, result: %s', r)

            # to retrieve group from metanate
            rs = self.rest.retrieve()
            rr = None
            for r in rs.content:
                if isinstance(r, tuple) and len(r) == 2 and isinstance(r[1], dict):
                    r1 = self._convert_dict_key_to_lower(r[1])
                    if key == 'dn':
                        if value == r[0]:
                            rr = r
                            break
                    elif r1.has_key(key) and isinstance(r1[key], list) and value in r1[key]:
                        rr = r
                        break

            if not rr:
                logger.error('Can not found group with condition: %s', condition)
                raise MDMiHttpError(404, 'Not Found', 'Can not found group with condition: %s' % condition)

            # do remove group from metanate
            if not self.transaction:
                r = self.rest.remove(dn=rr[0], **rr[1])
                logger.info('metanate operation REMOVE on data: %s, result: %s', rr, r)
            else:
                logger.info('metanate operation REMOVE was in transaction')
                r = self._process_once('remove', 'Groups', dn=rr[0], **rr[1])

            # replace value
            to_dic = self._parse_args_to_dict(kwargs)
            dic = self._parse_args_to_dict(rr[1])
            for k, v in to_dic.iteritems():
                dic[k] = v

            if not dic.has_key('dn'):
                # replace dn
                if rr[1]['cn'] == dic['cn'][0]:
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

            # to add group to metanate
            if not self.transaction:
                r = self.rest.add(**dic)
                logger.info('metanate operation ADD on data %s, result: %s', dic, r)
            else:
                logger.info('metanate operation ADD was in transaction')
                r = self._process_once('add', 'Groups', **dic)

            if not self.transaction:
                r = self.rest.commit()
                logger.info('metanate operation COMMIT, result: %s', r)

            return r
        finally:
            if not self.transaction:
                r = self.rest.close_session()
                logger.info('metanate operation CLOSESESSION, result: %s', r)

    def modify_group_by_name(self, group_name, to_name, members=None):

        """
        modify a group in metanate
        Parameters:
            name: group name, like 'engine test'
        """
        if not group_name:
            logger.error('the group name parameter is empty or none')
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'The group name parameter is empty or none')

        return self._modify_group({'cn': group_name}, cn=to_name, member=members)

    def modify_group_by_dn(self, group_dn, to_name, members=None):

        """
        modify a group in metanate
        Parameters:
            group_dn: group dn, like 'cn=websense019,cn=Users,dc=lb,dc=com'
        """
        if not group_dn:
            logger.error('the group name parameter is empty or none')
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'The group name parameter is empty or none')

        return self._modify_group({'dn': group_dn}, cn=to_name, member=members)

    def modify_group_by_guid(self, object_guid, to_name, members=None):
        """
        modify a group in metanate
        Parameters:
            object_guid: the guid of group , like 'o7PvDTRiSACrzzB2Nt75RA==', this parameter should be in base64 format.
        """
        if not object_guid:
            logger.error('the group name parameter is empty or none')
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'The group name parameter is empty or none')

        return self._modify_group({'objectguid': object_guid}, cn=to_name, member=members)

    def add_airwatch_group(self, cn, **kwargs):
        """
        Deprecated: add an airwatch group into metanate
        Parameters:
            cn: group name like 'dev group'
        """
        return self.replace_airwatch_group(cn, self.generate_guid(), 'add', **kwargs)

    def remove_airwatch_group(self, cn, object_guid):
        """Deprecated: remove an group from metanate
        Parameters:
            cn: cn of group in ldap
            object_guid: the id of the group

        """
        if not cn:
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'cn should not empty or None')

        dic = {'dn': 'cn={cn},cn=Users,dc=awmdm,dc=com'.format(cn=cn),
               'cn': [cn], 'objectclass': ['User'], 'objectguid': [object_guid]}

        return self._process_once('remove', 'Groups', **dic)

    def replace_airwatch_group(self, cn, object_guid, method_name='replace', **kwargs):
        """
        Deprecated: replace an airwatch group in airwatch
        Parameters:
            cn: common name like 'dev group'
        """
        if not cn:
            raise MDMiInvalidParameterError(601, 'Invalid Parameter', 'cn should not empty or None')

        dic = self._parse_args_to_dict(kwargs)

        dn = 'cn={cn},cn=Users,dc=awmdm,dc=com'.format(cn=cn)
        if dic.has_key('cn'):
            if cn not in dic['cn']:
                dic['cn'].append(cn)
        else:
            dic['cn'] = [cn]

        logger.debug(dic)

        return self.replace_group(dn, object_guid, method_name, **dic)
