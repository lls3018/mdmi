#!/usr/bin/env python2.6
#encoding=utf-8

import fcntl
from psutil import cpu_percent

def lock_file(file):
    fcntl.flock(file.fileno(), fcntl.LOCK_EX)

def unlock_file(file):
    fcntl.flock(file.fileno(), fcntl.LOCK_UN)

def get_current_cpu_percent(interval=0.01, percpu=True):
    '''
    Get average usage percent of all cores at current.
    
    Params:
        interval: When interval is > 0.0 compares system CPU times elapsed before and after the interval (blocking).
                When interval is 0.0 or None compares system CPU times elapsed since last call 
                or module import, returning immediately. In this case is recommended for accuracy that 
                this function be called with at least 0.1 seconds between calls.
        percpu: First element of the list refers to first CPU, second element to second CPU and so on.

    Return:
         a float representing the current system-wide CPU utilization as a percentage.
    '''
    percents = cpu_percent(interval, percpu)
    retval = 0.0
    if percpu: # a list
        assert(len(percents) > 0)
        for val in percents:
            retval = retval + val
        retval = retval / len(percents)
    else:
        retval = percents
    return retval
    pass

