#!/usr/bin/env python

import sys
import os
import time
import atexit
import string
from signal import SIGTERM
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
from utils import logger

class Daemon:
    '''
    class Daemon 
        This class implements the daemon service.

    Attributes:
        service: Name of the service.
        stdin: Input stream.
        stdout: Output stream.
        stderr: Error stream.
        pidfile: *.pid for the specific service.
    '''
    def __init__(self, service='Service', pidfile=None, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        if not pidfile:
            raise Exception('Invalid input! Please input the service pid file name!')
        self.service = service
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        pass

    def _daemonize(self):
        '''
        Daemon init.
        '''
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            logger.error('Daemon %s:fork #1 failed: %d (%s)\n' % (self.service, e.errno, e.strerror))
            sys.exit(1)

        os.chdir("/")
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            logger.error('Daemon %s:fork #2 failed: %d (%s)\n' % (self.service, e.errno, e.strerror))
            sys.exit(1)

        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        atexit.register(self._delpid)
        pid = str(os.getpid())
        file(self.pidfile, 'w+').write('%s\n' % pid)
        pass

    def _delpid(self):
        os.remove(self.pidfile)
        pass

    def status(self):
        '''
        Check the status of the service.
        '''
        try:
            pid = self._check_pid_()
        except IOError:
            pid = None

        if pid:
            sys.stdout.write('%s is running!\n' % self.service)
        else:
            sys.stdout.write('%s is stopped!\n' % self.service)
        pass

    def start(self):
        '''
        Start the service.
        '''
        try:
            pid = self._check_pid_()
        except IOError:
            pid = None

        if pid:
            message = 'Daemon:pidfile %s already exists. %s already running!\n' % (self.pidfile, self.service)
            sys.stdout.write(message)
            sys.exit(1)

        self._init_()
        self._daemonize()
        self._run_()
        pass

    def stop(self):
        '''
        Stop the service.
        '''
        try:
            pid = self._check_pid_()
        except IOError:
            pid = None

        if not pid:
            message = 'Daemon:pidfile %s does not exist. %s already stopped!\n' % (self.pidfile, self.service)
            sys.stdout.write(message)
            return

        try:
            while True:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
            self._clean_()
        except OSError, err:
            err = str(err)
            if err.find('No such process') > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                logger.error('Daemon:%s' % err)
                sys.exit(1)
        pass

    def restart(self):
        '''
        Restart the service.
        '''
        self.stop()
        self.start()
        pass

    def _check_pid_(self):
        pf = file(self.pidfile, 'r')
        pid = int(pf.read().strip())
        pf.close()
        #check pid exists
        if str(pid) in os.listdir('/proc'):
            return pid
        else:
            #remove pid file
            os.remove(self.pidfile)
            return None
        pass

    def _run_(self):
        pass

    def _init_(self):
        pass

    def _clean_(self):
        pass

#end of class Daemon


