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
import time
import random
import base64

from utils import logger
from metanate.user import MetanateUser
from metanate.group import MetanateGroup
from metanate import transaction
from task_handler import TaskHandler

from service_variables import g_service_status
from service_variables import g_task_dict

class MetanateTaskHandler(TaskHandler):
    def __init__(self, key, task, index):
        super(self.__class__, self).__init__('metanate', key, task, index)
        self._index = index

    def _pre_handle(self):
        logger.debug('metanate task handler pre_handle function, handler: %s, task key: %s', self.name, self._key)
        g_service_status.increase_invoke_thread_number(self._index)

    def _do_handle(self):
        logger.debug('metanate task handler do_handle function, handler: %s, task key: %s', self.name, self._key)
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
                # elif isinstance(content, (list, tuple, set)):
                #    tasks.extend(t)
            except Exception as e:
                logger.error('exception occurred in %s when parse task to json format: %s, %s', self.name, content, e)

        if not tasks:
            return
        logger.debug("metanate task handler handled %d tasks in %s", task_length, self.name)

        account = tasks[0]['account']
        trans_type = tasks[0]['trans_type']
        if trans_type == transaction.TRANS_USER:
            g_service_status.increase_user_number(self._index, task_length)
        else:
            g_service_status.increase_group_number(self._index, task_length)
        # use xrange(2) just for batch commit twice if the first batch commit failed
        for i in xrange(2):
            try:
                self._batch_commit(tasks)
            except Exception, e:
                logger.error('metanate transaction failed in %s, task key: %s, task: %s', self.name, self._key, tasks)
                logger.error('metanate transaction failed in %s, times: %d, account:%s, trans_type: %s, task number: %d, exception: %s',
                        self.name, i, account, trans_type, task_length, e)
                # retry committing after 1 ~ 10 seconds
                if i == 1:  # failed twice
                     # self._one_by_one_commit(tasks)
                     g_task_dict.put_retry(self._key, tasks)
                else:
                    time.sleep(random.random() * 5)
            else:
                logger.info('metanate transaction success in %s, task key is: %s, task number: %d', self.name, self._key, task_length)
                if i == 0:
                    if trans_type == transaction.TRANS_USER:
                        g_service_status.increase_user_success_number(self._index, task_length)
                    else:
                        g_service_status.increase_group_success_number(self._index, task_length)
                break
    # END def _do_handle

    def _batch_commit(self, tasks):
        account = tasks[0]['account']
        trans_type = tasks[0]['trans_type']
        with transaction.begin(account, trans_type) as tx:
            metanate_object = None
            if trans_type == transaction.TRANS_USER:
                metanate_object = MetanateUser(account, tx)
            else:
                metanate_object = MetanateGroup(account, tx)
            logger.info('do transaction in %s for account: %s, trans_type: %s', self.name, account, trans_type)
            executed_funcs = []
            for task in tasks:
                logger.info('%s, function name: %s, parameters: %s', self.name, task['func'], task['parameters'])
                if 'objectguid' in task['parameters'] and task['parameters']['objectguid']:
                    try:
                        task['parameters']['objectguid'] = base64.b64decode( task['parameters']['objectguid'])
                    except Exception:
                        logger.warn('objectguid is not base64 encoded')
                func_params = (task['func'], task['parameters'])
                if func_params in executed_funcs:
                    logger.info('the same request has executed and ignore this time')
                    continue

                func = getattr(metanate_object, task['func'])
                func(**task['parameters'])
                logger.info('submitted metanate request')

                executed_funcs.append(func_params)
            # END for

            tx.commit(metanate_object)
            logger.info('metanate transaction is done')
        # END with
    # END def _batch_commit

    def _one_by_one_commit(self, tasks):
        account = tasks[0]['account']
        trans_type = tasks[0]['trans_type']
        logger.info('submit one by one for account: %s, trans_type: %s' % (account, trans_type))
        logger.info('submit one by one for account: %s' % tasks)
        executed_funcs = []
        for task in tasks:
            metanate_object = None
            if trans_type == transaction.TRANS_USER:
                metanate_object = MetanateUser(account)
            else:
                metanate_object = MetanateGroup(account)
            try:
                logger.info('function name: %s. parameters: %s' % (task['func'], task['parameters']))
                if 'objectguid' in task['parameters'] and task['parameters']['objectguid']:
                    try:
                        task['parameters']['objectguid'] = base64.b64decode( task['parameters']['objectguid'])
                    except Exception:
                        logger.warn('objectguid is not base64 encoded')
                func_params = (task['func'], task['parameters'])
                if func_params in executed_funcs:
                    logger.info('the same request has execute and ignore this time')
                    continue

                func = getattr(metanate_object, task['func'])
                func(**task['parameters'])
                executed_funcs.append(func_params)
            except Exception, e:
                logger.error('metanate failed in one by one in %s, account: %s, trans_type: %s, parameters: %s, exception: %s',
                        self.name, account, trans_type, task['parameters'], e)
            else:
                logger.info('finished in metanate one by one task in %s and task is: %s', self.name, task)
                if trans_type == transaction.TRANS_USER:
                    g_service_status.increase_user_success_number(self._index)
                else:
                    g_service_status.increase_group_success_number(self._index)
        # END for
    # END def _one_by_one_commit

    def _post_handle(self):
        logger.debug('metanate task handler post_handle function, handler: %s, task key: %s', self.name, self._key)
