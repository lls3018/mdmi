#!/usr/bin/env python2.6
# encoding=utf-8

# # @package pkeypoolservice
#  Implementation of private key pool service. 
#  The service in order to generate private keys for other services(For example, VPN profile generation service).
#  @file key_creator.py
#  @brief Implementation of creator for generating private keys for the service.
#  @author xfan@websense.com

import multiprocessing
import os
import sys
import defs
import time
import Queue
import OpenSSL
if not '/opt/mdmi/modules' in sys.path:
    sys.path.append('/opt/mdmi/modules')
from utils import logger
from utils.sysutils import get_current_cpu_percent

# # Generate private keys
# @param cnt Expect number of the private keys would be generated.
# @param evt_stop Stop event flag.
# @param save Enable/Disable key saving flag.
# @param key_dir Folder to hold the private keys.
# @return One list with new private keys.
def generate_keys(cnt, evt_stop=None, save=False, key_dir=defs.KEYPL_DEFAULT_DIR):
    retval = []
    saved_file_names = []
    logger.info('Starting to generate %d private keys! timestamp:%f' % (cnt, time.time()))
    while(len(retval) < cnt):
        if evt_stop and evt_stop.is_set():
            break

        key_file = None
        key = OpenSSL.crypto.PKey()
        key.generate_key(OpenSSL.crypto.TYPE_RSA, 1024)
        key_content = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_ASN1, key)

        if save:  # save to files
            key_file = str(os.getpid()) + '_' + str(time.time())
            if key_file not in saved_file_names:
                saved_file_names.append(key_file)
            else:
                continue  #avoid the same file name, bottle neck!!!

            if key_file and key_content:
                fd = open(key_dir + '/' + key_file, 'w')
                fd.write(key_content)
                fd.close()

        key_val = {'fn':key_file, 'content':key_content}
        retval.append(key_val)
    logger.info('Finished generating %d private keys! timestamp:%f' % (len(retval), time.time()))

    return retval
    pass


# #Creator to generate private keys for the service.
# The creator would provide private keys as one processor.
class keys_creator(multiprocessing.Process):
    # #The constructor.
    # @param  self The pointer of the object.
    # @param  ready_evt multiprocessing.Event to notice new keys are prepared.
    # @param  stop_evt multiprocessing.Event to notice service is stopped.
    # @param  key_list_queue multiprocessing.Queue to load new private keys.
    # @param  key_dir Folder to hold the new key files.
    # @param  init Flag to enable init.
    def __init__(self, ready_evt, stop_evt, key_list_queue, key_dir, init=False):
        multiprocessing.Process.__init__(self)
        self.m_ready_evt = ready_evt
        self.m_keylist_queue = key_list_queue
        self.m_key_dir = key_dir
        self.m_stop_evt = stop_evt
        self.m_enable_init = init
        pass

    # #The processor's entry.
    # @brief Creator start to work.
    # @param self The pointer of the object.
    def run(self):
        # read keys from files at first
        if self.m_enable_init:
            logger.info('Creator %d running, doing init!' % os.getpid())
            keys_list = self._init_keys_list()
            for item in keys_list:
                if not self.m_keylist_queue.full():
                    self._put(item)

        else:
            # waiting for init finished
            logger.debug('Creator %d running, waiting init done!' % os.getpid())
            while not self.m_ready_evt.is_set():
                if self._idle(1):
                    return
        logger.info('Creator %d init done!' % os.getpid())

        self._generate_keys_handle()

        # clean multiprocess queue
        self.m_keylist_queue.close()
        while not self.m_keylist_queue.empty():
            self.m_keylist_queue.get(1)

        logger.info('key pool creator(%d) exits' % os.getpid())
        return
        pass

    # # Handler for private keys generate requests.
    #  @brief Handler would decide wether to generate keys based on the CPU usage.
    #  @param self The pointer of the object.
    def _generate_keys_handle(self):
        while True:
            # check cpu usage
            usage = get_current_cpu_percent()
            if self.m_keylist_queue.full() or (usage >= defs.KEYPL_CPU_LIMIT):
                if self._idle(defs.KEYPL_DEFAULT_GEN_PERIOD):
                    break
            else:
                logger.info('Creator %d:cpu %f, ready to generate keys!\n' % (os.getpid(), usage))
                tmpkeylist = generate_keys(defs.KEYPL_MAX_CNT, self.m_stop_evt, True)
                if not self._put(tmpkeylist):
                    # delete key files
                    self._remove_key_files(None, tmpkeylist)

        logger.info('Creator handler exits!')
        pass

    # #Loads the old private keys at init step.
    # @param self The pointer of the object.
    def _init_keys_list(self):
        if os.path.exists(self.m_key_dir) is False:
            os.mkdir(self.m_key_dir)
        keys_list = []
        keys_item = []
        for dirpath, dirnames, filenames in os.walk(self.m_key_dir):
            for filename in filenames:
                fd = open(self.m_key_dir + '/' + filename, 'r')
                content = fd.read()
                fd.close()
                key_val = {'fn':filename, 'content':content}
                keys_item.append(key_val)

        if len(keys_item) <= defs.KEYPL_MAX_CNT:
            logger.info('Remain %d keys, less than one group %d keys, generating keys!' % (len(keys_item), defs.KEYPL_MAX_CNT))
            keys_list.append(keys_item + generate_keys((defs.KEYPL_MAX_CNT - len(keys_item)), self.m_stop_evt, True))
        else:
            logger.info('Remain %d keys, more than one group %d keys, dividing keys!' % (len(keys_item), defs.KEYPL_MAX_CNT))
            start_pos = 0
            end_pos = defs.KEYPL_MAX_CNT
            while end_pos <= len(keys_item):
                temp_item = keys_item[start_pos:end_pos]
                keys_list.append(temp_item)
                start_pos = end_pos
                end_pos = end_pos + defs.KEYPL_MAX_CNT

        return keys_list
        pass

    # #Put the new keys into the key queue.
    # @param  self The pointer of the object.
    # @param  keys_list Lists of the private keys.
    def _put(self, keys_list):
        if keys_list:
            if self.m_keylist_queue.full():
                return False
            try:
                self.m_keylist_queue.put(keys_list, False)  # ready for using
            except Queue.Full:
                return False
            # notice
            self.m_ready_evt.set()
        return True
        pass

    # #Remove key file
    # @param  self The pointer of the object.
    # @param  kname Name of the key file.
    # @param  klist List of the key files
    def _remove_key_files(self, kname, klist):
        if kname:
            try:
                os.remove(self.m_key_dir + '/' + kname)
            except:
                pass
        if len(klist):
            for item in klist:
                try:
                    os.remove(self.m_key_dir + '/' + item['fn'])
                except:
                    pass
        pass

    # #Idle for a period
    # @param self The pointer of the object.
    # @param sec The seconds for idling.
    def _idle(self, sec=0):
        if sec > 0:
            self.m_stop_evt.wait(sec)
        return self.m_stop_evt.is_set()
        pass

# end class

