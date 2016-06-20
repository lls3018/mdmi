#!/usr/bin/python
#-*- coding: utf-8 -*-

#---------------------------------------------------
# File Name: main_process.py
# Purpose:
# Creation Date: 17-12-2013
# Last Modified: Tue Mar 18 19:14:47 2014
# Created by:
#---------------------------------------------------

import os
import signal
import sys
import time
import atexit
from multiprocessing import Queue

if not '/opt/mdmi/modules' in sys.path:
    sys.path.append('/opt/mdmi/modules')

reload(sys)
sys.setdefaultencoding('utf-8')

from utils import logger

#from service_config import g_config_thread_pool_max_size
from service_config import reload_config
from service_variables import g_service_status

from socket_process import SocketProcess
from dispatch_process import DispatchProcess
from schedule_process import ScheduleProcess

#from task_cache import TaskCache
#from task_cache import TaskCacheDict
#from service_variables import g_service_status

#from service_status import ServiceStatus

work_dir = '/var/run/mdmi'
pid_file = 'task_service.pid'
sock_file = 'task_service.sock'
config_file = '/opt/mdmi/etc/task_service.conf'
make_daemon = False

socket_process = None
dispatch_process = None
schedule_process = None
#service_status = ServiceStatus()

to_stop = False

def parse_option():
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'c:dwh', ['config=', 'daemon', 'workdir', 'help'])
    except getopt.GetoptError as e:
        print 'Parse options error: %s' % str(e)
        return 2
    
    global config_file, make_daemon, workdir
    for o, a in opts:
        if o in ['-c', '--config']:
            config_file = a
        elif o in ['-d', '--daemon']:
            make_daemon = True
        elif o in ['-w', '--workdir']:
            if os.path.isdir(a) and os.access(a, os.W_OK):
                workdir = a
            elif not os.path.exists(a):
                try:
                    os.makedirs(a, 0600)
                except os.error as e:
                    print 'Cannot create directory: %s - %s' % (a, e)
                    return 3
        elif o in ['-h', '--help']:
            return 1

def usage():
    print "Usage: %s [options]\n" % sys.argv[0]
    print "Options:\n" \
          "  -h, --help             show this help message and exit\n" \
          "  -c FILE, --config FILE config file, default value is /opt/mdmi/etc/task_service.conf\n" \
          "  -d, --deamon           run this program as a daemon service\n" \
          "  -w DIR, --workdir DIR  work directory, pid file and unixsock file will be created in this directory"

def cleanup():
    os.remove(pid_file)

def daemonize():
    '''
    Daemon init.
    '''
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        logger.error('Task service: fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
        sys.exit(1)

    os.chdir(work_dir)
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        logger.error('Task service: fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
        sys.exit(1)

    sys.stdout.flush()
    sys.stderr.flush()
    si = file("/dev/null", 'r')
    so = file("/dev/null", 'a+')
    se = file("/dev/null", 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    atexit.register(cleanup)
    pid = str(os.getpid())
    file(pid_file, 'w+').write('%s\n' % pid)

def stop_children():
    global socket_process
    global dispatch_process
    global schedule_process
    global to_stop

    to_stop = True

    if socket_process:
        socket_process.terminate()
    if schedule_process:
        schedule_process.stop()
    if dispatch_process:
        dispatch_process.stop()

def signal_handler(signum, frame):
    logger.debug('Catched interrupt signal: %d in main process', signum)
    if signum == signal.SIGHUP:
        reload_config()
        g_service_status.reload_status()
    else:
        stop_children()

def join_children():
    global socket_process
    global dispatch_process
    global schedule_process

    if socket_process and socket_process.is_alive():
        socket_process.join()

    if dispatch_process and dispatch_process.is_alive():
        dispatch_process.join()

    if schedule_process and schedule_process.is_alive():
        schedule_process.join()

def watch_dog():
    global to_stop
    global socket_process
    global dispatch_process
    global schedule_process

    while not to_stop:
        try:
            time.sleep(5)
        except Exception:
            pass
        else:
            start_sub_process(is_first=False)

def start_sub_process(is_first=True):
    global socket_process
    global dispatch_process
    global schedule_process
    #global service_status
    global sock_file
    global to_stop

    if to_stop:
        return

    if not is_first and not socket_process.is_alive():
        logger.warning("socket process was stopped, try to start it")
    if is_first or (not is_first and not socket_process.is_alive()):
        socket_queue = Queue()
        socket_process = SocketProcess(sock_file, socket_queue)
        socket_process.start()

        try:
            status = socket_queue.get(timeout=3)
            if status != 0:
                stop_children()
                return
        except Exception:
            logger.error('Cannot start socket process at this time')
            stop_children()
            return

    if not is_first and not dispatch_process.is_alive():
        logger.warning("dispatch thread was stopped, try to start it")
    if is_first or (not is_first and not dispatch_process.is_alive()):
        dispatch_queue = Queue()
        dispatch_process = DispatchProcess(dispatch_queue)
        dispatch_process.start()

    if not is_first and not schedule_process.is_alive():
        logger.warning("schedule thread was stopped, try to start it")
    if is_first or (not is_first and not schedule_process.is_alive()):
        schedule_process = ScheduleProcess(dispatch_process)
        schedule_process.start()

def main():
    r = parse_option()
    if r:
        usage()
        return r - 1

    if make_daemon:
        daemonize()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # read config file to load constant values
    reload_config()
    g_service_status.reload_status()

    try:
        os.chdir(work_dir)
    except Exception as e:
        logger.error('cannot change work directory %s: %s', work_dir, e)
        return 255

    try:
        start_sub_process()
        watch_dog()

        join_children()
    except Exception as e:
        logger.error('Exception occurred in main process: %s', e)
        stop_children()
    finally:
        if os.access(work_dir, os.W_OK):
            if os.access(pid_file, os.W_OK):
                os.remove(pid_file)

if __name__ == '__main__':
    main()
