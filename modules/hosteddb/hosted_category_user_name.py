#!/usr/bin/env python
#-*- encoding:UTF-8 -*-

import json
import sys

from hosted_access import HostedAccess
from utils import logger

if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')


class Hosted_category_user_name(object):
    def __init__(self):
        self.m_wrest = HostedAccess()
        pass

    def get_category_user(self, category_id, hosted_user='HostedUsers', account=1, version=1):
        '''
        Get an object from category service
        Params:
            category: category ID
            version: category service version
        Return:
            Instatnce of RestResult
        '''
        try:
            if category_id:
                resource = '/ug/v-%d/%s?a=[%s]' % (version, hosted_user, category_id)
                logger.debug('Get category info from category service - resource: %s' % resource)
                return self.m_wrest.do_access(resource, 'GET', data=None, headers=None)
            else:
                raise Exception('Invalid parameters')
        except Exception as e:
            logger.error('Access category service error, error: %s' % repr(e))
            raise e
    """
    def delete_category_user(self, category_id, hosted_user='HostedUsers', account=1, version=1):
        '''
        remove category user
        Params:
            category: category ID
            version:  category service version
        Return:
            Instatnce of RestResult
        '''
        try:
            if category_id:
                resource = '/ug/v-%d/%s?a=[%s]' % (version, hosted_user, category_id)
                logger.debug('Delete category from category service - resource: %s', resource)
                return self.m_wrest.de_access(resource, 'DELETE', data=None, headers=None)
            else:
                raise Exception('Invalid params')
        except Exception as e:
            logger.error('Access vategory service error: %s', repr(e))
            raise e
    """

if __name__ == '__main__':
    category = Hosted_category_user_name()
    category.get_category_user('110')

