from threading import Thread, Condition, Event

import sys
if not '/opt/mdmi/modules' in sys.path:
    sys.path.append('/opt/mdmi/modules')

from utils import logger

class TaskHandlerThread(Thread):
    def __init__(self, index):
        super(self.__class__, self).__init__()
        self.__condition = Condition()
        self.__stop_event = Event()
        self.__ready = False
        self._task_handler = None
        self._index = index

        self.__stop_event.clear()

        self.name = 'task-thread-%d' % index
        logger.info('task thread %s is ready to run...', self.name)

    def run(self):
        logger.info('task thread %s is running...', self.name)
        while not self.__stop_event.isSet():
            try:
                self.__condition.acquire()
                self.__ready = True
                self.__condition.wait()
            except Exception:
                pass
            else:
                self.__ready = False
                if not self._task_handler:
                    continue
                try:
                    logger.debug('task thread %s begin to handle %s task', self.name, self._task_handler._handler_type)

                    self._task_handler.do_handle()
                except Exception as e:
                    logger.error('Exception occurred in %s, %s', self.name, e)
                    # TODO should add task into retry thread
                finally:
                    logger.debug('task thread %s finish to handle %s task', self.name, self._task_handler._handler_type)
                    self._task_handler = None
            finally:
                self.__condition.release()

    def stop(self):
        logger.info('stopping task thread %s...', self.name)
        self.__stop_event.set()
        self.__condition.acquire()
        self.__condition.notify()
        self.__condition.release()
        logger.info('task thread %s stopped', self.name)

    def notify(self):
        self.__condition.acquire()
        self.__condition.notify()
        self.__condition.release()

    def to_busy(self, task_handler):
        if self.__condition.acquire(False):
            if not self.__ready or self._task_handler:
                self.__condition.release()
                return False
            self._task_handler = task_handler
            self.__condition.notify()
            self.__condition.release()
            return True

        return False

    def get_index(self):
        return self._index
