#!/usr/bin/python
# fileName: hosted_os.py
# encoding=utf-8

import json
import sys
import os
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
from hosted_access import HostedAccess
from utils import logger

HOSTED_OS_OBJECT = '/os/v-%d/account-%d/namespace-%s/object-%s'
HOSTED_OS_SECTION = '/os/v-%d/account-%d/namespace-%s/object-%s/section-%s'

class HostedOS(object):
    """
    this class implements to access hosted OS
    """
    def __init__(self):     
        self.m_wrest = HostedAccess()
        pass

    def get_object(self, objName=None, namespace='mobile', account=1, version=1):
        """
        get an object from OS
        Params:
            objName: Name of the object
            namespace: Name of the namespace
            account: account ID
            version: OS version
        Return:
            Instatnce of RestResult
        """
        try:
            if objName:
                resource = HOSTED_OS_OBJECT % (version, account, namespace, objName)
                logger.debug('Get object from OS - resource:%s' % resource)
                return self.m_wrest.do_access(resource, 'GET', data=None, headers=None)
            else:
                raise Exception('Invalid parameters.')
        except Exception, e:
            logger.error('access hosted OS error: %s' % repr(e))
            raise e

    def get_section(self, secName=None, objName=None, namespace='mobile', account=1, version=1):
        """
        get an section from OS
        Params:
            secName: section name
            objName: Name of the object
            namespace: Name of the namespace
            account: account ID
            version: OS version
        Return:
            Instatnce of RestResult
        """
        try:
            if objName and secName:
                resource = HOSTED_OS_SECTION % (version, account, namespace, objName, secName)
                logger.debug('Get section from OS - resource:%s' % resource)
                return self.m_wrest.do_access(resource, 'GET', data=None, headers=None)
            else:
                raise Exception('Invalid parameters.')
        except Exception, e:
            logger.error('Access hosted OS error: %s' % repr(e))
            raise e 

    def import_object(self, objName=None, namespace='mobile', account=1, version=1, data=None):
        """
        import an object into OS
        Params:
            objName: Name of the object
            namespace: Name of the namespace
            account: account ID
            version: OS version
        Return:
            Instatnce of RestResult
        """
        try:
            if objName:
                resource = HOSTED_OS_OBJECT % (version, account, namespace, objName)
                resource += "/import"
                logger.debug('Import object into OS - resource:%s, data %s' % (resource, data))
                data = json.dumps(data)
                return self.m_wrest.do_access(resource, 'PUT', data=data, headers=None)
            else:
                raise Exception("Invalid parameters.")
        except Exception, e:
            logger.error('Access hosted OS error: %s' % repr(e))
            raise e


    def put_section(self, secName=None, objName=None, namespace='mobile', account=1, version=1, data=None):
        """
        import a section into OS
        Params:
            secName: section name
            objName: Name of the object
            namespace: Name of the namespace
            account: account ID
            version: OS version
        Return:
            Instatnce of RestResult
        """
        try:
            if objName and secName:
                resource = HOSTED_OS_SECTION % (version, account, namespace, objName, secName)
                logger.debug('Put section into OS - resource:%s' % resource)
                data = json.dumps(data)
                return self.m_wrest.do_access(resource, 'PUT', data=data, headers=None)
            else:
                raise Exception("Invalid parameters.")
        except Exception, e:
            logger.error('Access hosted OS error: %s' % repr(e))
            raise e



