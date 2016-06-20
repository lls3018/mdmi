#! /usr/bin/python
#!/usr/bin/env python2.6
# encoding=utf-8

# # @package ods-mdmi-tools
#  Implementation of the tool for device information sync
#  @file tools_dev_daily_sync.py
#  @brief Start the tool with input params
#  @author xfan@websense.com

import os
import sys
import time
sys.path.append("/opt/mdmi/modules/")
from utils import logger
from aw_dev_daily_sync import AW_DeviceSyncController

def _get_handler():
    handlers = []
    handler = AW_DeviceSyncController()
    handlers.append(handler)
    return handlers
    pass

if __name__ == '__main__':

    #estimate localhost is master
    result =  os.path.exists('/etc/sysconfig/mes.primary')
    if result:
        logger.info('Devices\' information sync started at %s!' % str(time.time()))
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
        logger.info('Devices\' information sync end at %s!' % str(time.time()))
    else:
        logger.info('localhost is not master')

