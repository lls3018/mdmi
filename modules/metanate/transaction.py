# -*- coding: utf-8 -*-
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')

from utils import logger

from metanate.mrest_access import MRESTAccess

TRANS_USER = 'Users'
TRANS_GROUP = 'Groups'

class begin(object):
    def __init__(self, account_id, trans_object, rest=None, host=None, port=443):
        self.account_id = account_id
        self.trans_object = trans_object
        if rest:
            self.rest = rest
        else:
            self.rest = MRESTAccess(account_id, host, port)

    def __enter__(self):
        r = self.rest.create_session(object_class=self.trans_object)
        logger.info('metanate operation CREATESESSION in transaction: %s', r)

        return self

    def __exit__(self, type, value, trackback):
        r = self.rest.close_session()
        logger.info('metanate operation CLOSESESSION in transaction: %s', r)

    def commit(self, o):
        o._operate_rest_info()
        r = self.rest.commit()
        logger.info('metanate operation COMMIT in transaction: %s', r)

        return r
