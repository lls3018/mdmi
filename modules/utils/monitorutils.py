#! /usr/bin/python
# fileName: monitorutils.py
# encoding=utf-8

import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')

from utils import logger
import ConfigParser
import json
import os
from utils.sysutils import lock_file, unlock_file

MONITOR_COUNTER_PATH = '/opt/mdmi/etc/mdmi_monitor'
MONITOR_CONFIG_PATH = '/opt/mdmi/etc/monitors.json'

def count_task(name, is_success):
    """
    Count and record tasks in monitor configuration file according to the given name.
    """

    monitor_ini = '{path}/mdmi_monitor_{service}.ini'.format(path=MONITOR_COUNTER_PATH, service=name)
    conf = ConfigParser.SafeConfigParser()
    # create configuration file if it does not exist 
    try:
        file = open(monitor_ini, 'r+')
    except IOError, e:
        file = open(monitor_ini, 'a+')

    lock_file(file)
    conf.read(monitor_ini)
    try:
        total_success = conf.getint(name, '%s_receiving_success_counter' % name)
        total_fail = conf.getint(name, '%s_receiving_failure_counter' % name)
    except ConfigParser.NoSectionError, e:
        # empty file, do init
        logger.debug('section %s does not exist in monitor configuration file, init section %s' % (name, name))
        conf.add_section(name)
        conf.set(name, '%s_receiving_success_counter_last' % name, '0')
        conf.set(name, '%s_receiving_failure_counter_last' % name, '0')
        if is_success:
            conf.set(name, '%s_receiving_success_counter' % name, '1')
            conf.set(name, '%s_receiving_failure_counter' % name, '0')
            logger.debug('total %s success task number is: %s' % (name, '1'))
            logger.debug('total %s failure task number is: %s' % (name, '0'))
        else:
            conf.set(name, '%s_receiving_failure_counter' % name, '1')
            conf.set(name, '%s_receiving_success_counter' % name, '0')
            logger.debug('total %s success task number is: %s' % (name, '0'))
            logger.debug('total %s failure task number is: %s' % (name, '1'))
        conf.write(file)
    except Exception, e:
        logger.error('write %s monitor record error! message: %s' % (name, repr(e)))
    else:
        if is_success:
            total_success += 1
        else:
            total_fail += 1
        
        conf.set(name, '%s_receiving_success_counter' % name, str(total_success))
        conf.set(name, '%s_receiving_failure_counter' % name, str(total_fail))
        conf.write(file)
        logger.debug('total %s success task number is: %s' % (name, total_success))
        logger.debug('total %s failure task number is: %s' % (name, total_fail))
    finally:
        file.flush()
        unlock_file(file)
        file.close()

def count_periodic_task(name, values):
    """
    Count and record periodic tasks in monitor configuration file according to the given name.
    """

    monitor_ini = '{path}/mdmi_monitor_{service}.ini'.format(path=MONITOR_COUNTER_PATH, service=name)
    conf = ConfigParser.SafeConfigParser()
    # create configuration file if it does not exist 
    try:
        file = open(monitor_ini, 'r+')
    except IOError, e:
        file = open(monitor_ini, 'a+')
    
    lock_file(file)
    conf.read(monitor_ini)
    try:
        for key1 in values:
            for key2 in values[key1]:
                for key3 in values[key1][key2]:
                    option = '{0}_{1}_{2}_{3}'.format(name, key1, key2, key3)
                    value = int(values[key1][key2][key3]) + conf.getint(name, option)
                    conf.set(name, option, str(value))
                    logger.debug('{0} {1} {2} {3} task number is: {4}'.format(name, key1, key2, key3, str(value)))
        conf.write(file)
    except ConfigParser.NoSectionError, e:
        # empty file, do init
        logger.debug('section %s does not exist in monitor configuration file, init section %s' % (name, name))
        conf.add_section(name)
        for key1 in values:
            for key2 in values[key1]:
                for key3 in values[key1][key2]:
                    conf.set(name, '{0}_{1}_{2}_{3}'.format(name, key1, key2, key3), str(values[key1][key2][key3]))
                    logger.debug('{0} {1} {2} {3} task number is: {4}'.format(name, key1, key2, key3, str(values[key1][key2][key3])))
        conf.write(file)
    except Exception, e:
        logger.error('write %s monitor record error! message: %s' % (name, repr(e)))
    finally:
        file.flush()
        unlock_file(file)
        file.close()

def get_threshold(name, key):
    """
    Get monitor warning threshold in configuration file according to the given name.
    If configuration file does not exist, the return default value. 
    """

    if os.path.isfile(MONITOR_CONFIG_PATH):
        file = open(MONITOR_CONFIG_PATH)
        try:
            file = open(MONITOR_CONFIG_PATH)
            thresholds = json.loads(file.read())
            return thresholds['thresholds'][name][key]
        except Exception, e:
            logger.error('get %s monitor threshold error: %s' % (name, repr(e)))
        finally:
            file.close()
    else:
        logger.warning('monitor configuration file does not exist')
        return 10

def count_task_by_num(name, success_num=0, fail_num=0):
    """
    Record tasks in monitor configuration file according to the given name, and success and failure num.
    """

    monitor_ini = '{path}/mdmi_monitor_{service}.ini'.format(path=MONITOR_COUNTER_PATH, service=name)
    conf = ConfigParser.SafeConfigParser()
    # create configuration file if it does not exist 
    try:
        file = open(monitor_ini, 'r+')
    except IOError, e:
        file = open(monitor_ini, 'a+')

    lock_file(file)
    conf.read(monitor_ini)
    try:
        total_success = conf.getint(name, '%s_receiving_success_counter' % name)
        total_fail = conf.getint(name, '%s_receiving_failure_counter' % name)
    except ConfigParser.NoSectionError, e:
        # empty file, do init
        logger.debug('section %s does not exist in monitor configuration file, init section %s' % (name, name))
        conf.add_section(name)
        conf.set(name, '%s_receiving_success_counter_last' % name, '0')
        conf.set(name, '%s_receiving_failure_counter_last' % name, '0')
        conf.set(name, '%s_receiving_success_counter' % name, str(success_num))
        conf.set(name, '%s_receiving_failure_counter' % name, str(fail_num))
        conf.write(file)
        logger.debug('total %s success task number is: %s' % (name, str(success_num)))
        logger.debug('total %s failure task number is: %s' % (name, str(fail_num)))
    except Exception, e:
        logger.error('write %s monitor record error! message: %s' % (name, repr(e)))
    else:
        if success_num or fail_num:
            total_success += success_num
            total_fail += fail_num
        
            conf.set(name, '%s_receiving_success_counter' % name, str(total_success))
            conf.set(name, '%s_receiving_failure_counter' % name, str(total_fail))
            conf.write(file)
        logger.debug('total %s success task number is: %s' % (name, total_success))
        logger.debug('total %s failure task number is: %s' % (name, total_fail))
    finally:
        file.flush()
        unlock_file(file)
        file.close()

def clear_data(name):
    monitor_ini = '{path}/mdmi_monitor_{service}.ini'.format(path=MONITOR_COUNTER_PATH, service=name)
    conf = ConfigParser.SafeConfigParser()
    # create configuration file if it does not exist 
    try:
        file = open(monitor_ini, 'r+')
    except IOError, e:
        logger.error('%s monitor configuration file does not exist' % name)
        return
    
    lock_file(file)
    conf.read(monitor_ini)
    
    try:
        options = conf.options(name)
        if options:
            for option in options:
                conf.set(name, option, '0')
            conf.write(file)
            logger.debug('clear %s monitor configuration file data success')
    except Exception, e:
        logger.error('clear %s monitor configuration file data error! message: %s' % (name, repr(e)))
    finally:
        file.flush()
        unlock_file(file)
        file.close()

def trunk_data(name):
    monitor_ini = '{path}/mdmi_monitor_{service}.ini'.format(path=MONITOR_COUNTER_PATH, service=name)

    try:
        file = open(monitor_ini, 'w')
    except IOError, e:
        logger.error('%s monitor configuration file does not exist' % name)
    finally:
        file.flush()
        unlock_file(file)
        file.close()
