#!/usr/bin/env python2.6
# encoding=utf-8

# # @package pkeypoolservice
#  Implementation of private key pool service. 
#  The service in order to generate private keys for other services(For example, VPN profile generation service).
#  @file service_daemon.py
#  @brief Service daemon.
#  @author xfan@websense.com

import sys
if not '/opt/mdmi/modules' in sys.path:
    sys.path.append('/opt/mdmi/modules')
from utils.daemon import Daemon
import key_pool
from keypoolclient import pkeypool_is_enabled

# #Service name
SERVICE_NAME = 'Private Key Pool'
# #Path of the service pid file
SERVICE_PIDFILE_PATH = '/var/run/pkeypoolservice.pid'
# #Input stream
SERVICE_STDIN = '/dev/null'
# #Output stream
SERVICE_STDOUT = '/dev/null'
# #Error stream.
SERVICE_STDERR = '/dev/null'

# # Subclass of the Daemon, in order to define new behaviour to start the daemon.
class service(Daemon):
    # #Daemon init.
    # @param self The pointer of the object.
    def _init_(self):
        # check service enable flag
        if pkeypool_is_enabled():
            sys.stdout.write('Private key pool service enabled!\n')
        else:
            sys.stdout.write('Private key pool service disabled!\n')
        pass

    # #Daemon entry.
    # @param self The pointer of the object.
    def _run_(self):
        # check service enable flag
        if pkeypool_is_enabled():
            key_pool.start_service()
        else:
            sys.exit(1)
        pass

if __name__ == '__main__':
    # #Daemon object
    _daemon = service(service=SERVICE_NAME, pidfile=SERVICE_PIDFILE_PATH, stdin=SERVICE_STDIN, stdout=SERVICE_STDOUT, stderr=SERVICE_STDERR)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            _daemon.start()
        elif 'stop' == sys.argv[1]:
            _daemon.stop()
        elif 'restart' == sys.argv[1]:
            _daemon.restart()
        elif 'status' == sys.argv[1]:
            _daemon.status()
        else:
            sys.stdout.write('Unknown command!\n')
            sys.exit(2)
        sys.exit(0)  # exit normal
    else:
        sys.stdout.write('usage: %s start|stop|restart\n' % sys.argv[0])
        sys.exit(2)
    pass

