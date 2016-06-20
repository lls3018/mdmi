#! /usr/bin/python
#!/usr/bin/env python2.6
# encoding=utf-8

# # @package ods-mdmi-tools
#  Implementation of the tool for inserting account attribute for old device.
#  @file aw_dev_account_ins.py
#  @brief Start the tool with input params
#  @author xfan@websense.com

import sys
import time
import Queue
sys.path.append("/opt/mdmi/modules/")
from utils import logger
from tools_base import DeviceSyncThread
from hosteddb.hosted_account import HostedAccount
from hosteddb.hosted_device import HostedDevice

class AW_DeviceAccountAttrInsHandler(DeviceSyncThread):
    def __init__(self):
        self.dev_update_queue = Queue.Queue()
        super(AW_DeviceAccountAttrInsHandler, self).__init__()
        pass

    def run(self):
        logger.info('Step 1: Get devices from RS!')
        self._get_devinfo_from_rs()
        # pick out device without account attribute
        while (self.devinfo_original_queue.qsize() > 0) :  # make sure the queue is not empty
            devlist = self.devinfo_original_queue.get(True)  # get by block
            for dev in devlist:
                has_account = dev['attributes'].get('account', False)
                if has_account == False:
                    self.dev_update_queue.put(dev)
        logger.info('%d devices need to be inserted with account attribute!' % self.dev_update_queue.qsize())

        logger.info('Step 2: Insert account attribute!')
        self._account_ins()
        pass

    def stop(self):
        pass

    def _get_devinfo_from_rs(self):
        #get all devices from rs
        return super(AW_DeviceAccountAttrInsHandler, self)._get_devinfo_from_rs(100, )
        pass

    def _account_ins(self):
        cnt_need_update = self.dev_update_queue.qsize()
        if (cnt_need_update == 0):
            return cnt_need_update
        cnt_result = 0

        while (self.dev_update_queue.qsize() > 0):  # make sure the queue is not empty
            dev = self.dev_update_queue.get(True)  # get by block
            try:
                owner = dev['attributes'].get('deviceOwner', [''])[0]
                udid = dev['attributes'].get('UDID', [''])[0]
                if len(owner) > 0:
                    aidobj = HostedAccount()
                    account = aidobj.get_account_id(**{'objectClass':'hostedUser', 'mail' : owner}) #only hosted user for MDMi
                    if account:
                        devobj = HostedDevice(udid)
                        data = devobj.format_update_data(None, 'replace', account=account[0])
                        result = devobj.do_update(attributes=data)
                        del devobj
                        if result.code >= 200 and result.code < 300:
                            cnt_result = cnt_result + 1
                    del aidobj
            except Exception, e:
                logger.error('Insert account error:%s' % repr(e))
                pass
        logger.info('Insert account attribute total %d device,  %d device ok' % (cnt_need_update, cnt_result))
        pass

def _get_handler():
    handlers = []
    handler = AW_DeviceAccountAttrInsHandler()
    handlers.append(handler)
    return handlers
    pass

if __name__ == '__main__':
    logger.info('Devices\' account attribute insert started at %s!' % str(time.time()))
    # step 0: Init
    handlers = _get_handler()
    
    # step 1: Working
    if handlers:
        for handle in handlers:
            handle.start()
    
    # step 2: finsh
    if handlers:
        for handle in handlers:
            handle.join()
    logger.info('Devices\' account attribute insert end at %s!' % str(time.time()))

