import threading
import Queue
import sys
import json
sys.path.append("/opt/mdmi/modules/")
from utils import logger
from hosteddb.hosted_device import HostedDevice

def get_dict_value2(srcdict, key, defval, **expect):
    for ekey in expect:
        if srcdict[key] == ekey:
            return expect[ekey]
    return defval
    pass


class DeviceSyncThread(threading.Thread):
    def __init__(self):
        self.devinfo_original_queue = Queue.Queue()
        self.devinfo_refresh_queue = Queue.Queue()
        threading.Thread.__init__(self)
        pass

    def run(self):
        pass

    def stop(self):
        if self.devinfo_original_queue:
            while not self.devinfo_original_queue.empty():
                self.devinfo_original_queue.get(True)
            self.devinfo_original_queue = None
        if self.devinfo_refresh_queue:
            while not self.devinfo_refresh_queue.empty():
                self.devinfo_refresh_queue.get(True)
            self.devinfo_refresh_queue = None
        pass

    def _get_devinfo_from_rs(self, max, **attributes):
        # return number of the device needed to be updated.
        rs_dev = HostedDevice()
        idx = 0
        total = 0
        try:
            while idx >= 0:
                result = rs_dev.do_get_many(idx, max, 'account', **attributes)
                if result.code >= 200 and result.code < 300:
                    length = self._dispatch_original_devinfo(result.content, self.devinfo_original_queue)
                    if length == max:
                        idx = idx + 1  # more
                    else:
                        idx = -1  # get all
                    total = total + length
            return total
        except Exception, e:
            logger.error('Get device information from RS error! %s' % repr(e))
            return total
        finally:
            del rs_dev
        pass

    def _dispatch_original_devinfo(self, devinfo, destqueue):
        try:
            devlist = json.loads(devinfo)
        except Exception, e:
            logger.error('Device information does NOT format as json! %s' % repr(e))
            return 0
        
        retval = len(devlist)
        if (retval > 0):
            destqueue.put(devlist)
        return retval
        pass

    def _sync_devinfo(self, udid, devinfo):
        #remove invalid keys and values
        dev_item = dict(devinfo) #copy one to keep input not be changed.
        for k in dev_item.keys():
            if not dev_item[k]: #include '' and None
                del dev_item[k]
                
        devobj = HostedDevice(udid)
        dev_data = devobj.format_update_data(None, 'replace', **dev_item)
        logger.info('Update device information! UDID:%s, data:%s' % (str(udid), repr(dev_data)))
        try:
            result = devobj.do_update(attributes=dev_data)
            if result.code >= 200 and result.code < 300:
                logger.info('Update device %s information success!' % str(udid))
                return 0
            else:
                logger.error('Update device %s information failed!' % str(udid))
                return -1
        except Exception, e:
            logger.error('Update device information failed! error:%s' % repr(e))
            return -1
        finally:
            del devobj
        pass

