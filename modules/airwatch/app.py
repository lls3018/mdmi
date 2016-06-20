# -*- coding: utf-8 -*-
import sys
if '/opt/mdmi/modules' not in sys.path:
	sys.path.append('/opt/mdmi/modules')
from airwatch.base import AirwatchBase

class AirwatchApp(AirwatchBase):
	def __init__(self, account_id):
		super(AirwatchApp, self).__init__(account_id)

	def __del__(self):
		super(AirwatchApp, self).__del__()

	def do_action_by_sometype(self, app_info, appid_type=None, type_value=None, http_method="GET", data=None, content_type="application/json"):
		if not app_info and appid_type and type_value:
			resource = "/API/v1/mam/apps/{appidtype}/{appid}".format(appidtype=appid_type, appid=type_value)
		elif appid_type and type_value:
			resource = "/API/v1/mam/apps/{appidtype}/{value}/{info}".format(appidtype=appid_type, value=type_value, info=app_info)
		elif appid_type and not type_value:
			resource = "/API/v1/mam/apps/{appidtype}/{info}".format(appidtype=appid_type, info=app_info)
		elif type_value:
			resource = "/API/v1/mam/apps/{value}/{info}".format(value=type_value, info=app_info)
		else:
			resource = "/API/v1/mam/apps/{info}".format(info=app_info)

		if content_type:
			http_headers = {'Content-Type': content_type}
		else:
			http_headers = {'Content-Type': 'application/json'}
		http_headers.update(self.aw_headers)
		result = self.rest.do_access(resource, http_method, data, http_headers)
		if not result:
			return result
		if result.code == 204:
			return (result.code, result.reason)
		body = self._parse_result(result)
		if result.code >= 200 and result.code < 300:
			if not body:
				return type_value
			if type(body) == dict:
				if body.has_key('Total'):
					if body.has_key('Application'):
						apps = body['Application']
						for a in apps:
							if type(a['Id']) == dict and a['Id'].has_key('Value'):
								a['Id'] = a['Id']['Value']
						return body
				elif body.has_key('Id'):
					if type(body['Id']) == dict and body['Id'].has_key('Value'):
						body['Id'] = body['Id']['Value']
			elif type(body) == str and body == 'null':
				return type_value
			return body
		return body

	def assigneddevices_internal(self, app_id, location_group_id):
		"""
		Provides a list of devices that have been assigned the specified internal application.
		Parameter	Notes
			app_id	The application ID.
			location_group_id		The Location Group ID.
		Returns: a dict contains a list of device ID on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype('assigneddevices', 'internal', app_id, data={'locationgroupid': location_group_id})

	def assigneddevices_public(self, app_id, location_group_id):
		"""
		Provides a list of devices that have been assigned the specified public application.
		Parameter	Notes
			app_id	The application ID.
			location_group_id		The Location Group ID.
		Returns: a dict contains a list of device ID on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype('assigneddevices', 'public', app_id, data={'locationgroupid': location_group_id})

	def installeddevices_internal(self, app_id, location_group_id):
		"""
		Provides a list of devices that have the specified internal application installed.
		Parameter	Notes
			app_id	The application ID.
			location_group_id		The Location Group ID.
		Returns: a dict contains a list of device ID on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype('installeddevices', 'internal', app_id, data={'locationgroupid': location_group_id})

	def installeddevices_public(self, app_id, location_group_id):
		"""
		Provides a list of devices that have the specified public application installed.
		Parameter	Notes
			app_id	The application ID.
			location_group_id		The Location Group ID.
		Returns: a dict contains a list of device ID on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype('installeddevices', 'public', app_id, data={'locationgroupid': location_group_id})

	def status_internal(self, app_id, device_info):
		"""
		Indicates the status of the specified internal application on a device.
		Parameter	Notes
			app_id	The application ID.
			device_info	A dict should contains the following keys:
				deviceid	The device ID.
				macaddress	The device MAC address.
				serialnumber	The device serial number.
				udid	The device UDID.
		Returns: a string on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype('status', 'internal', app_id, data=device_info)

	def status_public(self, app_id, device_info):
		"""
		Indicates the status of the specified public application on a device.
		Parameter	Notes
			app_id	The application ID.
			device_info	A dict should contains the following keys:
				deviceid	The device ID.
				macaddress	The device MAC address.
				serialnumber	The device serial number.
				udid	The device UDID.
		Returns: a string on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype('status', 'public', app_id, data=device_info)

	def delete_internal(self, app_id):
		"""
		Deletes the specified internal application.
		Parameter	Notes
			app_id	The application ID.
		Returns: app_id on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype(None, 'internal', app_id, http_method='DELETE')

	def delete_public(self, app_id):
		"""
		Deletes the specified public application.
		Parameter	Notes
			app_id	The application ID.
		Returns: app_id on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype(None, 'public', app_id, http_method='DELETE')

	def activate_internal(self, app_id):
		"""
		Activates the specified internal application.
		Parameter	Notes
			app_id	The application ID.
		Returns: app_id on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype('activate', 'internal', type_value=app_id, http_method="POST")

	def deactivate_internal(self, app_id):
		"""
		Deactivates the specified internal application.
		Parameter	Notes
			app_id	The application ID.
		Returns: app_id on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype('deactivate', 'internal', type_value=app_id, http_method="POST")

	def activate_public(self, app_id):
		"""
		Activates the specified public application.
		Parameter	Notes
			app_id	The application ID.
		Returns: app_id on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype('activate', 'public', type_value=app_id, http_method="POST")

	def deactivate_public(self, app_id):
		"""
		Deactivates the specified public application.
		Parameter	Notes
			app_id	The application ID.
		Returns: app_id on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype('deactivate', 'public', type_value=app_id, http_method="POST")

	def update_public(self, app_info):
		"""
		Inserts or updates the public application selected by searching for the bundle ID (Android) or external ID (iOS) in the app market.
		Parameter	Notes
			app_info	A dict may should be in following format:
			{
				"Id":9223372036854775807,
				"ApplicationName":"Text value",
				"BundleId":"Text value",
				"AppVersion":"Text value",
				"AppType":"Text value",
				"Status":"Text value",
				"Platform":2147483647,
				"SupportedModels":[{
					"ModelId":2147483647,
					"ModelName":"Text value"
				}],
				"AssignmentStatus":"Text value",
				"ApplicationSize":"Text value",
				"CategoryList":[{
					"CategoryId":2147483647,
					"Name":"Text value"
				}],
				"Comments":"Text value",
				"IsReimbursable":true,
				"ApplicationUrl":"Text value",
				"LocationGroupId":9223372036854775807,
				"ExternalId":"Text value",
				"PushMode":0
			}
		Returns: a dict contains app information on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype('public', data=self.parse_param(app_info), http_method='POST')

	def install_internal(self, app_id, device_info):
		"""
		Installs the specified internal application on a device.
		Parameter	Notes
			app_id	The application ID.
			device_info	A dict should contains the following keys:
				deviceid	The device ID.
				macaddress	The device MAC address.
				serialnumber	The device serial number.
				udid	The device UDID.
		Returns: the app_id on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype('install', 'internal', app_id, data=self.parse_param(device_info), http_method='POST')

	def install_public(self, app_id, device_info):
		"""
		Installs the specified public application on a device.
		Parameter	Notes
			app_id	The application ID.
			device_info	A dict should contains the following keys:
				deviceid	The device ID.
				macaddress	The device MAC address.
				serialnumber	The device serial number.
				udid	The device UDID.
		Returns: the app_id on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype('install', 'public', app_id, data=self.parse_param(device_info), http_method='POST')

	def uninstall_internal(self, app_id, device_info):
		"""
		Installs the specified internal application on a device.
		Parameter	Notes
			app_id	The application ID.
			device_info	A dict should contains the following keys:
				deviceid	The device ID.
				macaddress	The device MAC address.
				serialnumber	The device serial number.
				udid	The device UDID.
		Returns: the app_id on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype('uninstall', 'internal', app_id, data=self.parse_param(device_info), http_method='POST')

	def uninstall_public(self, app_id, device_info):
		"""
		Installs the specified public application on a device.
		Parameter	Notes
			app_id	The application ID.
			device_info	A dict should contains the following keys:
				deviceid	The device ID.
				macaddress	The device MAC address.
				serialnumber	The device serial number.
				udid	The device UDID.
		Returns: the app_id on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype('uninstall', 'public', app_id, data=self.parse_param(device_info), http_method='POST')

	def uploadchunk(self, chunk_data):
		"""
		Uploads the chunk data of an internal application into the server.
		Parameter	Notes
			chunk_data	a dict may in following format:
				{
					"TransactionId":"Text value",
					"ChunkData":[81, 109, 70, 122, 90, 83, 61],
					"ChunkSequenceNumber":2147483647,
					"TotalApplicationSize":9223372036854775807,
					"ChunkSize":9223372036854775807
				}
		Returns: a dict of transaction information on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype('uploadchunk', 'internal', data=self.parse_param(chunk_data), http_method="POST")

	def begininstall(self, transaction_info):
		"""
		Creates an internal application using the uploaded file chunks.
		Parameter	Notes
			chunk_data	a dict may in following format:
				{
					"TransactionId":"Text value",
					"DeviceType":"Text value",
					"ApplicationName":"Text value",
					"SupportedModels":[{
						"ModelId":2147483647,
						"ModelName":"Text value"
					}],
					"PushMode":"Text value",
					"Description":"Text value",
					"SupportEmail":"Text value",
					"SupportPhone":"Text value",
					"Developer":"Text value",
					"DeveloperEmail":"Text value",
					"DeveloperPhone":"Text value",
					"AutoUpdateVersion":true
				}
		Returns: a dict of app information on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype('begininstall', 'internal', data=self.parse_param(transaction_info), http_method="POST")

	def retire_internal(self, app_id):
		"""
		Retires the specified internal application.
		Parameter	Notes
			app_id	The application ID.
		Returns: app_id on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype('retire', 'internal', app_id, http_method="POST")

	def unretire_internal(self, app_id):
		"""
		Unretires the specified internal application.
		Parameter	Notes
			app_id	The application ID.
		Returns: app_id on success or a dict contains error on failure.
		"""
		return self.do_action_by_sometype('unretire', 'internal', app_id, http_method="POST")
	
	def search(self, condition=None):
		"""
		Search and retrieve details for both internal and external applications.
		Parameter	Notes
			condition: a dict may contains zero or more keys which should be:
				applicationname		The application name.
				category	The application category.
				locationgroupid		The Location Group ID.
				bundleid	The bundle/package ID.
				platform	The application platform.
				model	The model of Device
				status	The active status.
				orderby		Order the results by this.
				page	The specific page number to get.
				pagesize	Max records per page.
				type	App or Book
		Returns: a dict and each element contains detail information of an application
		"""
		return self.do_action_by_sometype('search', data=condition)

	def list(self):
		"""
		List and retrieve details for both internal and external applications.
		Returns: a dict and each element contains detail information of an application
		"""
		return self.search()
