# -*- coding: utf-8 -*-
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
from airwatch.base import AirwatchBase

class AirwatchUser(AirwatchBase):
    def __init__(self, account_id):
        super(self.__class__, self).__init__(account_id)

    def __del__(self):
        super(self.__class__, self).__del__()

    def create(self, data):
        """
        Creates a new enrollment user.
        Parameter   Notes
            data: a dict, may contains following information:
                "UserName":"Text value",
                "Password":"Text value",
                "FirstName":"Text value",
                "LastName":"Text value",
                "Status":true,
                "Email":"Text value",
                "SecurityType":0,
                "ContactNumber":"Text value",
                "EmailUserName":"Text value",
                "Group":"Text value",
                "Role":"Text value",
                "MessageType":0,
                "EnrolledDevicesCount":"Text value",
                "MessageTemplateId":2147483647
        Returns:
            The created user id, or a dict contains error on failure.
        """
        result = self.rest.do_access("/API/v1/system/users/adduser", "POST", self.parse_param(data), headers=self.aw_headers)
        body = self._parse_result(result)
        if isinstance(body, dict) and body.has_key('Value'):
            return body['Value']
        return body

    def modify(self, user_id, data=None, method_name='update', http_method='POST'):
        resource = "/API/v1/system/users/{id}/{method}".format(id=user_id, method=method_name)
        result = self.rest.do_access(resource, http_method, self.parse_param(data), headers=self.aw_headers)
        if not result:
            return result

        return user_id

    def update(self, user_id, data):
        """
        Updates the user details.
        Parameter   Notes
            user_id: the user's identify
            data: a dict, may contains following information:
                "UserName":"Text value",
                "Password":"Text value",
                "FirstName":"Text value",
                "LastName":"Text value",
                "Status":true,
                "Email":"Text value",
                "SecurityType":0,
                "ContactNumber":"Text value",
                "EmailUserName":"Text value",
                "Group":"Text value",
                "Role":"Text value",
                "MessageType":0,
                "EnrolledDevicesCount":"Text value",
                "MessageTemplateId":2147483647
        Return:
            The user id on success, or a dict contains error on failure.
        """
        return self.modify(user_id, data)

    def register_device(self, user_id, data):
        return self.modify(user_id, data, self.register_device.__name__)

    def activate(self, user_id):
        return self.modify(user_id, None, self.activate.__name__)

    def deactivate(self, user_id):
        return self.modify(user_id, None, self.deactivate.__name__)

    def delete(self, user_id):
        return self.modify(user_id, None, 'delete', 'DELETE')

    def modify_users(self, data, method_name):
        resource = "/API/v1/system/users/{method}".format(method=method_name)
        result = self.rest.do_access(resource, "POST", self.parse_param(data))
        body = self._parse_result(result)
        return body

    def delete_users(self, data):
        return self.modify_users(data, "delete")

    def activate_users(self, data):
        return self.modify_users(data, "activate") 

    def deactivate_users(self, data):
        return self.modify_user(data, "deactivate") 

    def change_location_group(self, user_id, location_group_id):
        resource = "/API/v1/system/users/{id}/changelocationgroup?targetLG={locationgroupid}".format(id=user_id, locationgroupid=location_group_id)
        result = self.rest.do_access(resource, "POST", headers=self.aw_headers)
        if not result:
            return result

        return location_group_id

    def get(self, user_id):
        """
        Retrieves information about the specified enrollment user.
        Parameter   Notes
            user_id The user ID.
        Returns: On success, a dict may contains following user information
            {
                "Id":9223372036854775807,
                "UserName":"Text value",
                "Password":"Text value",
                "FirstName":"Text value",
                "LastName":"Text value",
                "Status":true,
                "Email":"Text value",
                "SecurityType":0,
                "ContactNumber":"Text value",
                "EmailUserName":"Text value",
                "Group":"Text value",
                "Role":"Text value",
                "MessageType":0,
                "EnrolledDevicesCount":"Text value",
                "MessageTemplateId":2147483647
            }
            or a dict contains error on failure.
        """
        resource = "/API/v1/system/users/{id}".format(id=user_id)
        result = self.rest.do_access(resource, headers=self.aw_headers)
        u = self._parse_result(result)
        if isinstance(u, dict) and isinstance(u['Id'], dict):
            if u['Id'].has_key('Value'):
                u['Id'] = u['Id']['Value']

        return u
        
    def search(self, data=None):
        """
        Searches for enrollment users using the query information provided.
        Parameter   Notes
            data: a dict may contain none or more item of following
                firstname   The first name to search for.
                lastname    The last name to search for.
                emailaddress    The email address to search for.
                locationgroupid     The Location Group ID to search for.
                role    The role to search for.
        Returns: a list of user information, or a tuple contains http error code and message on failure.
        """
        resource = "/API/v1/system/users/search"
        result = self.rest.do_access(resource, data=data, headers=self.aw_headers)
        if result.code == 204:
            # return (result.code, result.reason)
            return None
        body = self._parse_result(result)
        users = body['Users']
        for u in users:
            if isinstance(u['Id'], dict):
                if u['Id'].has_key('Value'):
                    u['Id'] = u['Id']['Value']

        return users

    def list(self):
        return self.search()
