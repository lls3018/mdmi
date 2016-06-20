#!/usr/bin/python
#-*- coding: utf-8 -*-

#---------------------------------------------------
# File Name: service_config.py
# Purpose:
# Creation Date: 06-03-2014
# Last Modified: Thu Mar  6 02:01:35 2014
# Created by:
#---------------------------------------------------

from multiprocessing import Value
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')

from utils.configure import MDMiConfigParser
from utils.configure import MDMI_CONFIG_FILE

from utils import logger

g_config_thread_pool_min_size = Value('i', 4)
g_config_thread_pool_max_size = Value('i', 32)
g_config_thread_kill_idle_each_time = Value('i', 1)

SECTION_KEY = 'task-service'
THREAD_POOL_MAX_SIZE = 'thread_pool_max_size'

def reload_config():
    try:
        reader = MDMiConfigParser(MDMI_CONFIG_FILE, False)
        v = reader.read(SECTION_KEY, THREAD_POOL_MAX_SIZE)
        v=v[0]
        to_value = int(v[1])
        if v[0] == THREAD_POOL_MAX_SIZE:
            if to_value < (g_config_thread_pool_min_size.value << 1):
                logger.warning('the max pool size is smaller than double of min size, change it to double size of min size')
                to_value = g_config_thread_pool_min_size.value << 1
            if to_value != g_config_thread_pool_max_size.value:
                logger.info('thread pool size changed from %d to %d', g_config_thread_pool_max_size.value, to_value)
            g_config_thread_pool_max_size.value = to_value
    except Exception as e:
        logger.warning('error occurred: %s', e)
