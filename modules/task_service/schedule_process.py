#!/usr/bin/python
#-*- coding: utf-8 -*-

#---------------------------------------------------
# File Name: schedule_process.py
# Purpose:
# Creation Date: 09-01-2014
# Last Modified: Fri Feb 14 00:50:40 2014
# Created by:
#---------------------------------------------------

from threading import Thread, Event, Condition

import sys
if not '/opt/mdmi/modules' in sys.path:
    sys.path.append('/opt/mdmi/modules')

from utils import logger
from service_variables import g_task_cache
from service_variables import g_task_dict

class ScheduleProcess(Thread):
    def __init__(self, dispatcher):
        super(self.__class__, self).__init__()
        self.__stop_event = Event()
        self.__condition = Condition()
        self.__dispatcher = dispatcher

        self.__stop_event.clear()

    def run(self):
        logger.info('schedule thread is running...')
        while not self.__stop_event.isSet():
            try:
                self.__condition.acquire()
                self.__condition.wait(5)
            except Exception:
                pass
            else:
                if not g_task_cache.is_empty():
                    task_data_list = g_task_cache.get_all()
                    if task_data_list:
                        logger.info('get some tasks from task cache')
                        for data in task_data_list:
                            logger.info('get a task from task cache: %s', data)
                            g_task_dict.put(data['key'], data['value'])
                    self.__dispatcher.notify()
                    g_task_cache.notify()
            finally:
                self.__condition.release()

        logger.info('schedule thread %s stopped', self.name)

    def stop(self):
        logger.info('stopping schedule thread %s...', self.name)
        self.__stop_event.set()
        self.__condition.acquire()
        self.__condition.notify()
        self.__condition.release()
