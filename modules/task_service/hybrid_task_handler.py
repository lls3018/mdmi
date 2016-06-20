#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------------------------------
# File Name:
# Purpose:
# Creation Date: 09-01-2014
# Last Modified: Mon Mar 10 22:00:06 2014
# Created by:
#---------------------------------------------------

import sys
if not '/opt/mdmi/modules' in sys.path:
    sys.path.append('/opt/mdmi/modules')
import json

from utils import logger
from hybrid_access import HybridAccess
from task_handler import TaskHandler

from service_variables import g_service_status
from service_variables import g_task_dict

class HybridTaskHandler(TaskHandler):
    def __init__(self, key, task, index):
        super(self.__class__, self).__init__('hybrid', key, task, index)
        self._index = index

    def _pre_handle(self):
        logger.debug('hybrid task handler pre_handle function, handler: %s, task key: %s', self.name, self._key)
        g_service_status.increase_invoke_thread_number(self._index)

    def _do_handle(self):
        logger.debug('hybrid task handler do_handle function, handler: %s, task key: %s', self.name, self._key)
        tasks = []
        task_length = 0
        for content in self._task:
            try:
                if isinstance(content, basestring):
                    t = json.loads(content)
                    if isinstance(t, (list, tuple, set)):
                        tasks.extend(t)
                        task_length += len(t)
                    else:
                        tasks.append(t)
                        task_length += 1
                elif isinstance(content, dict):
                    tasks.append(content)
                    task_length += 1
            except Exception as e:
                logger.error('exception occurred in %s when parse task to json format: %s, %s', self.name, content, e)

        if not tasks:
            return
        logger.debug("hybrid task handler handled %d tasks in %s", task_length, self.name)

        account = tasks[0]['account']
        data = [t['parameters'] for t in tasks]
        # todo: modify g_service_status
        # g_service_status.increase_hybrid_user_number(self._index, task_length)
        # use xrange(2) just for batch commit twice if the first batch commit failed
        try:
            r = HybridAccess(account).add_multi_users(data)
        except Exception, e:
            logger.error('%s send request to hss server failed, task key: %s, tasks: %s', self.name, self._key, tasks)
            logger.error('%s send request to hss server failed, account: %s, task number: %d, exception: %s',
                    self.name, account, task_length, e)
            # retry committing after 1 ~ 10 seconds
            g_task_dict.put_retry(self._key, tasks)
        else:
            logger.info('%s send request to hss server success, task key is: %s, task number: %d', self.name, self._key, task_length)
            if r.code == 200:
                g_service_status.increase_user_success_number(self._index, task_length)
            else:
                g_task_dict.put_retry(self._key, tasks)
    # END def _do_handle

    def _post_handle(self):
        logger.debug('hybrid task handler post_handle function, handler: %s, task key: %s', self.name, self._key)
