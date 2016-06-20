#!/usr/bin/env python2.6
#encoding=utf-8

## @package ods-mdmi-task-enrollment
#  Implementation of plugin for enrollment decision tasks.
#  The service in order to handle every enrollment decision task.
#  @file defs.py
#  @brief Defines default value for the plugin.
#  @author xfan@websense.com

##Modules library root path
MOD_ROOT = '/opt/mdmi/modules'

##Task queue table, all task queues listed in beblow would established by default.
TQ_SETUP_TAB = [
        {'name' : 'enrollment', 'settings' : {"description" : "Enrollment Decision task queue", "max_leases" : "30", "max_age" : "0"}},
        {'name' : 'iosdeploy', 'settings' : {"description" : "iOS Deploy task queue", "max_leases" : "30", "max_age" : "0"}},
        {'name' : 'enrollmentRetry', 'settings' : {"description" : "Enrollment Decision Retry task queue", "max_leases" : "30", "max_age" : "0"}},
        {'name' : 'enrollmentError', 'settings' : {"description" : "Enrollment Decision Error task queue", "max_leases" : "30", "max_age" : "0"}},
        {'name' : 'androiddeploy', 'settings' : {"description" : "Android Deploy task queue", "max_leases" : "30", "max_age" : "0"}},
        ]

##Default retry rounds while task handle failed in the enrollment decision plugin module.
ELM_HANDLE_RETRY_RNDS = 5

##Type defined in the section tags for enrollment task
TASK_TAGS_EVT_TYPE = {
        'Enrollment' : 1,
        'De-enrollment' : 2,
        'Wipe' : 3,
        'Enterprise Wipe' : 4,
        'Compliance status changed' : 5,
        'Compromise status changed' : 6,
        }

##Supported os type
OS_TYPE_SUPPORTED = {
        'Apple' : 1,
        'Android' : 2,
        }

##Supported os version, order by os type
OS_VER_SUPPORTED = [
        10000, #ignored
        0.0, #Apple
        0.0, #Android
        ]

##Get a key value from a dict
# @param srcdict Source dict.
# @param key Key name in the source dict.
# @param err If the key does not exist in the source dict, use 'err' instead the value.
# @return The value or the err.
def get_dict_value(srcdict, key, err):
    if srcdict.has_key(key):
        try:
            value = srcdict[key]
            if value == None:
                return err
            return value
        except Exception, e:
            return err
    else:
        return err
    pass

##Get a key value from a dict
# @param srcdict Source dict.
# @param key Key name in the source dict.
# @param defval Default value when no key matches.
# @param expect A return value dict.
# @return The value.
def get_dict_value2(srcdict, key, defval, **expect):
    for ekey in expect:
        if srcdict[key] == ekey:
            return expect[ekey]
    return defval
    pass


