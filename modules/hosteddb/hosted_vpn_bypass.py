#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
from utils import logger
from hosted_access import HostedAccess

class HostedVpnInfo(object):
    def __init__(self):
        self.m_wrest = HostedAccess()
        pass

    def get_vpninfo(self, account_id, version=1, name='LocalNetworkAccessKey+LocalNetworkAccessValue'):
        '''
        Get an object from VPN server
        Params:
            account_id: account id
            version: VPN server version
        Return:
            Instance of Restresult
        '''
        try:
            if account_id:
                resource = '/rs/v-%d/account-%s?attributes=%s' % (version, account_id, name)
                logger.debug("Get vpn info from service - resource: %s" % resource)
                result = self.m_wrest.do_access(resource, "GET", data=None, headers=None)
                return result
            else:
                raise Exception("Invalid parameters")
        except Exception as e:
            logger.info("access vpn info error: %s" % repr(e))
            return []

    def search_vpninfo(self, search_param, version=1):
        '''
        Get an section from VPN server
        Params:
            search_param: dict, query parameters
            version: VPN server version
        Return:
            instance of RestResult
        '''
        try:
            resource = "/rs/v-%d/search" % version
            data = json.dumps(search_param)
            logger.debug("Search vpn info from service - resource: %s:" % resource)
            return self.m_wrest.do_access(resource, "POST", data=data, headers=None)
        except Exception as e:
            logger.error("Access vpn service error: %s" % repr(e))
            raise e


if __name__ == "__main__":
    vpn_bypass = HostedVpnInfo()
    print vpn_bypass.get_vpninfo("106")

