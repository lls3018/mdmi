#!/usr/bin/env python2.6
# encoding=utf-8

import json
import sys
import os
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
from hosted_access import HostedAccess
from utils import logger

DEVRES_TEMPLATE_STR = '/rs/v-%d/ou-devices/udid-%s'
DEVSEARCH_TEMPLATE_STR = '/rs/v-%d/search'
BULK_OP_URL = '/rs/v-%d/bulk'
DEVDN_TEMPLATE_STR = 'udid=%s,ou=devices,dc=blackspider,dc=com'

class HostedDevice(object):
    '''
    class HostedDevice
        This class implements the access RS to get device information.
    
    Attributes:
        m_udid: udid of the device
        m_ver: Version of the resource, default value 1.
    '''
    def __init__(self, udid=None, version=1):
        self.m_udid = None
        self.set_udid(udid)
        self.m_ver = version
        pass

    def set_udid(self, udid):
        '''
        Set udid value

        Params:
            udid: UDID in string.

        Return:
            None.
        '''
        if udid:
            self.m_udid = str(udid)
        pass

    def do_insert(self, devinfo=None):
        '''
        Insert one new device information to RS

        Params:
            devinfo: Detail information of the device.

        Return:
            Instance object of class RestResult;
            Exception message
        '''
        if not self.m_udid:
            raise Exception('Require device UDID!')
        resource = DEVRES_TEMPLATE_STR % (self.m_ver, self.m_udid)
        if isinstance(devinfo, dict):
            temp = devinfo
        elif isinstance(devinfo, basestring):
            temp = json.loads(devinfo)
        else:
            raise Exception('Invalid input!')

        temp = {'attributes':temp}
        data = json.dumps(temp)

        wrest = HostedAccess()
        logger.debug('Insert new device info - resource:%s, data:%s' % (resource, data))
        retval = wrest.do_access(resource, 'PUT', data=data, headers=None)
        del wrest
        return retval

    def do_update(self, udid=None, attributes=None):
        '''
        Update one device information to RS

        Params:
            attributes: Attributes of the devicd information.

        Return:
            Instance object of class RestResult;
            Exception message
        '''
        if udid:
            udid_str = str(udid)
        else:
            udid_str = self.m_udid
        if not udid_str:
            raise Exception('Require device UDID!')
        resource = DEVRES_TEMPLATE_STR % (self.m_ver, udid_str)
        if isinstance(attributes, list):
            attr = json.dumps(attributes)
        elif isinstance(attributes, basestring):
            attr = attributes
        else:
            raise Exception('Invalid input!')

        content = {
                        'method':'modify',
                        'params':attributes,
                    }
        data = json.dumps(content)
        wrest = HostedAccess()
        logger.debug('Update device info - resource:%s, data:%s' % (resource, data))
        retval = wrest.do_access(resource, 'POST', data=data, headers=None)
        del wrest
        return retval

    def do_get(self, **conditions):
        '''
        Get one device information from RS

        Params:
            conditions: The conditions for device selecting.

        Return:
            One dict with device information.
            Exception message
        '''
        if self.m_udid:  # search by udid
            resource = DEVRES_TEMPLATE_STR % (self.m_ver, self.m_udid)
            method = 'GET'
            post_data = None
        else:  # without udid
            if conditions:
                resource = DEVSEARCH_TEMPLATE_STR % self.m_ver
                method = 'POST'
                post_data = '{"base":"ou=devices", "filter":"(&(objectClass=mobileDevice)'
                for cond in conditions:
                    temp_str = '(%s=%s)' % (str(cond), str(conditions[cond]))
                    post_data = post_data + temp_str
                post_data = ''.join([post_data,')"}'])
            else:
                raise Exception('Require device UDID or conditions for searching!')
        logger.debug('Get one device info - resource:%s' % (resource))
        wrest = HostedAccess()
        devinfo = wrest.do_access(resource, method, data=post_data, headers=None)
        del wrest
        return devinfo

    def get_devices_by_owner(self, deviceowner):
        '''
        get devices by device owner
        '''
        if deviceowner:
            resource = DEVSEARCH_TEMPLATE_STR % self.m_ver
            method = 'POST'
            post_data = '{"base":"ou=devices", "filter":"(&(objectClass=mobileDevice)(deviceOwner=%s))"}' % deviceowner
        else:
            raise Exception('Require device owner for searching!')
        logger.debug('Get devices by device owner - resource:%s' % (resource))
        wrest = HostedAccess()
        devinfo = wrest.do_access(resource, method, data=post_data, headers=None)
        del wrest
        return devinfo

    def do_get_many(self, idx, max, sortby, **conditions):
        '''
        Get devices' information from RS

        Params:
            idx: Page index number. (0 ~ )
            max: Page size.
            sortby: Sort condition string.
            conditions: The conditions for device selecting.

        Return:
            One dict with devices information.
            Exception message
        '''
        offset_val = idx * max + 1
        after_val = max - 1
        vlv_str = '{"sort":["%s"],"vlv":{"before":0,"after":%d,"offset":%d},' % (sortby, after_val, offset_val)
        resource = DEVSEARCH_TEMPLATE_STR % self.m_ver
        method = 'POST'
        post_data = ''.join([vlv_str, '"base":"ou=devices", "filter":"(&(objectClass=mobileDevice)'])
        if conditions:
            for k,v in conditions.iteritems():
                cond_str = '(%s=%s)' % (k, str(v))
                post_data = ''.join([post_data, cond_str])
        post_data = ''.join([post_data, ')"}'])
        logger.debug('Get %d devices info - resource:%s, data:%s' % (max, resource, repr(post_data)))
        wrest = HostedAccess()
        devinfo = wrest.do_access(resource, method, data=post_data, headers=None)
        del wrest
        return devinfo

    def format_insert_data(self, source=None, **attributes):
        '''
        Format data structure for inserting device information.

        Params:
            source : Input dict, if source is None, function would return a new dict. If source is been set, attribute would be append to this dict.
            attributes : Name and value of the attribute.

        Return:
            One dict with source and attributes
        '''
        if source:
            assert(isinstance(source, dict))
            retval = source
        else:
            retval = {}

        if attributes:
            retval.update(attributes)

        return retval
        pass

    def format_update_data(self, source=None, type='replace', **attributes):
        '''
        Format data structure for updating device information.

        Params:
            source : Input LIST, if source is None, function would return a new List. If source is been set, attribute would be append to this LIST.
            type : Operation type for the specific attribute.
            attributes : Name and value of the attribute, str type required.

        Return:
            One list with source and attributes
        '''
        if source:
            assert(isinstance(source, list))
            retval = source
        else:
            retval = []

        for key in attributes:  # visit every attribute
            content = {
                        'type':type,
                        'attribute':key,
                        'values':attributes[key]
                    }
            if content:
                retval.append(content)
        return retval
        pass

    def format_bulk_data(self, source=None, udid=None, attributes=None, method=None):
        '''
        Generate data for bulk operation. 

        Params:
            source: Input LIST, if source is None, function would return a new List. If source is been set, attribute would be append to this LIST.
            udid:   device UDID
            attributes: device attributes generated by format_insert_data or format_update_data
            method:
                if attributes generated by format_insert_data, method should be 'add'
                if attributes generated by format_update_data, method should be 'modify'

        Return:
            list in certain format for bulk operation
        '''
        if source:
            assert(isinstance(source, list))
            retval = source
        else:
            retval = []

        if not udid:
            raise Exception('Require device UDID!')
        udid_str = str(udid)

        if not isinstance(attributes, list) and not isinstance(attributes, dict):
            raise Exception('Invalid input!')

        if method not in ['add', 'modify']:
            raise Exception('Invalid method!')

        if method == 'add':
            params = {'attributes':attributes}
        else:   #'modify'
            params = attributes

        dn = DEVDN_TEMPLATE_STR % udid_str

        content = {
                        'method':method,
                        'dn':dn,
                        'params':params,
                    }

        retval.append(content)

        return retval

    def do_bulk_op(self, content):
        '''
        Bulk add or/and update device information into RS

        Params:
            content:    data in a specific format, generated by format_bulk_data

        Return:
            instance object of class RestResult;
            exception message
        '''
        if isinstance(content, list):
            data = json.dumps(content)
        elif isinstance(attributes, basestring):
            data = content
        else:
            raise Exception('Invalid content!')

        resource = BULK_OP_URL % self.m_ver

        wrest = HostedAccess()
        logger.debug('bulk operation info - resource:%s, data:%s' % (resource, data))
        retval = wrest.do_access(resource, 'POST', data=data, headers=None)
        del wrest
        return retval

    def get_device_by_serial_number(self, serial_number):
        '''
        Get device info by device serial number.

        Params:
            serial_number:  device serial number

        Return:
            device info dict
        '''
        if type(serial_number) != str:
            raise Exception('device serial number should be a string')
        conditions = {"deviceSerialNumber": serial_number}
        devinfo = self.do_get(**conditions)
        jobj = json.loads(devinfo.content)

        device_num = len(jobj)
        if device_num  < 1:
            raise Exception('No device found')
        if device_num   > 1:
            raise Exception('found %d devices by serial number %s' % (device_num , serial_number))

        return jobj[0]

# end of HostedDevice
