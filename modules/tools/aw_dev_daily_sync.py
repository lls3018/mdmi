from tools_base import DeviceSyncThread
import sys
import time
import threading
import Queue
sys.path.append("/opt/mdmi/modules/")
from utils import logger
from airwatch.device import AirwatchDevice
from hosteddb.hosted_account import HostedAccount
from tools_base import DeviceSyncThread
from tools_base import get_dict_value2

class AW_DeviceSyncHandler(DeviceSyncThread):
    def __init__(self, account):
        self.aw_account = -1
        try:
            self.aw_account = int(account)
        except Exception, e:
            raise Exception('Input account error! %s' % repr(e))
        self.m_defect_devs = []
        super(AW_DeviceSyncHandler, self).__init__()
        pass

    def run(self):
        logger.info('Devices\' information sync with airwatch started at %s under account %d!' % (str(time.time()), self.aw_account))
        try:
            logger.info('Step 1: Get device information from RS.')
            rs_retval = self._get_devinfo_from_rs()
            logger.debug('Account %d includes %d device needed sync with airwatch!' % (self.aw_account, rs_retval))
            if rs_retval <= 0:
                # report
                return  # exit, no work to do

            logger.info('Step 2: Get device information from airwatch.')
            aw_retval = self._get_devinfo_from_aw(self.devinfo_original_queue, self.devinfo_refresh_queue)
            logger.debug('Account %d, get %d device information from airwatch!' % (self.aw_account, aw_retval))
            if (aw_retval != rs_retval):
                #The devices do not exist in airwatch needed to be updated as unenroll status.
                logger.warning('Account %d, Original device number (%d) and refresh device number (%d) NOT match!' % (self.aw_account, rs_retval, aw_retval))

            logger.info('Step 3: Sync device information to RS.')
            sync_retval = self._sync_devinfo()
            logger.debug('Account %d, sync %d device information with RS finished!' % (self.aw_account, sync_retval))
            if (aw_retval != sync_retval):
                #causes of updating RS fail
                logger.warning('Account %d, Refresh device number (%d) and Sync device number (%d) NOT match!' % (self.aw_account, aw_retval, sync_retval))

            # Step 4: Update the defect devices to be unenroll.
            if self.m_defect_devs:
                defect_cnt = len(self.m_defect_devs)
                logger.info('Step 4: Set %d devices to be "unenroll" status!' % defect_cnt)
                ok_cnt = self._unenroll_dev_status(self.m_defect_devs)
                if defect_cnt != ok_cnt:
                    logger.warning('Account %d, Set %d devices to be "unenroll status failed!"' % (self.aw_account, (defect_cnt - ok_cnt)))
            # Step 5: Report
        except Exception, e:
            logger.error(repr(e))
        logger.info('Devices\' information sync with airwatch end at %s!' % str(time.time()))
        pass

    def stop(self):
        pass

    def _get_devinfo_from_rs(self):
        return super(AW_DeviceSyncHandler, self)._get_devinfo_from_rs(100, deviceEnrollmentStatus=1, account=self.aw_account)
        pass

    def _get_devinfo_from_aw(self, src_queue, dest_queue):
        aw_dev = AirwatchDevice(self.aw_account)
        list_udids = []
        while src_queue.qsize() > 0:
            devitems = src_queue.get(True)
            for dev in devitems:
                try:
                    udid = dev['attributes'].get('UDID')[0]
                    if udid and (udid != 'NA'):  # try get udid
                        list_udids.append(udid.lower()) #keep all string in lower
                    else:
                        logger.warning('Unknow device: %s' % repr(dev))
                except Exception, e:
                    logger.error('Unknow device, error info:%s' % repr(e))
                    pass
        #Should be filled at first
        self.m_defect_devs = list_udids
        if list_udids:
            self._do_get_from_aw(dest_queue, list_udids, aw_dev.get_by_udids, aw_dev.get_by_udid)
        #save all devices udid in local cache
        del aw_dev
        return dest_queue.qsize()
        pass

    def _sync_devinfo(self):
        retcnt = 0
        while not self.devinfo_refresh_queue.empty():
            devinfo = self.devinfo_refresh_queue.get(True)
            hdevinfo = self._convert_into_rs_format(devinfo)
            udid = devinfo.get('Udid').lower()
            if udid:
                if (0 == super(AW_DeviceSyncHandler, self)._sync_devinfo(udid, hdevinfo)):
                    retcnt = retcnt + 1
                #delete from local records, if the device exists in airwatch
                if udid in self.m_defect_devs:
                    self.m_defect_devs.remove(udid)
        return retcnt
        pass

    def _unenroll_dev_status(self, defect_list):
        retcnt = 0
        for udid in defect_list:
            if (0 == super(AW_DeviceSyncHandler, self)._sync_devinfo(udid, {'deviceEnrollmentStatus':2})):
                retcnt = retcnt + 1
        return retcnt
        pass

    def _convert_into_rs_format(self, aw_dev_info):
        hosted_dev_info = {}
        # Note: there would be fail when the value of the attributes equals None or '', please avoid it existing.
        tmpval = aw_dev_info.get('UserEmailAddress')
        if tmpval:
            hosted_dev_info['deviceOwner'] = tmpval
        tmpval = aw_dev_info.get('Model')
        if tmpval:
            hosted_dev_info['displayType'] = tmpval
        tmpval = aw_dev_info.get('SerialNumber')
        if tmpval:
            hosted_dev_info['deviceSerialNumber'] = tmpval
        tmpval = aw_dev_info.get('MacAddress')
        if tmpval:
            hosted_dev_info['wifiMacAddress'] = tmpval
        tmpval = aw_dev_info.get('Imei')
        if tmpval:
            hosted_dev_info['imei'] = tmpval
        tmpval = aw_dev_info.get('DeviceFriendlyName')
        if tmpval:
            hosted_dev_info['deviceFriendlyName'] = tmpval
        tmpval = aw_dev_info.get('LocationGroupName')
        if tmpval:
            hosted_dev_info['locationGroupName'] = tmpval
        tmpval = aw_dev_info.get('OperatingSystem')
        if tmpval:
            hosted_dev_info['deviceOsVersion'] = tmpval
        tmpval = aw_dev_info.get('Id')
        if tmpval:
            hosted_dev_info['mdmDeviceId'] = tmpval
        tmpval = aw_dev_info.get('CompromisedStatus')
        if tmpval:
            hosted_dev_info['deviceCompromisedStatus'] = tmpval
        tmpval = aw_dev_info.get('UserId')
        if tmpval:
            hosted_dev_info['mdmUserId'] = tmpval

        hosted_dev_info['deviceOwnership'] = get_dict_value2(aw_dev_info, 'Ownership', 0, C=1, S=2, E=3, Undefined=4)
        hosted_dev_info['devicePlatform'] = get_dict_value2(aw_dev_info, 'Platform', 0, Apple=1, Android=2)
        hosted_dev_info['deviceEnrollmentStatus'] = get_dict_value2(aw_dev_info, 'EnrollmentStatus', 0, Enrolled=1, Unenrolled=2)
        hosted_dev_info['deviceComplianceStatus'] = get_dict_value2(aw_dev_info, 'ComplianceStatus', 0, **{'Non-compliant':1, 'Compliant':2, 'NotAvailable':3})

        hosted_dev_info['status'] = 'good'
        hosted_dev_info['objectClass'] = 'mobileDevice'
        
        # logger.debug('Device info:%s' % repr(hosted_dev_info))
        return hosted_dev_info
        pass

    def _do_get_from_aw(self, dest_queue, src_list, do_get_many, do_get):
        if src_list:
            try:
                result = do_get_many(src_list)
                if isinstance(result, dict):
                    devlist = result.get('Devices')
                    for dev in devlist:
                        dest_queue.put(dev)  # insert
            except Exception, e:
                # Error occurred, get device information one by one
                for dev_attr in src_list:
                    try:
                        result = do_get(dev_attr)
                        dest_queue.put(result)
                    except Exception, e:
                        logger.error('No such device info:%s' % dev_attr)
        pass


class AW_DeviceSyncController(threading.Thread):
    def __init__(self):
        self.m_handlers = []
        threading.Thread.__init__(self)
        pass

    def run(self):
        # Get the accounts that include airwatch information
        accounts = self._get_aw_accounts()
        if accounts:
            for account in accounts:
                handler = AW_DeviceSyncHandler(account)
                handler.start()
                self.m_handlers.append(handler)

        if self.m_handlers:
            for handler in self.m_handlers:
                handler.join()
        pass

    def stop(self):
        pass
    
    def _get_aw_accounts(self):
        # temp
        return HostedAccount().get_airwatch_account_ids()
        pass


