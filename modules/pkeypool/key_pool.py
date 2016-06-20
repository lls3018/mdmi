#!/usr/bin/env python2.6
# encoding=utf-8

# # @package pkeypoolservice
#  Implementation of private key pool service. 
#  The service in order to generate private keys for other services(For example, VPN profile generation service).
#  @file key_pool.py
#  @brief Implementation of service to provide private keys.
#  @author xfan@websense.com

import multiprocessing
import time
import os
import signal
import sys
import threading
import defs
from key_creator import keys_creator
from key_creator import generate_keys
if not '/opt/mdmi/modules' in sys.path:
    sys.path.append('/opt/mdmi/modules')
from utils import logger
from utils.serviceutils import BaseServiceServer

# # Global signal flag.
is_signal_up = False  # exit signal flag

# # Service to provide private keys for clients.
class KeyPoolServer(BaseServiceServer):
    # #The constructor
    # @param host Host name.
    # @param port Host port number.
    # @param dir Folder to save private keys.
    # @param creators Expect number of the creators.
    def __init__(self, host=defs.KEYPL_DEFAULT_HOST, port=defs.KEYPL_DEFAULT_PORT, dir=defs.KEYPL_DEFAULT_DIR, creators=defs.KEYPL_DEFAULT_CREATORS_CNT):
        self.m_stop = False
        self.m_key_dir = dir
        self.m_pool_lock = threading.Lock()
        self.m_key_pool_list = []
        self.m_init_evt = multiprocessing.Event()
        self.m_stop_evt = multiprocessing.Event()
        super(KeyPoolServer, self).__init__('private key pool service', host, port, defs.KEYPL_DEFAULT_ACCPECT_LIMIT)
        self.m_num_creators = creators
        if self.m_num_creators <= 0:
            err = 'Creators input error, make sure the value bigger than 1!'
            logger.error(err)
            raise Exception(err)
            exit(-1)
        self.m_creators = []

        items = defs.KEYPL_DEFAULT_ITEMS_IN_QUEUE 
        if items > (defs.KEYPL_MULTIPLE_QUEUES * self.m_num_creators):
            pass
        else:
            items = defs.KEYPL_MULTIPLE_QUEUES * self.m_num_creators
        self.m_keys_queue = multiprocessing.Queue(items)
        pass

    # # The service entry.
    # @brief Service start to work.
    # @param self The pointer of the object.
    def run(self):
        self._keys_ctrl_start()
        pass

    # # Stop the service.
    # @param self The pointer of the object.
    def stop(self):
        self.m_stop = True
        if self.m_stop_evt:
            self.m_stop_evt.set()
        self._do_clean()
        pass

    def _do_clean(self):
        # stop creator
        for creator in self.m_creators:
            try:
                creator.join(5)
            except:
                pass
            finally:
                if creator.is_alive():
                    creator.terminate()

        # empty queue
        if self.m_keys_queue:
            self.m_keys_queue.close()
            while not self.m_keys_queue.empty():
                self.m_keys_queue.get()
        pass
    
    # # Service idle for a while.
    # @param self The pointer of the object.
    # @param sec The seconds expected.
    # @return True Cancel by stoping request.
    # @return False Reach the idle seconds. 
    def _delay(self, sec):
        retval = False
        if self.m_stop_evt:
            self.m_stop_evt.wait(sec)
        else:
            time.sleep(sec)

        retval = self.m_stop
        return retval
        pass

    # #Service start to accept the requests.
    # @param self The pointer of the object.
    def _keys_ctrl_start(self):
        # set up listener to accept requirements
        sock = self.do_setup()
        while (sock == None) and (self.m_stop == False):
            time.sleep(1)
            sock = self.do_setup()
        
        # setup key creators
        self._init_key_creators()
        logger.info('Keypool service init done! Started!')

        while(self.m_stop == False):
            if(0 != self.do_listen(sock, self._do_handle, 0.1)):
                logger.debug('Key pool service error occurred, stop creators')

        if sock:
            sock.close()
        logger.info('Keypool service shutting down!')
        pass

    # #init creators
    # @param self The pointer of the object.
    def _init_key_creators(self):
        # set up creators for generate keys
        self.m_creators = [keys_creator(self.m_init_evt, self.m_stop_evt, self.m_keys_queue, self.m_key_dir, True)]
        while len(self.m_creators) < self.m_num_creators:
            self.m_creators.append(keys_creator(self.m_init_evt, self.m_stop_evt, self.m_keys_queue, self.m_key_dir))
        for creator in self.m_creators:
            creator.start()
        pass

    # #Handler for the accepted connections.
    # @param self The pointer of the object.
    # @param conn Connection object.
    # @param recvdata The data received.
    def _do_handle(self, conn, recvdata):
        try:
            data = eval(recvdata)
        except Exception, e:
            logger.error('Key pool service convert command failed! %s' % repr(e))
        if not isinstance(data, dict):
            logger.error('Wrong command, turning down!')
            return 1
        
        key_cnt = data.get('key_cnt') # handle key require
        if key_cnt and (key_cnt > 0):
            retval = self._get_valid_keys(key_cnt)
            if retval:
                conn.sendall(repr(retval))
        else:
            cmd = data.get('command')
            if cmd:  # handle command
                result = self._cmd_handle(cmd)
                conn.sendall(repr(result))
            else:  # error message
                logger.error('Wrong command for key pool, command: %s' % recvdata)
        
        if conn:
            conn.close()
        pass

    # #Get valid private keys
    # @param self The pointer of the object.
    # @param cnt Expect number of the private keys.
    # @return One list with expect private keys.
    def _get_valid_keys(self, cnt):
        retval = []
        get_cnt = 0
        key_list = None
        while get_cnt < cnt :  # situation: request number larger than the keys remain in pool
            if self.m_stop:
                break
            
            step_cnt = cnt - get_cnt
            #To release lock as fast as possible
            self.m_pool_lock.acquire()  # lock
            if not self.m_key_pool_list: # for the first round, trigger to read one group keys
                self.m_key_pool_list = self.m_keys_queue.get()
            remain = len(self.m_key_pool_list)
            if remain < step_cnt: #require keys more than remain keys
                key_list = self.m_key_pool_list
                self.m_key_pool_list = []
                step_cnt = remain
            else: #get enough keys
                key_list = self.m_key_pool_list[:step_cnt]
                del self.m_key_pool_list[:step_cnt]
            self.m_pool_lock.release()  # release

            if key_list: 
                #Get some keys, append them and remove the key files
                for key in key_list:
                    retval.append(key['content'])
                    # delete key file
                    self._remove_key_file(key['fn'])
            else:
                #Keys were not enough, runtime generate one
                key = generate_keys(1)[0]
                retval.append(key['content'])
                step_cnt = 1
            # update status for next round
            get_cnt = get_cnt + step_cnt

        return retval
        pass

    # #Remove the used private key file.
    # @param self The pointer of the object.
    # @param name The name of the key file.
    def _remove_key_file(self, name):
        if not name:
            return
        try:
            os.remove(self.m_key_dir + '/' + name)
        except:
            pass
        pass

    # #Handler of the commands
    # @param self The pointer of the object.
    # @param cmd Command content.
    # @return The response to the specific command.
    def _cmd_handle(self, cmd):
        if cmd == defs.KEYPL_CMDS['alive']:
            return {'response':1}
        elif cmd == defs.KEYPL_CMDS['qsize']:
            return {'response': self.m_keys_queue.qsize()}
        elif cmd == defs.KEYPL_CMDS['remain_keys']:
            rkeys = self._count_remain_keys()
            return {'response': rkeys}
        else:
            return None
        pass

    # #Count the remain keys at mement
    # @param self The pointer of the object.
    # @return The number of the remain private keys in the pool.
    def _count_remain_keys(self):
        qsize = self.m_keys_queue.qsize()
        qkeys = qsize * defs.KEYPL_MAX_CNT
        lkeys = len(self.m_key_pool_list)
        return (qkeys + lkeys)
        pass

# end class


# # Handler of the signals
# @param signum The ID of the signal.
# @param frame Frame of the signal sent.
def signal_handler(signum, frame):
    global is_signal_up
    logger.debug('Catched a stop signal!')
    is_signal_up = True
    pass

# # Start service
def start_service():
    ctrl = KeyPoolServer()
    ctrl.start()
    
    #signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)

    while True:
        try:
            if is_signal_up:
                ctrl.stop()
                ctrl.join()
                break
            else:
                time.sleep(0.1)

        except Exception, e:
            logger.error(e)
            break
    pass

if __name__ == '__main__':
    start_service()
    pass

