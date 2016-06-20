#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------------------------------
# File Name: task_thread_pool.py
# Purpose:
# Creation Date: 08-01-2014
# Last Modified: Thu Mar  6 22:30:34 2014
# Created by:
#---------------------------------------------------

from threading import Lock

import sys
if not '/opt/mdmi/modules' in sys.path:
    sys.path.append('/opt/mdmi/modules')

from utils import logger

from service_config import g_config_thread_pool_max_size
from service_config import g_config_thread_pool_min_size
from service_config import g_config_thread_kill_idle_each_time

from task_handler_thread import TaskHandlerThread
from metanate_task_handler import MetanateTaskHandler
from hybrid_task_handler import HybridTaskHandler

task_handler_classes = {
        'metanate': MetanateTaskHandler,
        'hybrid': HybridTaskHandler,
    }

class TaskHandlerFactory:
    @classmethod
    def create_handler(cls, handler_type):
        global task_handler_classes
        if not handler_type in task_handler_classes:
            handler_type = 'metanate'
        clazz = task_handler_classes.get(handler_type)
        return clazz

class TaskHandlerPool:
    def __init__(self):
        self.__cur_threads = 0
        self.__cur_pos = 0

        self.__lock = Lock()
        self.__handler_thread_pool = []
        self.__none_handler_thread_indexes = []

        for i in xrange(g_config_thread_pool_min_size.value):
            # handler = TaskHandlerFactory.create_handler(self.__cur_threads)
            handler_thread = TaskHandlerThread(self.__cur_threads)
            handler_thread.setDaemon(True)
            handler_thread.start()
            self.__handler_thread_pool.append(handler_thread)
            self.__cur_threads += 1

    def _get_task_handler_thread(self, handler):
        for i in xrange(self.__cur_pos, self.__cur_threads):
            if self.__handler_thread_pool[i].to_busy(handler):
                self.__cur_pos = i + 1
                return self.__handler_thread_pool[i]

        for i in xrange(self.__cur_pos):
            if self.__handler_thread_pool[i].to_busy(handler):
                self.__cur_pos = i + 1
                return self.__handler_thread_pool[i]

        return None

    def _new_handler_thread(self):
        '''
        If current thread number is less than g_config_thread_pool_max_size, then create a new task handler thread.
        '''
        if self.__cur_threads < g_config_thread_pool_max_size.value:
            logger.debug('create a new thread, and current thread number: %d', self.__cur_threads)
            if self.__none_handler_thread_indexes:
                index = self.__none_handler_thread_indexes.pop()
            else:
                index = self.__cur_threads
            handler_thread = TaskHandlerThread(index)
            handler_thread.setDaemon(True)
            handler_thread.start()

            self.__handler_thread_pool.append(handler_thread)
            self.__cur_threads += 1
            
    def make_thread_to_handle_task(self, key, task):
        '''
        Create a task handler according to the given key and make a handler thread to handle certain type task.
        '''
        keys = key.split(':')
        handler_type = keys[0]
        if handler_type == 'retry':
            handler_type = keys[2]
        clazz = TaskHandlerFactory.create_handler(handler_type)
        if not clazz:
            logger.debug('task handler type %s does not exist', handler_type)
            return False
        
        handler = clazz(key, task, self.__cur_pos)
        handler_thread = self._get_task_handler_thread(handler)
        self._new_handler_thread()
        if not handler_thread:
            logger.debug('thread pool has no idle thread, current threads: %d', self.__cur_threads)
            return False

        return True

    def kill_idle_handlers(self):
        count = 0
        index = g_config_thread_pool_min_size.value
        while index < self.__cur_threads and count < g_config_thread_kill_idle_each_time.value:
            if self.__handler_thread_pool[index].to_busy(None):
                handler_thread = self.__handler_thread_pool.pop(index)
                handler_thread.stop()
                self.__none_handler_thread_indexes.append(handler_thread.get_index())
                self.__cur_threads -= 1
                count += 1
            else:
                index += 1

            if self.__cur_pos > self.__cur_threads:
                self.__cur_pos = self.__cur_threads

    def kill_all_handlers(self):
        for handler_thread in self.__handler_thread_pool:
            handler_thread.stop()
