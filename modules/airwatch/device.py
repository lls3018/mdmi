# -*- coding: utf-8 -*-
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
from airwatch.base import AirwatchBase

class AirwatchDevice(AirwatchBase):
    def __init__(self, account_id):
        super(AirwatchDevice, self).__init__(account_id)

    def __del__(self):
        super(AirwatchDevice, self).__del__()

    def do_action_by_sometype(self, device_info, deviceid_type=None, type_value=None, http_method="GET", data=None, content_type="application/json"):
        if deviceid_type and type_value:
            resource = "/API/v1/mdm/devices/{deviceidtype}/{value}/{info}".format(deviceidtype=deviceid_type, value=type_value, info=device_info)
        elif deviceid_type:
            resource = "/API/v1/mdm/devices/{deviceid}/{info}".format(deviceid=deviceid_type, info=device_info)
        elif type_value:
            resource = "/API/v1/mdm/devices/{value}/{info}".format(value=type_value, info=device_info)
        else:
            resource = "/API/v1/mdm/devices/{info}".format(info=device_info)

        http_headers = self.aw_headers
        if content_type:
            http_headers['Content-Type'] = content_type
        result = self.rest.do_access(resource, http_method, data, http_headers)
        if not result:
            return result
        if result.code == 204:
            return None
        body = self._parse_result(result)
        if result.code >= 200 and result.code < 300:
            if not body:
                return type_value
            if type(body) == dict:
                if body.has_key('Total'):
                    if body.has_key('Devices'):
                        devices = body['Devices']
                        for d in devices:
                            if type(d['Id']) == dict and d['Id'].has_key('Value'):
                                d['Id'] = d['Id']['Value']
                    elif body.has_key('DeviceApps'):
                        apps = body['DeviceApps']
                        for a in apps:
                            if type(a['Id']) == dict and a['Id'].has_key('Value'):
                                a['Id'] = a['Id']['Value']
                    elif body.has_key('DeviceCertificates'):
                        certs = body['DeviceCertificates']
                        for c in certs:
                            if c.has_key('Id') and type(c['Id']) == dict and c['Id'].has_key('Value'):
                                c['Id'] = c['Id']['Value']
                elif body.has_key('Id'):
                    if type(body['Id']) == dict and body['Id'].has_key('Value'):
                        body['Id'] = body['Id']['Value']
            elif type(body) == list:
                for c in body:
                    if c.has_key('Id') and type(c['Id']) == dict and c['Id'].has_key('Value'):
                        c['Id'] = c['Id']['Value']
                    if c.has_key('DeviceId') and type(c['DeviceId']) == dict and c['DeviceId'].has_key('Value'):
                        c['DeviceId'] = c['DeviceId']['Value']
            elif type(body) == str and body == 'null':
                return type_value
            return body
        return body

    # Device information
    def get(self, device_id):
        """
        Retrieves information about the device identified by device ID.
        Parameter   Notes
            device_id   The device ID.
        Returns: a dict contains device information on success, or a dict contains error on failure.
        """
        # return self.get_device_info_by_sometype(None, device_id)
        return self.do_action_by_sometype(device_id)

    def get_by_macaddress(self, macaddress):
        """
        Retrieves information about the device identified by MAC address.
        Parameter   Notes
            macaddress  The MAC address of the device.
        Returns: a dict contains device information on success, or a dict contains error on failure.
        """
        # return self.get_device_info_by_sometype("macaddress", macaddress)
        return self.do_action_by_sometype(macaddress, "macaddress")

    def get_by_serialnumber(self, serialnumber):
        """
        Retrieves information about the device identified by serial number.
        Parameter   Notes
            serialnumber    The serial number of the device.
        Returns: a dict contains device information on success, or a dict contains error on failure.
        """
        # return self.get_device_info_by_sometype("serialnumber", serialnumber)
        return self.do_action_by_sometype(serialnumber, "serialnumber")

    def get_by_udid(self, udid):
        """
        Retrieves information about the device identified by UDID.
        Parameter   Notes
            udid    The UDID to search for.
        Returns: a dict contains device information on success, or a dict contains error on failure.
        """
        # return self.get_device_info_by_sometype("udid", udid)
        return self.do_action_by_sometype(udid, "udid")

    def bulksettings(self):
        # return self.get_device_info_by_sometype(None, "bulksettings")
        return self.do_action_by_sometype("bulksettings")

    def get_by_ids(self, data):
        """
        Retrieves information about multiple devices identified by device ID.
        Parameter Notes
            data: a list of device id
        Returns: a list of device on success, or a dict contains error on failure.
        """
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("id", http_method="POST", data=data, content_type="application/xml")

    def get_by_macaddresses(self, data):
        """
        Retrieves information about multiple devices identified by MAC address.
        Parameter Notes
            data: a list of device MAC address
        Returns: a list of device on success, or a dict contains error on failure.
        """
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("macaddress", http_method="POST", data=data, content_type="application/xml")

    def get_by_serialnumbers(self, data):
        """
        Retrieves information about multiple devices identified by serial number
        Parameter Notes
            data: a list of device serial number
        Returns: a list of device on success, or a dict contains error on failure.
        """
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("serialnumber", http_method="POST", data=data, content_type="application/xml")

    def get_by_udids(self, data):
        """
        Retrieves information about multiple devices identified by UDID
        Parameter Notes
            data: a list of device UDID
        Returns: a list of device on success, or a dict contains error on failure.
        """
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("udid", http_method="POST", data=data, content_type="application/xml")

    # Enrollment status
    def get_apps_by_id(self, device_id):
        return self.do_action_by_sometype("apps", type_value=device_id)

    def get_apps_by_macaddress(self, macaddress):
        return self.do_action_by_sometype("apps", "macaddress", macaddress)

    def get_apps_by_serialnumber(self, serialnumber):
        return self.do_action_by_sometype("apps", "serialnumber", serialnumber)

    def get_apps_by_udid(self, udid):
        return self.do_action_by_sometype("apps", "udid", udid)

    def get_certificates_by_id(self, device_id):
        """
        Retrieves certificate details of the device identified by device ID.
        Parameter   Notes
            device_id   The device ID.
        Returns: a dict contians device certificate on success or a dict contains error on failure.
        """
        return self.do_action_by_sometype("certificates", type_value=device_id)

    def get_certificates_by_macaddress(self, macaddress):
        """
        Retrieves certificate details of the device identified by MAC address.
        Parameter   Notes
            macaddress  The MAC address of the device.
        Returns: a dict contians device certificate on success or a dict contains error on failure.
        """
        return self.do_action_by_sometype("certificates", "macaddress", type_value=macaddress)

    def get_certificates_by_serialnumber(self, serialnumber):
        """
        Retrieves certificate details of the device identified by serial number.
        Parameter   Notes
            serialnumber    The serial number of the device.
        Returns: a dict contians device certificate on success or a dict contains error on failure.
        """
        return self.do_action_by_sometype("certificates", "serialnumber", type_value=serialnumber)

    def get_certificates_by_udid(self, udid):
        """
        Retrieves certificate details of the device identified by UDID.
        Parameter   Notes
            udid    The UDID of the device.
        Returns: a dict contians device certificate on success or a dict contains error on failure.
        """
        return self.do_action_by_sometype("certificates", "udid", type_value=udid)

    def get_compliance_by_id(self, device_id):
        return self.do_action_by_sometype("compliance", type_value=device_id)

    def get_compliance_by_macaddress(self, macaddress):
        return self.do_action_by_sometype("compliance", "macaddress", type_value=macaddress)

    def get_compliance_by_serialnumber(self, serialnumber):
        return self.do_action_by_sometype("compliance", "serialnumber", type_value=serialnumber)

    def get_compliance_by_udid(self, udid):
        return self.do_action_by_sometype("compliance", "udid", type_value=udid)

    def get_content_by_id(self, device_id):
        return self.do_action_by_sometype("content", type_value=device_id)

    def get_content_by_macaddress(self, macaddress):
        return self.do_action_by_sometype("content", "macaddress", type_value=macaddress)

    def get_content_by_serialnumber(self, serialnumber):
        return self.do_action_by_sometype("content", "serialnumber", type_value=serialnumber)

    def get_content_by_udid(self, udid):
        return self.do_action_by_sometype("content", "udid", type_value=udid)

    def get_eventlog_by_id(self, device_id):
        return self.do_action_by_sometype("eventlog", type_value=device_id)

    def get_eventlog_by_macaddress(self, macaddress):
        return self.do_action_by_sometype("eventlog", "macaddress", type_value=macaddress)

    def get_eventlog_by_serialnumber(self, serialnumber):
        return self.do_action_by_sometype("eventlog", "serialnumber", type_value=serialnumber)

    def get_eventlog_by_udid(self, udid):
        return self.do_action_by_sometype("eventlog", "udid", type_value=udid)

    def get_gps_by_id(self, device_id):
        """
        Retrieves the GPS coordinates of the device identified by device ID.
        Parameter   Notes
            device_id   The device ID.
        Returns: a list contains gps coordinates on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("gps", type_value=device_id)

    def get_gps_by_macaddress(self, macaddress):
        """
        Retrieves the GPS coordinates of the device identified by MAC address.
        Parameter   Notes
            macaddress  The MAC address of the device.
        Returns: a list contains gps coordinates on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("gps", "macaddress", type_value=macaddress)

    def get_gps_by_serialnumber(self, serialnumber):
        """
        Retrieves the GPS coordinates of the device identified by serial number.
        Parameter   Notes
            serialnumber    The serial number of the device.
        Returns: a list contains gps coordinates on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("gps", "serialnumber", type_value=serialnumber)

    def get_gps_by_udid(self, udid):
        """
        Retrieves the GPS coordinates of the device identified by UDID.
        Parameter   Notes
            udid    The UDID of the device.
        Returns: a list contains gps coordinates on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("gps", "udid", type_value=udid)

    def get_security_by_id(self, device_id):
        """
        Retrieves the security information of the device identified by device ID.
        Parameter   Notes
            device_id   The device ID.
        Returns: a dict contains security information of device on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("security", type_value=device_id)

    def get_security_by_macaddress(self, macaddress):
        """
        Retrieves the security information of the device identified by MAC address.
        Parameter   Notes
            macaddress  The MAC address of the device.
        Returns: a dict contains security information of device on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("security", "macaddress", type_value=macaddress)

    def get_security_by_serialnumber(self, serialnumber):
        """
        Retrieves the security information of the device identified by serial number.
        Parameter   Notes
            serialnumber    The serial number of the device.
        Returns: a dict contains security information of device on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("security", "serialnumber", type_value=serialnumber)

    def get_security_by_udid(self, udid):
        """
        Retrieves the security information of the device identified by UDID.
        Parameter   Notes
            udid    The UDID of the device.
        Returns: a dict contains security information of device on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("security", "udid", type_value=udid)

    def get_network_by_id(self, device_id):
        """
        Retrieves the network information of the device identified by device ID.
        Parameter   Notes
            device_id   The device ID.
        Returns: a dict contains network information of device on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("network", type_value=device_id)

    def get_network_by_macaddress(self, macaddress):
        """
        Retrieves the network information of the device identified by MAC address.
        Parameter   Notes
            macaddress  The MAC address of the device.
        Returns: a dict contains network information of device on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("network", "macaddress", type_value=macaddress)

    def get_network_by_serialnumber(self, serialnumber):
        """
        Retrieves the network information of the device identified by serial number.
        Parameter   Notes
            serialnumber    The serial number of the device.
        Returns: a dict contains network information of device on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("network", "serialnumber", type_value=serialnumber)

    def get_network_by_udid(self, udid):
        """
        Retrieves the network information of the device identified by UDID.
        Parameter   Notes
            udid    The UDID of the device.
        Returns: a dict contains network information of device on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("network", "udid", type_value=udid)

    def get_profiles_by_id(self, device_id):
        return self.do_action_by_sometype("profiles", type_value=device_id)

    def get_profiles_by_macaddress(self, macaddress):
        return self.do_action_by_sometype("profiles", "macaddress", type_value=macaddress)

    def get_profiles_by_serialnumber(self, serialnumber):
        return self.do_action_by_sometype("profiles", "serialnumber", type_value=serialnumber)

    def get_profiles_by_udid(self, udid):
        return self.do_action_by_sometype("profiles", "udid", type_value=udid)

    def get_users_by_id(self, device_id):
        """
        Retrieves the user details of the device identified by device ID.
        Parameter   Notes
            device_id   The device ID.
        Returns: a dict contains user details of device on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("user", type_value=device_id)

    def get_users_by_macaddress(self, macaddress):
        """
        Retrieves the user details of the device identified by MAC address.
        Parameter   Notes
            macaddress  The MAC address of the device.
        Returns: a dict contains user details of device on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("user", "macaddress", type_value=macaddress)

    def get_users_by_serialnumber(self, serialnumber):
        """
        Retrieves the user details of the device identified by serial number.
        Parameter   Notes
            serialnumber    The serial number of the device.
        Returns: a dict contains user details of device on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("user", "serialnumber", type_value=serialnumber)

    def get_users_by_udid(self, udid):
        """
        Retrieves the user details of the device identified by UDID.
        Parameter   Notes
            udid    The UDID of the device.
        Returns: a dict contains user details of device on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("user", "udid", type_value=udid)

    def clearpasscode_by_id(self, device_id):
        """
        Sends a Clear Passcode command to the device identified by device ID.
        Parameter   Notes
            device_id   The device ID.
        Returns: return device_id on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("clearpasscode", type_value=device_id, http_method="POST")

    def clearpasscode_by_macaddress(self, macaddress):
        """
        Sends a Clear Passcode command to the device identified by MAC address.
        Parameter   Notes
            macaddress  The MAC address of the device.
        Returns: return macaddress on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("clearpasscode", "macaddress", macaddress, http_method="POST")

    def clearpasscode_by_serialnumber(self, serialnumber):
        """
        Sends a Clear Passcode command to the device identified by serial number.
        Parameter   Notes
            serialnumber    The serial number of the device.
        Returns: return serialnumber on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("clearpasscode", "serialnumber", serialnumber, http_method="POST")

    def clearpasscode_by_udid(self, udid):
        """
        Sends a Clear Passcode command to the device identified by UDID.
        Parameter   Notes
            udid    The UDID of the device.
        Returns: return udid on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("clearpasscode", "udid", udid, http_method="POST")

    def enterprisewipe_by_id(self, device_id):
        """
        Sends a Enterprise Wipe command to the device identified by device ID.
        Parameter   Notes
            device_id   The device ID.
        Returns: return device_id on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("enterprisewipe", type_value=device_id, http_method="POST")

    def enterprisewipe_by_macaddress(self, macaddress):
        """
        Sends a Enterprise Wipe command to the device identified by MAC address.
        Parameter   Notes
            macaddress  The MAC address of the device.
        Returns: return macaddress on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("enterprisewipe", "macaddress", macaddress, http_method="POST")

    def enterprisewipe_by_serialnumber(self, serialnumber):
        """
        Sends a Enterprise Wipe command to the device identified by serial number.
        Parameter   Notes
            serialnumber    The serial number of the device.
        Returns: return serialnumber on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("enterprisewipe", "serialnumber", serialnumber, http_method="POST")

    def enterprisewipe_by_udid(self, udid):
        """
        Sends a Enterprise Wipe command to the device identified by UDID.
        Parameter   Notes
            udid    The UDID of the device.
        Returns: return udid on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("enterprisewipe", "udid", udid, http_method="POST")

    def enterprisewipe_by_ids(self, data):
        """
        Sends a Enterprise Wipe command to multiple devices identified by device ID.
        Parameter   Notes
            data    a list of device ID.
        Returns: return a dict as following, or a dict contains error on failure.
            {
                "TotalItems":2147483647,
                "AcceptedItems":2147483647,
                "FailedItems":2147483647,
                "Faults":{
                    "ActivityId":"Text value",
                    "Fault":{
                        "ErrorCode":2147483647,
                        "ItemValue":"Text value",
                        "Message":"Text value"
                    }
                }
            }
        """
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("enterprisewipe", http_method="POST", data=data, content_type="application/xml")

    def enterprisewipe_by_macaddresses(self, data):
        """
        Sends a Enterprise Wipe command to multiple devices identified by MAC address.
        Parameter   Notes
            data    a list of MAC address of devices.
        Returns: return a dict as following, or a dict contains error on failure.
            {
                "TotalItems":2147483647,
                "AcceptedItems":2147483647,
                "FailedItems":2147483647,
                "Faults":{
                    "ActivityId":"Text value",
                    "Fault":{
                        "ErrorCode":2147483647,
                        "ItemValue":"Text value",
                        "Message":"Text value"
                    }
                }
            }
        """
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("enterprisewipe", "macaddress", http_method="POST", data=data, content_type="application/xml")

    def enterprisewipe_by_serialnumbers(self, data):
        """
        Sends a Enterprise Wipe command to multiple devices identified by serial number.
        Parameter   Notes
            data    a list of serial number of devices.
        Returns: return a dict as following, or a dict contains error on failure.
            {
                "TotalItems":2147483647,
                "AcceptedItems":2147483647,
                "FailedItems":2147483647,
                "Faults":{
                    "ActivityId":"Text value",
                    "Fault":{
                        "ErrorCode":2147483647,
                        "ItemValue":"Text value",
                        "Message":"Text value"
                    }
                }
            }
        """
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("enterprisewipe", "serialnumber", http_method="POST", data=data, content_type="application/xml")

    def enterprisewipe_by_udids(self, data):  # TODO
        """
        Sends a Enterprise Wipe command to multiple devices identified by UDID.
        Parameter   Notes
            data    a list of UDID of devices.
        Returns: return a dict as following, or a dict contains error on failure.
            {
                "TotalItems":2147483647,
                "AcceptedItems":2147483647,
                "FailedItems":2147483647,
                "Faults":{
                    "ActivityId":"Text value",
                    "Fault":{
                        "ErrorCode":2147483647,
                        "ItemValue":"Text value",
                        "Message":"Text value"
                    }
                }
            }
        """
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("enterprisewipe", "udid", http_method="POST", data=data, content_type="application/xml")

    # Commands - Find   
    def find_device_by_id(self, device_id, data):
        return self.do_action_by_sometype("finddevice", type_value=device_id, http_method="POST", data=data)

    def find_device_by_macaddress(self, macaddress, data):
        return self.do_action_by_sometype("finddevice", "macaddress", macaddress, http_method="POST", data=data)

    def find_device_by_serialnumber(self, serialnumber, data):
        return self.do_action_by_sometype("finddevice", "serialnumber", serialnumber, http_method="POST", data=data)

    def find_device_by_udid(self, udid, data):
        return self.do_action_by_sometype("finddevice", "udid", udid, http_method="POST", data=data)

    # Commands - Lock
    def lockdevice_by_id(self, device_id):
        """
        Sends a Lock command to the device identified by device ID.
        Parameter   Notes
            device_id   The device ID.
        Returns: return device id on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("lockdevice", type_value=device_id, http_method="POST")

    def lockdevice_by_macaddress(self, macaddress):
        """
        Sends a Lock command to the device identified by MAC address.
        Parameter   Notes
            macaddress  The MAC address of the device.
        Returns: return macaddress on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("lockdevice", "macaddress", macaddress, http_method="POST")

    def lockdevice_by_serialnumber(self, serialnumber):
        """
        Sends a Lock command to the device identified by serial number.
        Parameter   Notes
            serialnumber    serial number of the device.
        Returns: return serialnumber on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("lockdevice", "serialnumber", serialnumber, http_method="POST")

    def lockdevice_by_udid(self, udid):
        """
        Sends a Lock command to the device identified by UDID.
        Parameter   Notes
            udid    The UDID of device.
        Returns: return udid on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("lockdevice", "udid", udid, http_method="POST")

    def lockdevice_by_ids(self, data):
        """
        Sends a Lock command to multiple devices identified by device ID.
        Parameter   Notes
            data    a list of device ID.
        Returns: return a dict as following, or a dict contains error on failure.
            {
                "TotalItems":2147483647,
                    "AcceptedItems":2147483647,
                    "FailedItems":2147483647,
                    "Faults":{
                        "ActivityId":"Text value",
                        "Fault":{
                            "ErrorCode":2147483647,
                            "ItemValue":"Text value",
                            "Message":"Text value"
                        }
                    }
            }
        """
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("lockdevice", http_method="POST", data=data, content_type="application/xml")

    def lockdevice_by_macaddresses(self, data):
        """
        Sends a Lock command to multiple devices identified by MAC address.
        Parameter   Notes
            data    a list of MAC address of devices.
        Returns: return a dict as following, or a dict contains error on failure.
            {
                "TotalItems":2147483647,
                    "AcceptedItems":2147483647,
                    "FailedItems":2147483647,
                    "Faults":{
                        "ActivityId":"Text value",
                        "Fault":{
                            "ErrorCode":2147483647,
                            "ItemValue":"Text value",
                            "Message":"Text value"
                        }
                    }
            }
        """
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("lockdevice", "macaddress", http_method="POST", data=data, content_type="application/xml")

    def lockdevice_by_serialnumbers(self, data):
        """
        Sends a Lock command to multiple devices identified by serial number.
        Parameter   Notes
            data    a list of serial number of devices.
        Returns: return a dict as following, or a dict contains error on failure.
            {
                "TotalItems":2147483647,
                    "AcceptedItems":2147483647,
                    "FailedItems":2147483647,
                    "Faults":{
                        "ActivityId":"Text value",
                        "Fault":{
                            "ErrorCode":2147483647,
                            "ItemValue":"Text value",
                            "Message":"Text value"
                        }
                    }
            }
        """
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("lockdevice", "serialnumber", http_method="POST", data=data, content_type="application/xml")

    def lockdevice_by_udids(self, data):
        """
        Sends a Lock command to multiple devices identified by UDID.
        Parameter   Notes
            data list of UDID of devices.
        Returns: return a dict as following, or a dict contains error on failure.
            {
                "TotalItems":2147483647,
                    "AcceptedItems":2147483647,
                    "FailedItems":2147483647,
                    "Faults":{
                        "ActivityId":"Text value",
                        "Fault":{
                            "ErrorCode":2147483647,
                            "ItemValue":"Text value",
                            "Message":"Text value"
                        }
                    }
            }
        """
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("lockdevice", "udid", http_method="POST", data=data, content_type="application/xml")

    # Commands - Query
    def query_by_id(self, device_id):
        """
        Sends an Query command to the device identified by device ID.
        Parameter   Notes
            device_id   The device ID.
        Returns: device_id on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("query", type_value=device_id, http_method="POST")

    def query_by_macaddress(self, macaddress):
        """
        Sends an Query command to the device identified by MAC address.
        Parameter   Notes
            macaddress  The MAC address of the device.
        Returns: macaddress on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("query", "macaddress", macaddress, http_method="POST")

    def query_by_serialnumber(self, serialnumber):
        """
        Sends an Query command to the device identified by serial number.
        Parameter   Notes
            serialnumber    The serial number of the device.
        Returns: serialnumber on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("query", "serialnumber", serialnumber, http_method="POST")

    def query_by_udid(self, udid):
        """
        Sends an Query command to the device identified by UDID.
        Parameter   Notes
            udid    The UDID of the device.
        Returns: udid on success, or a dict contains error on failure.
        """
        return self.do_action_by_sometype("query", "udid", udid, http_method="POST")

    # Commands - Sync
    def syncdevice_by_id(self, device_id):
        return self.do_action_by_sometype("syncdevice", type_value=device_id, http_method="POST")

    def syncdevice_by_macaddress(self, macaddress):
        return self.do_action_by_sometype("syncdevice", "macaddress", macaddress, http_method="POST")

    def syncdevice_by_serialnumber(self, serialnumber):
        return self.do_action_by_sometype("syncdevice", "serialnumber", serialnumber, http_method="POST")

    def syncdevice_by_udid(self, udid):
        return self.do_action_by_sometype("syncdevice", "udid", udid, http_method="POST")

    # Commands - Wipe
    def devicewipe_by_id(self, device_id):
        return self.do_action_by_sometype("devicewipe", type_value=device_id, http_method="POST")

    def devicewipe_by_macaddress(self, macaddress):
        return self.do_action_by_sometype("devicewipe", "macaddress", macaddress, http_method="POST")

    def devicewipe_by_serialnumber(self, serialnumber):
        return self.do_action_by_sometype("devicewipe", "serialnumber", serialnumber, http_method="POST")

    def devicewipe_by_udid(self, udid):
        return self.do_action_by_sometype("devicewipe", "udid", udid, http_method="POST")

    # Delete
    def delete_device_by_id(self, device_id):
        return self.do_action_by_sometype("delete", type_value=device_id, http_method="DELETE")

    def delete_device_by_macaddress(self, macaddress):
        return self.do_action_by_sometype("delete", "macaddress", macaddress, http_method="DELETE")

    def delete_device_by_serialnumber(self, serialnumber):
        return self.do_action_by_sometype("delete", "serialnumber", serialnumber, http_method="DELETE")

    def delete_device_by_udid(self, udid):
        return self.do_action_by_sometype("delete", "udid", udid, http_method="DELETE")

    def delete_device_by_ids(self, data):
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("delete", http_method="POST", data=data, content_type="application/xml")

    def delete_device_by_macaddresses(self, data):
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("delete", "macaddress", http_method="POST", data=data, content_type="application/xml")

    def delete_device_by_serialnumbers(self, data):
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("delete", "serialnumber", http_method="POST", data=data, content_type="application/xml")

    def delete_device_by_udids(self, data):
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("delete", "udid", http_method="POST", data=data, content_type="application/xml")

    # Messaging - Email
    def send_email_by_id(self, device_id, data):
        return self.do_action_by_sometype("sendmessage/email", type_value=device_id, http_method="POST", data=data)

    def send_email_by_macaddress(self, macaddress, data):
        return self.do_action_by_sometype("sendmessage/email", "macaddress", macaddress, http_method="POST", data=data)

    def send_email_by_serialnumber(self, serialnumber, data):
        return self.do_action_by_sometype("sendmessage/email", "serialnumber", serialnumber, http_method="POST", data=data)

    def send_email_by_udid(self, udid, data):
        return self.do_action_by_sometype("sendmessage/email", "udid", udid, http_method="POST", data=data)

    def send_email_by_ids(self, data):
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("sendmessage/email", http_method="POST", data=data, content_type="application/xml")

    def send_email_by_macaddresses(self, data):
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("sendmessage/email", "macaddress", http_method="POST", data=data, content_type="application/xml")

    def send_email_by_serialnumbers(self, data):
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("sendmessage/email", "serialnumber", http_method="POST", data=data, content_type="application/xml")

    def send_email_by_udids(self, data):
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("sendmessage/email", "udid", http_method="POST", data=data, content_type="application/xml")

    # Messaging - Generic
    def send_message_by_id(self, device_id, data):
        return self.do_action_by_sometype("sendmessage", type_value=device_id, http_method="POST", data=data)

    def send_message_by_macaddress(self, macaddress, data):
        return self.do_action_by_sometype("sendmessage", "macaddress", macaddress, http_method="POST", data=data)

    def send_message_by_serialnumber(self, serialnumber, data):
        return self.do_action_by_sometype("sendmessage", "serialnumber", serialnumber, http_method="POST", data=data)

    def send_message_by_udid(self, udid, data):
        return self.do_action_by_sometype("sendmessage", "udid", udid, http_method="POST", data=data)

    # Messaging - Push
    def push_message_by_id(self, device_id, data):
        return self.do_action_by_sometype("sendmessage/push", type_value=device_id, http_method="POST", data=data)

    def push_message_by_macaddress(self, macaddress, data):
        return self.do_action_by_sometype("sendmessage/push", "macaddress", macaddress, http_method="POST", data=data)

    def push_message_by_serialnumber(self, serialnumber, data):
        return self.do_action_by_sometype("sendmessage/push", "serialnumber", serialnumber, http_method="POST", data=data)

    def push_message_by_udid(self, udid, data):
        return self.do_action_by_sometype("sendmessage/push", "udid", udid, http_method="POST", data=data)

    def push_message_by_ids(self, data):
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("sendmessage/push", http_method="POST", data=data, content_type="application/xml")

    def push_message_by_macaddresses(self, data):
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("sendmessage/push", "macaddress", http_method="POST", data=data, content_type="application/xml")

    def push_message_by_serialnumbers(self, data):
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("sendmessage/push", "serialnumber", http_method="POST", data=data, content_type="application/xml")

    def push_message_by_udids(self, data):
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("sendmessage/push", "udid", http_method="POST", data=data, content_type="application/xml")

    # Messaging - SMS
    def send_sms_by_id(self, device_id, data):
        return self.do_action_by_sometype("sendmessage/sms", type_value=device_id, http_method="POST", data=data)

    def send_sms_by_macaddress(self, macaddress, data):
        return self.do_action_by_sometype("sendmessage/sms", "macaddress", macaddress, http_method="POST", data=data)

    def send_sms_by_serialnumber(self, serialnumber, data):
        return self.do_action_by_sometype("sendmessage/sms", "serialnumber", serialnumber, http_method="POST", data=data)

    def send_sms_by_udid(self, udid, data):
        return self.do_action_by_sometype("sendmessage/sms", "udid", udid, http_method="POST", data=data)

    def send_sms_by_ids(self, data):
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("sendmessage/sms", http_method="POST", data=data, content_type="application/xml")

    def send_sms_by_macaddresses(self, data):
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("sendmessage/sms", "macaddress", http_method="POST", data=data, content_type="application/xml")

    def send_sms_by_serialnumbers(self, data):
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("sendmessage/sms", "serialnumber", http_method="POST", data=data, content_type="application/xml")

    def send_sms_by_udids(self, data):
        data = self.convert_to_xml(data)
        return self.do_action_by_sometype("sendmessage/sms", "udid", http_method="POST", data=data, content_type="application/xml")

    def search(self, data=None):
        """
        Searches for devices using the query information provided.
        Parameter notes:
            data: in python dict, may contains following items
                user            Enrolled username.
                model           Device model.
                platform        Device platform.
                lastseen        Last seen date string.
                ownership       Ownership.
                orderby         Orderby column name.
                compliantstatus Complaint status.
                page            Page number.
                pagesize        Records per page.
                sortorder       Sorting order. Values ASC or DESC. Defaults to ASC.
                lgid            LocationGroup to be searched, user's LG is considered if not sent.
        Returns: a list of device on success, or a tuple contains http error code and message on failure.
        """
        return self.do_action_by_sometype("search", data=data)

    def list(self):
        """
        List all devices.
        """
        return self.search()
