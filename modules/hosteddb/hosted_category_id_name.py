#!/usr/bin/env python
#FileName: hosted_category_id_name.py
#-*- encoding: UTF-8 -*-

import sys
import json
from hosted_access import HostedAccess
from utils import logger

if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')

class Hosted_category_id_name(object):
    def __init__(self):
        self.m_wrest = HostedAccess()
        pass

    def get_category_ID(self, category_id, category_dirname='Category', account=1, version=1):
        '''
        Get an object from category server
        Params:
            Category: category ID
        Return:
            Instatnce of RestResult
        '''

        try:
            if category_id:
                resource = "/ug/v-%d/%s?a=[%s]" % (version, category_dirname, category_id)
                logger.debug('Get category info from category service - resource: %s' % resource)
                return self.m_wrest.do_access(resource, 'GET', data=None, headers=None)
            else:
                raise Exception("Invalid parameters")
        except Exception as e:
            logger.error("Access category service error, error: %s", repr(e))
            raise e
    """  
    def delete_category_ID(self, category_id, category_dirname='Category', account=1, version=1):
        '''
        remove a category
        Params:
            category_id: category ID
            version: category service version
        Return:
            Instatnce of RestResult
        '''

        try:
            if category_id:
                resource = '/ug/v-%d/%s?a=[%s]' % (version, catgory_dirname, catefory_id)
                logger.debug('Delete category from category service - resource: %s', resource)
                return self.m_wrest.do_access(resource, "DELETE", data=None, headers=None)
            else:
                raise Exception("Invalid parameters")
        except Exception as e:
            logger.error('Access category service error, error: %s', repr(e))
            raise e
    """

if __name__ == '__main__':
    category = Hosted_category_id_name()
    category.get_category_ID('110')

