# -*- coding: utf-8 -*-
import sys
if '/opt/mdmi/modules' not in sys.path:
	sys.path.append('/opt/mdmi/modules')
from airwatch.base import AirwatchBase

class AirwatchGroup(AirwatchBase):
	def __init__(self, account_id):
		super(self.__class__, self).__init__(account_id)

	def __del__(self):
		super(self.__class__, self).__del__()

	def create(self, group_id, data):
		return self.update(group_id, data, True);

	def update(self, group_id, data, create=False):
		if create:
			resource = "/API/v1/system/groups/{id}/creategroup".format(id=group_id)
		else:
			resource = "/API/v1/system/groups/{id}/update".format(id=group_id)
		result = self.rest.do_access(resource, "POST", self.parse_param(data), headers=self.aw_headers)
		if not result:
			return result
		body = self._parse_result(result)
		if result.code >= 200 and result.code < 300:
			if body:
				if isinstance(body, dict) and body.has_key('Value'): return body['Value']
				return body
			else: return group_id
		else:
			return body

	def delete(self, group_id):
		resource = "/API/v1/system/groups/{id}/delete".format(id=group_id)
		result = self.rest.do_access(resource, "DELETE", headers=self.aw_headers)
		if not result:
			return result
		if result.code >= 200 and result.code < 300:
			return True, None
		else:
			body = self._parse_result(result)
			return False, body

	def getadmins(self, group_id):
		"""
		Provides a list of admin users in the specified organization group.
		Parameter	Notes
			group_id	The organization group ID.
		Returns: a list of admin, each item is a dict on success, or a dict contains error on failure.
		"""
		return self.get(group_id, self.getadmins.__name__)

	def getusers(self, group_id):
		"""
		Provides a list of enrollment users in the specified organization group.
		Parameter	Notes
			group_id	The organization group ID.
		Returns:
			a list of user, each item is a dict on success, or a dict contains error on failure.
		"""
		return self.get(group_id, self.getusers.__name__)

	def getchild(self, group_id):
		"""
		Provides a list of child organization groups of the specified organization group.
		Parameter	Notes
			group_id	The parent organization group ID.
		Returns: a list of group, echo item is a dict on success, or a dict contains error on failure.
		"""
		return self.get(group_id, self.getchild.__name__)

	def roles(self, group_id):
		"""
		Provides a list of user roles in the specified organization group.
		Parameter	Notes
			group_id	The organization group ID.
		Returns: a list of role, echo item is a dict on success, or a dict contains error on failure.
		"""
		return self.get(group_id, self.roles.__name__)

	def get(self, group_id, method_name=None):
		"""
		Retrieves information about the specified organization group.
		Parameter	Notes
			group_id	The organization group ID.
		Returns: On success, a dict contains following information:
			{
				"Id":9223372036854775807,
				"Name":"Text value",
				"GroupId":"Text value",
				"LocationGroupType":"Text value",
				"Country":"Text value",
				"Locale":"Text value",
				"ParentLocationGroup":{
				},
				"AddDefaultLocation":"Text value",
				"CreatedOn":"Text value",
				"LgLevel":2147483647,
				"Users":"Text value",
				"Admins":"Text value",
				"Devices":"Text value"
			}
			, or a dict contains error on failure.
		"""
		if method_name:
			resource = "/API/v1/system/groups/{id}/{method}".format(id=group_id, method=method_name);
		else:
			resource = "/API/v1/system/groups/{id}".format(id=group_id);
		result = self.rest.do_access(resource, headers=self.aw_headers)
		if not result:
			return result
		g = self._parse_result(result)
		if result.code >= 200 and result.code < 300:
			if isinstance(g, dict) and isinstance(g['Id'], dict):
				if g['Id'].has_key('Value'):
					g['Id'] = g['Id']['Value']
			elif isinstance(g, (list, tuple)):
				for i in g:
					if isinstance(i, dict) and isinstance(i['Id'], dict):
						if i['Id'].has_key('Value'):
							i['Id'] = i['Id']['Value']
		return g
	

	def search(self, data=None):
		"""
		Searches for organization groups using the query information provided.
		Parameter	Notes
			data: a dict may contain following item:
				name	The organization group name to search for.
				type	The organization group type to search for.
				groupid		The organization group ID to search for.
		Returns: a list of group on success, or a tuple contains http error and message on failure.
		"""
		resource = "/API/v1/system/groups/search"
		result = self.rest.do_access(resource, data=data, headers=self.aw_headers)
		if not result:
			return result
		if result.code == 204:
			 return None
		body = self._parse_result(result)
		if result.code >= 200 and result.code < 300:
			# print body['Page']
			# print body['PageSize']
			# print body['Total']
			groups = body['LocationGroups']
			for g in groups:
				if isinstance(g['Id'], dict):
					if g['Id'].has_key('Value'):
						g['Id'] = g['Id']['Value']
			return groups
		return body

	def list(self):
		return self.search()
