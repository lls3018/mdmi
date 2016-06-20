# -*- coding: utf-8 -*-
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')

import uuid

from metanate.mrest_access import MRESTAccess
from utils import logger

class MetanateBase(object):
    def __init__(self, account_id, transaction=None, host=None, port=443):
        self.account_id = account_id
        self.additions = []
        self.replacements = []
        self.removes = []
        self.transaction = transaction
        if transaction:
            self.rest = transaction.rest
        else:
            self.rest = MRESTAccess(account_id, host, port)

    def __del__(self):
        try:
            if self.rest:
                del self.rest
        except Exception as e:
            logger.error("exception in defining variable: %s", e)

    def generate_guid(self):
        """generate an ObjectGUID by uuid package.
        """
        return str(uuid.uuid4())

    def _process_once(self, method_name, users_or_groups='Users', sync_source='MDM', **kwargs):
        if self.transaction:
            logger.info('metanate transaction operation %s on data: %s', method_name.upper(), kwargs)
            if method_name == 'add':
                self.additions.append(kwargs)
                target = self.additions
            elif method_name == 'replace':
                self.replacements.append(kwargs)
                target = self.replacements
            elif method_name == 'remove':
                self.removes.append(kwargs)
                target = self.removes
            elif method_name == 'retrieve':
                r = self.rest.retrieve()
                return r
            else:
                return None

            # do add, replace or remove user or group operation
            # r = self.rest.add(**kwargs)
            if len(target) >= 32:  # TODO the value 32 should be discussed
                logger.info('metanate transaction operation on %s has exceeded 32, do operation for these data', users_or_groups)
                if self.removes:
                    r = self.rest.remove_list(self.removes)
                    logger.info("metanate transaction operation REMOVE for %d %s: %s", len(self.removes), users_or_groups, r)
                    del self.removes[:]
                if self.replacements:
                    r = self.rest.repalce_list(self.replacements)
                    logger.info("metanate transaction operation REPLACE for %d %s: %s", len(self.replacements), users_or_groups, r)
                    del self.replacements[:]
                if self.additions:
                    r = self.rest.add_list(self.additions)
                    logger.info("metanate transaction operation ADD for %d %s: %s", len(self.additions), users_or_groups, r)
                    del self.additions[:]

                return r

            return target

        try:
            # create a session if it not in transaction
            r = self.rest.create_session(object_class=users_or_groups, sync_source=sync_source)
            logger.info('metanate operation CREATESESSION: %s on SyncSource: %s', r, sync_source)
            # do add, replace or remove user or group operation
            rr = getattr(self.rest, method_name)(**kwargs)
            logger.info('metanate operation %s: %s', method_name.upper(), r)

            r = self.rest.commit()
            logger.info('metanate operation COMMIT: %s', r)

            if method_name == 'retrieve':
                return rr
            else:
                return r
        finally:
            try:
                r = self.rest.close_session()
                logger.info('metanate operation CLOSESESSION: %s', r)
            except Exception as e:
                # do not need to log in level ERROR, just debug.
                logger.debug('metanate operation CLOSESESSION error: %s', e)

    def _operate_rest_info(self):
        # TODO these results should be cared
        r = None
        if self.replacements:
            r = self.rest.replace_list(self.replacements)
        if self.removes:
            r = self.rest.remove_list(self.removes)
        if self.additions:
            r = self.rest.add_list(self.additions)

        return r

    def _parse_args_to_dict(self, kwargs):
        dic = {}
        for k, v in kwargs.iteritems():
            if v:
                if dic.has_key(k.lower()):
                    if isinstance(v, list) or isinstance(v, tuple):
                        dic[k.lower()].extend(v)
                    else:
                        dic[k.lower()].append(v)
                else:
                    if isinstance(v, list) or isinstance(v, tuple):
                        dic[k.lower()] = list(v)
                    else:
                        dic[k.lower()] = [v]

        return dic

    def _convert_dict_key_to_lower(self, d, append_to_list=False):
        dic = {}
        for k, v in d.iteritems():
            if v:
                if dic.has_key(k.lower()):
                    if append_to_list:
                        if isinstance(dic[k], list):
                            dic[k].append(v)
                        else:
                            dic[k] = [dic[k], v]
                else:
                    dic[k.lower()] = v

        return dic

    def _get_key_value_from_dict(self, kwargs):
        dic = self._convert_dict_key_to_lower(kwargs)
        if dic.get('objectguid'):
            key = 'objectguid'
            value = dic.get('objectguid')
        elif dic.get('dn'):
            key = 'dn'
            value = dic.get('dn')
        elif dic.get('mail'):
            key = 'mail'
            value = dic.get('mail')
        elif dic.get('cn'):
            key = 'cn'
            value = dic.get('cn')
        else:
            key = None
            value = None

        return key, value
