#!/usr/bin/env python2.6
# encoding=utf-8

# # @package pkeypoolservice
#  Implementation of private key pool service. 
#  The service in order to generate private keys for other services(For example, VPN profile generation service).
#  @file defs.py
#  @brief Defines default value for the service.
#  @author xfan@websense.com

import os

# #Default timeout value for require private keys.
KEYPL_DEFAULT_TIMOUT = 10
# #Default timeout value for recv data.
KEYPL_RECV_TIMOUT = 1
# #Default host name for the private key pool service.
KEYPL_DEFAULT_HOST = 'localhost'
# #Default port for the private key pool service.
KEYPL_DEFAULT_PORT = 30000
# #Max connections allowed to be accepted.
KEYPL_DEFAULT_ACCPECT_LIMIT = 1024
# #Default max value of every list for creators.
KEYPL_MAX_CNT = 500
# #The limitation of the cpu usage.
KEYPL_CPU_LIMIT = 70.0
# #Default idle period for generating private keys.
KEYPL_DEFAULT_GEN_PERIOD = 5  # second

# #Multiple of the max items in queue.
KEYPL_MULTIPLE_QUEUES = 2  # value must >= 1
# #Default specific creators, >= 1
KEYPL_DEFAULT_CREATORS_CNT = 1
# #Default items in the shared private key queue.
KEYPL_DEFAULT_ITEMS_IN_QUEUE = 5  # takes place the (KEYPL_MULTIPLE_QUEUES * KEYPL_DEFAULT_CREATORS_CNT) while the items too small

# #Default folder to hold the private key files.
KEYPL_DEFAULT_DIR = os.path.dirname(os.path.realpath(__file__)) + '/keys/'

# #Control commands
KEYPL_CMDS = {'alive':0, 'qsize':1, 'remain_keys':2}

# #Configure for client.
KPLS_REQ_MAX = 100


