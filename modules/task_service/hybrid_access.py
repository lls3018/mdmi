import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')

import base64
from utils import logger
from utils.configure import MDMiConfigParser
from utils.rest_access import RESTAccess
from hosteddb.hosted_crypt import decrypt
from utils.stringutils import get_admin_name_from_dn

AUTH_FILE_PATH = '/etc/sysconfig/mes.json'
HOST_FILE_PATH = '/etc/sysconfig/serviceconfig.json'

post_request_body_template = {
        'add': "dn: {0}\r\n"\
                "mail: {1}\r\n"\
                "objectClass: {2}\r\n"\
                "objectGuid:: {3}\r\n"\
                "cn: {4}",
        'delete': "dn: {0}\r\n"\
                "mail: {1}\r\n"\
                "objectClass: {2}\r\n"\
                "objectGuid:: {3}\r\n"\
                "changetype: delete\r\n"\
                "cn: {4}",
    }

class HybridAccess(RESTAccess):
    def __init__(self, account):
        self.account = account
        self.dn_list = list()
        self.counts = {'add': 0, 'delete': 0}

        conf = MDMiConfigParser(AUTH_FILE_PATH, isjson=True)
        info = conf.read()
        if isinstance(info, dict) and info.has_key('user') and info.has_key('metanate_password'):
            password = decrypt(info['metanate_password'])
            user = get_admin_name_from_dn(info['user'])
            self.authorization = ' '.join(['Basic', base64.b64encode(':'.join([user, password]))])
        else:
            self.authorization = ''

        conf = MDMiConfigParser(HOST_FILE_PATH, isjson=True)
        info = conf.read()
        if isinstance(info, dict) and info.has_key('hsync'):
            self.host = info['hsync']
        else:
            self.host = ''
        self.port = 443

        super(self.__class__, self).__init__(self.host, self.port)
        pass

    def __del__(self):
        pass

    def do_access(self, resource, data=None, headers=None):
        http_headers = self._generate_headers()
        if headers:
            http_headers.update(headers)
            
        if data:
            body = self._generate_post_body(data)
        else:
            body = ''
            http_headers.pop('Content-Type')

        logger.debug('hybrid request headers: %s, body: %s' % (http_headers, body))
        r = super(self.__class__, self).do_access(resource, method_name='PUT', data=body, headers=http_headers)
        
        if r.code == 200:
            logger.info('hybrid request: %s send successfully' % resource)
        else:
            logger.error('hybrid request: %s error occurred, error code: %s, error message: %s', resource, r.code, r.content)
            
        return r

    def add_user(self, data):
        '''
        Data is a dict which should contains keys: dn, mail, objectClass, objectGuid, cn
        '''
        headers = {'X-MDMI-DASID': 'MDMI_AIRWATCH'}
        return self.do_access('/hsync/users', data, headers)
    
    def add_multi_users(self, data):
        '''
        Data is a dict list(or tuple, or set), each dict should contains keys: dn, mail, objectClass, objectGuid, cn
        '''
        headers = {'X-MDMI-DASID': 'MDMI_AIRWATCH'}
        return self.do_access('/hsync/users', data, headers)
    
    def delete_user(self, data):
        '''
        Data is a dict which should contains keys: dn, mail, objectClass, objectGuid, cn
        '''
        return self.do_access('/hsync/users', data, None)
    
    def delete_multi_users(self, data):
        '''
        Data is a dict list(or tuple, or set), each dict should contains keys: dn, mail, objectClass, objectGuid, cn
        '''
        return self.do_access('/hsync/users', data, None)

    def _generate_headers(self):
        headers = {}
        headers['Authorization'] = self.authorization
        headers['Content-Type'] = 'multipart/form-data;'
        headers['X-SYNC-ACCOUNT'] = self.account
        
        return headers

    def _generate_post_body(self, data):
        '''
        Parameter data should be a dict or dict list(or tuple, or set).
        If data is a dict, it means the operation is on one user, or is on multiple users.
        '''
        global post_request_body_template
        post_body = ''
        
        if isinstance(data, dict):
            data = dict([(k.lower(), v) for (k, v) in data.items()])
            dn = data['dn']
            if dn in self.dn_list:
                return
            else:
                self.dn_list.append(dn)
                mail = data['mail']
                objectguid = data['objectguid']
                cn = data['cn']
                objectclass = 'User'
                changetype = 'add'
                if 'changetype' in data:
                    changetype = data['changetype']
                post_body = post_request_body_template.get(changetype).format(dn, mail, objectclass, objectguid, cn)
        elif isinstance(data, (list, tuple, set)):
            length = len(data)
            for i in xrange(length):
                if i == length - 1:
                    post_body += self._generate_post_body(data[i])
                else:
                    post_body += self._generate_post_body(data[i]) + '\r\n\r\n\r\n'
        
        return post_body
    
    def _delete_data_from_db(self, data):
        import MySQLdb
        
        if not data:
            return False
        else:
            try:
                logger.debug('start connection to MySQL...')
                conn = MySQLdb.connect(host='cfg', user='webserv', passwd='', db='blackspider', port=3306)
                cur = conn.cursor()
                logger.debug('connection to MySQL is ready, begin to delete data from MySQL')
                if isinstance(data, dict):
                    dn = data.get('dn')
                    cur.execute('DELETE FROM hyEndUsers WHERE AccountID = %s and dn = %s' % (self.account, dn))
                elif isinstance(data, (list, tuple, set)):
                    for d in data:
                        dn = d.get('dn')
                        cur.execute('DELETE FROM hyEndUsers WHERE AccountID = %s and dn = %s' % (self.account, dn))
                else:
                    logger.error('invalid data format and given data type is %s', type(data))
                conn.commit()
                cur.close()
                conn.close()
            except MySQLdb.Error as e:
                print 'MySQL error: %s' % e
                return False
            else:
                logger.debug('connection to MySQL is closed and data delete success')
                return True
