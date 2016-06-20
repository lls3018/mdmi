#! /usr/bin/python
# fileName: tq_initializer.py
#encoding=utf-8

import json
import sys
sys.path.append("/opt/mdmi/modules")
from utils import logger
from hosteddb.hosted_taskqueue import HostedTaskQueue
from taskutils import TaskQueueUtils
from defs import TQ_SETUP_TAB

if __name__ == '__main__':
    try:
        obj = TaskQueueUtils(TQ_SETUP_TAB)
        obj.init_task_queue()
        sys.exit(0)
    except Exception, e:
        logger.error('init task queue failed')
        logger.error(e)
        sys.exit(1)
