#!/usr/bin/python
# fileName: hosted_os.py
# encoding=utf-8

import json
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
from hosted_access import HostedAccess
from utils import logger

class HostedAPP(object):
    """
    this class implements to access hosted app service
    """
    def __init__(self):     
        self.m_wrest = HostedAccess()
        pass

    def get_appinfo(self, app_id, account=1, version=1):
        """
        get an object from app service
        Params:
            account: account ID
            version: app service version
        Return:
            Instatnce of RestResult
        """
        try:
            if app_id:
                resource = "/appservice/v-%d/app/%s" % (version, app_id)
                logger.debug('Get app info from app service - resource:%s' % resource)
                return self.m_wrest.do_access(resource, 'GET', data=None, headers=None)
            else:
                raise Exception('Invalid parameters.')
        except Exception, e:
            logger.error('access app service error  error: %s' % repr(e))
            raise e

    def search_app(self, search_param, account=1, version=1):
        """
        get an section from app service
        Params:
            search_param: dict, query parameters
            account: account ID
            version: app service version
        Return:
            Instatnce of RestResult
        """
        try:
            resource = "/appservice/v-%d/search" % (version)
            data = json.dumps(search_param)
            logger.debug('search app info from app service - resource:%s' % resource)
            return self.m_wrest.do_access(resource, 'POST', data=data, headers=None)
        except Exception, e:
            logger.error('Access app service error: %s' % repr(e))
            raise e 

    def delete_app(self, app_id, account=1, version=1):
        """
        import a section into app service
        Params:
            app_id: String application id
            account: account ID
            version: app service version
        Return:
            Instatnce of RestResult
        """
        try:
            if app_id:
                resource = "/appservice/v-%d/app/%s" % (version, app_id)
                logger.debug('delete app from app service - resource:%s' % resource)
                return self.m_wrest.do_access(resource, 'DELETE', data=None, headers=None)
            else:
                raise Exception("Invalid parameters.")
        except Exception, e:
            logger.error('Access app service error: %s' % repr(e))
            raise e

if __name__ == "__main__":
    app = HostedAPP()
    print app.get_appinfo("110")

