#!/usr/bin/python
#-*- coding: utf-8 -*-

#---------------------------------------------------
# File Name: global_variables.py
# Purpose:
# Creation Date: 13-02-2014
# Last Modified: Thu Feb 13 23:41:10 2014
# Created by:
#---------------------------------------------------

from service_status import ServiceStatus

from task_cache import TaskCache
from task_cache import TaskCacheDict

g_task_cache = TaskCache()
g_task_dict = TaskCacheDict()
g_service_status = ServiceStatus()
