#!/usr/bin/env python2.6
# encoding=utf-8

# # @package pkeypoolservice
#  Implementation of private key pool service. 
#  The service in order to generate private keys for other services(For example, VPN profile generation service).
#  @file keypoolclient.py
#  @brief Implementation of client to require private keys.
#  @author xfan@websense.com

import sys
import time
import defs
if not '/opt/mdmi/modules' in sys.path:
    sys.path.append('/opt/mdmi/modules')
from utils import logger
from utils.serviceutils import BaseServiceClient
from utils.configure import MDMiConfigParser
from utils.configure import MDMI_CONFIG_FILE

# # Implementation of the key pool client.
class KeyPoolClient(BaseServiceClient):
    # #The constructor
    # @param host Host name of the server.
    # @param port Host port number of the server.
    def __init__(self, host=defs.KEYPL_DEFAULT_HOST, port=defs.KEYPL_DEFAULT_PORT):
        super(KeyPoolClient, self).__init__('Require private keys', host, port)
        pass

    # # Require private keys from server.
    # @param self The pointer of the object.
    # @param cnt The expect number of the private keys.
    def require(self, cnt):
        assert(cnt <= defs.KPLS_REQ_MAX)
        logger.info('Client require %d private keys!' % cnt)
        keylist = []
        sock = self.do_connect(0) #set block
        if not sock:
            return keylist
        
        start_point = time.time()
        try:
            data = {'key_cnt' : cnt}
            sock.sendall(repr(data))
            sock.settimeout(defs.KEYPL_RECV_TIMOUT)
            data = ''
            if(cnt > 0):
                while True:
                    recv_data = sock.recv(655350)
                    if recv_data:
                        data = data + recv_data
                        if data[-1] is not ']':  # make sure recv all
                            if self._is_recv_timeout(start_point):
                                raise Exception('Recv timeout!')
                            else:
                                continue
                        else:
                            keylist = eval(data)
                            break
            else:
                keylist = []

        except Exception, e:
            logger.error('Client require exception: %s' % e)
            keylist = []

        finally:
            if sock:
                sock.close()
            logger.info('Client require keys done!')
        return keylist

    def _is_recv_timeout(self, start):
        now = time.time()
        if (now - start) >= defs.KEYPL_RECV_TIMOUT:
            return True
        else:
            return False

    # # To check the status of private key pool service
    # @param self The pointer of the object.
    def service_is_alive(self):
        logger.info('Client check service available!')
        sock = self.do_connect(defs.KEYPL_DEFAULT_TIMOUT)
        if not sock:
            logger.warning('Connect to key pool service failed!')
            return False

        try:
            data = self._send_cmd(sock, defs.KEYPL_CMDS['alive'])
            result = data.get('response')
            if result:
                return True
        except Exception, e:
            logger.error('Client check service status exception: %s' % e)
            return False
        finally:
            if sock:
                sock.close()
            logger.info('Client check service done!')
        return False
        pass

    # # To check the queue size of private key pool service
    # @param self The pointer of the object.
    def service_qsize(self):
        logger.info('Client query queue size!')
        sock = self.do_connect(defs.KEYPL_DEFAULT_TIMOUT)
        if not sock:
            logger.warning('Connect to key pool service failed!')
            return False
        try:
            data = self._send_cmd(sock, defs.KEYPL_CMDS['qsize'])
            return data.get('response')
        except Exception, e:
            logger.error('Client query queue size exception: %s' % e)
            raise Exception(e)
        finally:
            if sock:
                sock.close()
            logger.info('Client query queue size done!')
        pass

    # # To query the remain keys number of private key pool service
    # @param self The pointer of the object.
    def service_remain_keys(self):
        logger.info('Client query remain keys!')
        sock = self.do_connect(defs.KEYPL_DEFAULT_TIMOUT)
        if not sock:
            logger.warning('Connect to key pool service failed!')
            return False
        try:
            data = self._send_cmd(sock, defs.KEYPL_CMDS['remain_keys'])
            return data.get('response')
        except Exception, e:
            logger.error('Client query remain keys exception: %s' % e)
            raise Exception(e)
        finally:
            if sock:
                sock.close()
            logger.info('Client query remain keys done!')
        pass

    def _send_cmd(self, sock, cmd):
        data = {'command':cmd}
        sock.sendall(repr(data))
        data = ''
        data = sock.recv(65535)
        if data:
            data = eval(data)
        return data
        pass

# end of class KeyPoolClient

# #check the service enabled flag
# @return True Private key pool service allows to work.
# @return False Private key pool service is forbidden.
def pkeypool_is_enabled():
    cfg = MDMiConfigParser(cfgfile=MDMI_CONFIG_FILE)
    info = cfg.read('vpn', 'pkeypool_service_enabled')
    if info and info[0]:
        val = info[0][1]
    else:
        val = None
    if val:
        if int(val):
            return True
        else:
            logger.debug('Private key pool service disabled!')
    else:
        logger.debug('Private key pool service flag not found!')
    return False
    pass

def _do_test():
    client = KeyPoolClient()
    logger.debug(client.service_remain_keys())
    round = 3
    logger.debug("test key pool:")
    while round:
        klst = client.require(2)
        logger.debug("Get valid %d keys!" % len(klst))
        round = round - 1
    pass

if __name__ == '__main__':
    _do_test()
    pass

