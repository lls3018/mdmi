#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import sys
import json
import urllib
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
from utils import logger
from utils.error import MDMiHttpError
from airwatch.base import AirwatchBase

class AirwatchVPNProfile(AirwatchBase):
    def __init__(self, account_id, callback_url=None):
        super(AirwatchVPNProfile, self).__init__(account_id, callback_url)

    def push_vpnprofile(self, callback_url, data, content_type='xml'):
        try:
            proto, rest = urllib.splittype(callback_url)
            host, rest = urllib.splithost(rest)
            resource = callback_url[callback_url.find(host) + len(host) : ]

            if content_type == 'xml':
                self.aw_headers['Content-Type'] = 'application/xml'
            result = self.rest.do_access(resource, "POST", self.parse_param(data), headers=self.aw_headers)
            return True
        except Exception, e:
            error_msg = "push vpn to airwatch error %s" % str(e)
            logger.error(error_msg)
            return error_msg

    def detect_aw(self):
        resource = "/API/v1/mdm"
        return self.rest.do_access(resource, 'GET', None, headers=self.aw_headers)

    def modify(self, profile_id, data=None, method_name='install', http_method='POST'):
        resource = "/API/v1/mdm/profiles/{profileid}/{method}".format(profileid=profile_id, method=method_name)
        try:
            res = self.rest.do_access(resource, http_method, self.parse_param(data), headers=self.aw_headers)
        except MDMiHttpError as e:
            logger.warning("%s vpn profile exception: %s" % (method_name, e))
            return False
        except Exception as e:
            logger.warning("%s vpn profile exception: %s" % (method_name, e))
            return False
        
        return True

    def install_profile_by_deviceid(self, profile_id, device_id):
        data = {"DeviceId": device_id}
        method_name = "install"
        return self.modify(profile_id, data, method_name) 

    def remove_profile_by_deviceid(self, profile_id, device_id):
        data = {"DeviceId": device_id}
        method_name = "remove"
        return self.modify(profile_id, data, method_name)

    def install_profile_by_udid(self, profile_id, udid):
        data = {"Udid": udid}
        method_name = "install"
        return self.modify(profile_id, data, method_name) 

    def remove_profile_by_udid(self, profile_id, udid):
        data = {"Udid": udid}
        method_name = "remove"
        return self.modify(profile_id, data, method_name)
    
    def install_profile_by_serialnumber(self, profile_id, serialnumber):
        data = {"SerialNumber": serialnumber}
        method_name = "install"
        return self.modify(profile_id, data, method_name) 

    def remove_profile_by_serialnumber(self, profile_id, serialnumber):
        data = {"SerialNumber": serialnumber}
        method_name = "remove"
        return self.modify(profile_id, data, method_name) 

    def install_profile_by_macaddress(self, profile_id, macaddress):
        data = {"MacAddress": macaddress}
        method_name = "install"
        return self.modify(profile_id, data, method_name) 

    def remove_profile_by_macaddress(self, profile_id, macaddress):
        data = {"MacAddress": macaddress}
        method_name = "remove"
        return self.modify(profile_id, data, method_name) 

if __name__ == '__main__':
    logger.debug("Call back sevice request start")
    vpn = AirwatchVPNProfile(96, 'https://127.0.0.1/cgi-py/installvpn.py')
    data = {"UserName": "test",
            "Password": "123",
            "Name": "test"
            }

    req = vpn.push_vpnprofile('https://127.0.0.1/cgi-py/installvpn.py', json.dumps(data))
    logger.debug("Call back sevice response is %s" % req)
    logger.debug("Call back sevice request end")

    vpn = AirwatchVPNProfile(87, None)
    res = vpn.install_profile_by_deviceid(37, 1)
    # res = vpn.remove_profile_by_deviceid(37, 1)
    logger.debug(res)
