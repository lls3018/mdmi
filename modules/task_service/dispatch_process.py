#!/usr/bin/python
#-*- coding: utf-8 -*-

#---------------------------------------------------
# File Name: dispatch_thread.py
# Purpose:
# Creation Date: 08-01-2014
# Last Modified: Sun Mar  2 17:45:15 2014
# Created by:
#---------------------------------------------------

from threading import Thread, Event

import sys
if not '/opt/mdmi/modules' in sys.path:
    sys.path.append('/opt/mdmi/modules')

from utils import logger

from task_handler_pool import TaskHandlerPool
from service_variables import g_task_dict

class DispatchProcess(Thread):
    def __init__(self, queue):
        super(self.__class__, self).__init__()
        self.__task_handler_pool = TaskHandlerPool()
        self.__event = Event()
        self.__stop_event = Event()
        self.__queue = queue
        self.__cur_tasks = None

        self.__stop_event.clear()
        self.name = 'DispatchProcess'
        logger.info('dispatch thread %s is ready to run...', self.name)

    def run(self):
        logger.info('dispatch thread is running...')
        while not self.__stop_event.isSet():
            try:
                self.__event.wait(timeout=5)
            except Exception:
                pass
            else:
                if self.__cur_tasks:
                    if self._run_tasks():
                        self.__event.set()
                    else:
                        self.__event.clear()
                else:
                    self.__cur_tasks = g_task_dict.get()
                    if not self.__cur_tasks:
                        self.__task_handler_pool.kill_idle_handlers()
                        self.__event.clear()
                        continue
                    if self._run_tasks():
                        self.__event.set()
                    else:
                        self.__event.clear()
            finally:
                pass
        logger.info('dispatch thread %s stopped', self.name)

    def stop(self):
        logger.info('stopping dispatch thread %s...', self.name)
        self.__stop_event.set()
        #if not self.__busy.isSet():
        self.__event.set()

        self.__task_handler_pool.kill_all_handlers()

    def notify(self):
        self.__event.set()

    def _run_tasks(self):
        while self.__cur_tasks:
            key, value = self.__cur_tasks.popitem()
            logger.info('active a thread to handle task: %s', key)
            logger.debug('task content is: %s', value)
            try:
                if not self.__task_handler_pool.make_thread_to_handle_task(key, value):
                    self.__cur_tasks[key] = value
                    return False
            except Exception as e:
                logger.error('error occurred in dispatch: %s', e)
                self.__cur_tasks[key] = value
                return False

        return True
