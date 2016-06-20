#!/usr/bin/python
#-*- coding: utf-8 -*-

#---------------------------------------------------
# File Name: service_status.py
# Purpose:
# Creation Date: 12-02-2014
# Last Modified: Tue Mar 18 19:55:07 2014
# Created by:
#---------------------------------------------------

#from multiprocessing import Lock
from multiprocessing import Array
import json
import hashlib
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')

from utils import logger
from service_config import g_config_thread_pool_max_size

class SimpleHash:
    def __init__(self, cap, seed):
        self._cap = cap
        self._seed = seed

    def hash(self, value):
        ret = 0
        if value:
            value = hashlib.md5(value).digest()
        for i in range(len(value)):
            ret += self._seed*ret + ord(value[i])
        return (self._cap - 1) & ret

class CbFilter:

    def __init__(self):
        self._BIT_SIZE = 1 << 21
        self._seeds = [5, 7, 11, 13, 31, 37, 61, 67]
        self._bit_list = [0 for i in range(self._BIT_SIZE)]
        self._hash_func = []

        for i in range(len(self._seeds)):
            self._hash_func.append(SimpleHash(self._BIT_SIZE, self._seeds[i]))

    def insert(self, value):
        for f in self._hash_func:
            loc = f.hash(value)
            self._bit_list[loc] = self._bit_list[loc] + 1

    def remove(self, value):
        for f in self._hash_func:
            loc = f.hash(value)
            self._bit_list[loc] = self._bit_list[loc] - 1

    def contains(self, value):
        if value == None:
            return False
        ret = True
        for f in self._hash_func:
            loc = f.hash(value)
            ret = ret & (self._bit_list[loc] > 0)
        return ret

class ServiceStatus:
    def __init__(self):
        self.__status = {}
        self.__filter = CbFilter()
        self.__capacity = 0
        self.reload_status()

    def reload_status(self):
        if g_config_thread_pool_max_size.value > self.__capacity:
            logger.debug('status capacity changed from %d to %d', self.__capacity, g_config_thread_pool_max_size.value)
            self.__capacity = g_config_thread_pool_max_size.value
            self.__invoke_thread_number = Array("i", self.__capacity)
            self.__task_number = Array("i", self.__capacity) 
            self.__user_number = Array("i", self.__capacity)
            self.__user_success_number = Array("i", self.__capacity)
            self.__group_number = Array("i", self.__capacity)
            self.__group_success_number = Array("i", self.__capacity)

    def filter_metanate_request(self, tasks):
        account = tasks[0]['account']
        trans_type = tasks[0]['trans_type']
        for task in tasks:
            func = task['func']
            param = json.dumps(task['parameters'])
            fkey = "$$".join([str(account), trans_type, func, param])
            if self.__filter.contains(fkey):
                tasks.remove(task)
            else:
                with self.__lock:
                    self.__filter.insert(fkey)

    def clear_metanate_request(self, tasks):
        account = tasks[0]['account']
        trans_type = tasks[0]['trans_type']
        for task in tasks:
            func = task['func']
            param = json.dumps(task['parameters'])
            fkey = "$$".join([str(account), trans_type, func, param])
            if self.__filter.contains(fkey):
                with self.__lock:
                    self.__filter.remove(fkey)

    def _set_status(self, key, value):
        self.__status[key] = value

    def set_dispatch_status(self, value):
        if value == 1:
            self._set_status('dispatch', 'on')
        else:
            self._set_status('dispatch', 'off')

    def set_schedule_status(self, value):
        if value == 1:
            self._set_status('schedule', 'on')
        else:
            self._set_status('schedule', 'off')

    def set_socket_status(self, value):
        if value == 1:
            self._set_status('socket', 'on')
        else:
            self._set_status('socket', 'off')

    def set_task_handled_number(self, value):
        self._set_status('task finished', value)

    def set_metanate_session_created(self, value):
        self._set_status('metanate session created', value)

    def set_task_in_queue(self, value):
        self._set_status('task in queue', value)

    def increase_invoke_thread_number(self, index, n=1):
        #with self.__lock:
        self.__invoke_thread_number[index] += n

    def increase_user_number(self, index, n=1):
        #with self.__lock:
        self.__user_number[index] += n

    def increase_user_success_number(self, index, n=1):
        #with self.__lock:
        self.__user_success_number[index] += n

    def increase_group_number(self, index, n=1):
        #with self.__lock:
        self.__group_number[index] += n

    def increase_group_success_number(self, index, n=1):
        #with self.__lock:
        self.__group_success_number[index] += n

    #def __str__(self):
    #    return json.dumps(self.__status)

    def get_json_content(self):
        invoke_thread_number = 0
        user_number = 0
        user_success_number = 0
        group_number = 0
        group_success_number = 0

        for i in xrange(self.__capacity):
            invoke_thread_number += self.__invoke_thread_number[i]
            user_success_number += self.__user_success_number[i]
            user_number += self.__user_number[i]
            group_success_number += self.__group_success_number[i]
            group_number += self.__group_number[i]

        s = ['"number of invoking task handler":  %d' % invoke_thread_number,
         '"handled user tasks": %d' % user_number, 
         '"successful user tasks": %d' % user_success_number,
         '"handled group tasks": %d' % group_number,
         '"successful group tasks": %d' % group_success_number]

        return ", ".join(s).join(["{", "}"])
