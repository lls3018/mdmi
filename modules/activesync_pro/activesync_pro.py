#!/usr/bin/env python2.6

import sys
import base64
import common
import grouping
from error import *
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
from utils import logger

class ActivesyncEventProcessor(object):
    def __init__(self):
        self.asamc = grouping.ASAMemcache()
        pass

    def __del__(self):
        del self.asamc
        pass

    def handle(self, username, src_ip):
        if self.asamc.ip_is_incache(src_ip):
            logger.debug("Device from %s is already in the handle progress, ignore it!" % (src_ip))
            return 0

        logger.debug('Device from %s will be processed' % (src_ip))

        #get serial number from username and decrypt it
        encrypted_serialnum = username.upper()
        passKey = common.getPassKeyFromConfig()
        logger.debug('GET passKey:%s' % passKey)
        #serial_num = common.decryptPasswd(base64.b32decode(encrypted_serialnum), passKey)
        serial_num = base64.b32decode(encrypted_serialnum)

        if not serial_num:
            self.asamc.memcache_delete(src_ip)
            logger.error('Could not get device serial number!')
            return 1

        dev_owner,account_id, mdm_profile_id = common.get_device_info(serial_num)
        user_type = common.get_user_object_class(dev_owner, account_id)

        if not dev_owner:
            self.asamc.memcache_delete(src_ip)
            logger.error('Could not find the owner of the device!')
            return 2
        whitelists = common.get_activesync_whitelists(account_id, user_type)
        if (True == common.srcip_allowed(src_ip, whitelists)):
            logger.debug('ip is allowed')
            return 3
        else:
            logger.debug('will push vpn profile')
            ret = common.repush_profile(account_id, serial_num, mdm_profile_id)
            if ret == 1:
                self.asamc.memcache_delete(src_ip)
            return 0

if __name__ == "__main__":
    if (len(sys.argv) is not 3 and len(sys.argv) is not 4):
        raise ActiveSyncInputInvalid('Data invalid from zpush!')

    username = sys.argv[1]
    src_ip = sys.argv[2]

    private_ip = '10.250.70.111'
    if src_ip == private_ip:
        logger.debug('username: %s. Connection is coming from VPN server, will not repush VPN profile' % username)
        exit(0)


    aep = ActivesyncEventProcessor()
    aep.handle(username, src_ip)
