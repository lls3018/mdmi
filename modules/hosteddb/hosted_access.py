# -*- coding: utf-8 -*-
import sys
import httplib
import base64
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
import utils.configure
from utils.configure import MDMiConfigParser
from utils.rest_access import RESTAccess


class HostedAccess(RESTAccess):
    '''
    class HostedAccess
        This class implements the access through websense REST API.

    Attributes:
        m_conn: valid connection
        m_auth: Authorization information
    '''
    def __init__(self, hostauth=None, hostaddr=None, hostport=None):
        self.m_conn = None
        self.m_auth = None
        self.m_conn, self.m_auth = self._get_valid_conn(hostauth, hostaddr, hostport)
        super(HostedAccess, self).__init__(host=None, connection=self.m_conn)
        pass

    def __del__(self):
        if self.m_conn:
            self._ret_valid_conn(self.m_conn)  # return connections
        pass

    def do_access(self, resource, method_name="GET", data=None, headers=None):
        '''
        Issue the operation.

        Params:
            resource: resource of the destation.
            method_name: http request method, includes 'GET', 'POST', etc.
            data: Data sent with http request.
            headers: Headers sent with http request.

        Return:
            The response from the server.
        '''
        if not headers:
            headers = self.generate_default_header()
        response = super(HostedAccess, self).do_access(resource, method_name, data, headers)
        return response
        pass

    def generate_default_header(self):
        '''
        Generate default http header

        Return:
            The default http header in dict.
        '''
        http_headers = {
            'Authorization' : self.m_auth,
            'Accept' : 'application/json',
            'Connection' : 'Keep-Alive',
        }
        return http_headers
        pass

    def _get_valid_conn(self, hostauth, hostaddr, hostport):
        '''
        using conn pool later
        '''
        auth = '' 
        addr = ''
        port = ''
        if hostauth and hostaddr and hostport:
            auth = hostauth
            addr = hostaddr
            port = hostport
        else:
            addr, port, authpath = self._get_access_info()
            if self.m_auth == None:
                if authpath:
                    auth = self._get_access_authinfo(authpath)

        conn = httplib.HTTPSConnection(addr, port)  # temp
        return conn, auth
        pass
    
    def _ret_valid_conn(self, conn):
        '''
        return connection back to pool
        '''
        if conn:
            conn.close()  # temp
        pass

    def _get_access_info(self):
        '''
        Get address and port for accessing to hostedDB.

        Return:
            An pair of return values: address, port
        '''
        hostaddr = None
        hostport = None
        authfile = None
        cfg_reader = MDMiConfigParser(utils.configure.MDMI_CONFIG_FILE, False)
        tmp_list = cfg_reader.read('hosted', 'ipaddr')
        if tmp_list:
            hostaddr = tmp_list[0][1]
        tmp_list = cfg_reader.read('hosted', 'port')
        if tmp_list:
            hostport = tmp_list[0][1]
        tmp_list = cfg_reader.read('hosted', 'mesjsonpath')
        if tmp_list:
            authfile = tmp_list[0][1]

        return hostaddr, hostport, authfile
        pass

    def _get_access_authinfo(self, authpath):
        '''
        Get authorization information for accessing to hostedDB.

        Return:
            An authorization string.
        '''
        auth_dict = MDMiConfigParser(authpath, True).read('user', 'password')
        admin = auth_dict.get('user')
        passwd = auth_dict.get('password')
        auth_info = ''
        if admin and passwd:
            auth_info = ':'.join([admin, passwd])
            auth_info = base64.encodestring(auth_info).replace("\n", '')
            auth_info = ' '.join(['Basic', auth_info])
        return auth_info
        pass

# end of class HostedAccess


