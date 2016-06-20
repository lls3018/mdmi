import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')

import json
from multiprocessing import Queue, Event
from Queue import Full
from utils import logger
from threading import Lock

from service_config import g_config_thread_pool_max_size

class TaskCache(object):
    def __init__(self, maxsize=0):
        self.__queue = Queue(maxsize)
        self.__maxsize = maxsize
        self.__full_event = Event()
        self.__stop_event = Event()
        
        self.__full_event.clear()
        self.__stop_event.clear()
        pass
    
    def __del__(self):
        self.__queue.close()
    
    def put_data(self, data, block=True, timeout=0):
        task_data = {}
        
        data = json.loads(data)
        if data['sync_type'] == 'metanate':
            key = ':'.join(['metanate', str(data['account']), data['trans_type'], data['sync_source']])
            task_data['key'] = key
            task_data['value'] = data
        elif data['sync_type'] == 'hybrid':
            key = ':'.join([data['sync_type'], str(data['account'])])
            task_data['key'] = key
            task_data['value'] = data
            
        while not self.__stop_event.is_set():
            try:
                self.__queue.put(task_data, block, timeout)
                logger.debug('put task data (%s, %s) successfully' % (key, data))
                break
            except Full:
                logger.debug('task cache size reachs max size')
                self.full_event.clear()
                self.full_event.wait()
            except Exception, e:
                logger.error('put task data into cache error %s' % repr(e))
                break
        pass
        
    def get(self, block=True, timeout=0):
        pass

    def get_all(self):
        size = self.__queue.qsize()
        task_data_list = []
        
        for i in xrange(size):
            try:
                data = self.__queue.get_nowait()
                task_data_list.append(data)
            except Exception as e:
                logger.warning('error occured in getting No.%d data from queue, queue size: %d, error: %s', i, size, e)
                break
        
        return task_data_list

    def is_full(self):
        return self._queue.full()
    
    def is_empty(self):
        return self.__queue.empty()
    
    def size(self):
        return self._queue.qsize()
    
    def notify(self):
        self.__full_event.set()
        
    def stop(self):
        self.__stop_event.set()

class TaskCacheDict:
    def __init__(self):
        self.__lock = Lock()
        self.__cache_dict = {}
        self.__retry_cache_array = []
        self.__retry_index = 0
        pass

    def put(self, key, value):
        with self.__lock:
            if self.__cache_dict.has_key(key):
                if isinstance(value, (list, tuple, set)):
                    self.__cache_dict[key].extend(value)
                else:
                    self.__cache_dict[key].append(value)
            else:
                if isinstance(value, (list, tuple, set)):
                    self.__cache_dict[key] = list(value)
                else:
                    self.__cache_dict[key] = [value]

    def put_retry(self, key, value):
        if key.startswith('retry:'):
            return

        with self.__lock:
            if isinstance(value, (list, tuple, set)):
                for t in value:
                        k = ':'.join(['retry', str(self.__retry_index), key])
                        self._increase_index()
                        self.__retry_cache_array.append((k, t))
            else:
                k = ':'.join(['retry', str(self.__retry_index), key])
                self._increase_index()
                self.__retry_cache_array.append((k, value))

    def get(self):
        with self.__lock:
            r = self.__cache_dict
            self.__cache_dict = {}
            retry_size = g_config_thread_pool_max_size.value / 2
            retry_array = self.__retry_cache_array[:retry_size]  # half of thread
            self.__retry_cache_array = self.__retry_cache_array[retry_size:]  # half of thread
            for a in retry_array:
                r[a[0]] = [a[1]]


            return r

    def _increase_index(self):
        self.__retry_index += 1
        if self.__retry_index >= sys.maxint:
            self.__retry_index = 0
