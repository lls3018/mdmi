#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------------------------------
# File Name: task_handler.py
# Purpose:
# Creation Date: 08-01-2014
# Last Modified: Fri Mar  7 03:10:24 2014
# Created by:
#---------------------------------------------------

import sys
if not '/opt/mdmi/modules' in sys.path:
    sys.path.append('/opt/mdmi/modules')

from utils import logger

class TaskHandler(object):
    def __init__(self, handler_type, key, task, index):
        self._handler_type = handler_type
        self._key = key
        self._task = task
        self._index = index
        
        self.name = '%s-task-handler-thread-%d' % (self._handler_type, self._index)
        logger.info('%s is ready to handle task, task key is: %s', self.name, self._key)

    def _pre_handle(self):
        pass

    def _do_handle(self):
        pass

    def _post_handle(self):
        pass
    
    def do_handle(self):
        self._pre_handle()
        self._do_handle()
        self._post_handle()
        