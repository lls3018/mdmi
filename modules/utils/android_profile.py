#!/usr/bin/python

import sys
import base64
#from Crypto.Cipher import AES
sys.path.append("/opt/mdmi/modules")
from utils import logger
from utils.openssl import *
from xml.dom.minidom import Document
import urlparse
import urllib

class AndroidProfile(object):

    def __init__(self):
        pass

    def dumps(self, user_info, pac_url, vpn_bypass_except, format='xml'):
        """
            Dumps vpn profile to xml string.
            Parameter Notes:
            user_info(string): must contains Username and DeviceID keyword,
            like "Username:someone@websense.com;DeviceID:someone's device"
            pack_url(string): a valid http or https url
        """
        return self.generate_profile_xml(user_info, pac_url, vpn_bypass_except) 

    def generate_profile_xml(self, user_info, pac_url, vpn_bypass_except):
        doc = Document()
        root = doc.createElement('parameters')
        doc.appendChild(root)

        item0 = doc.createElement('extra')
        item0.setAttribute('key', 'com.websense.android.wms.extra.PROXY_CONFIGURATION_ACTION')
        item0.setAttribute('value', 'com.websense.android.wms.SET_PROXY_CONFIGURATION')
        root.appendChild(item0)

        item1 = doc.createElement('extra')
        item1.setAttribute('key', 'com.websense.android.wms.extra.PROXY_PAC_FILE_URL')
        #add param for the url
        updated_pac_url = self.update_pacfile_type(pac_url)
        item1.setAttribute('value', updated_pac_url)
        root.appendChild(item1)

        item2 = doc.createElement('extra')
        item2.setAttribute('key', 'com.websense.android.wms.extra.PROXY_AUTH_STRING')
        item2.setAttribute('value', str(user_info))
        root.appendChild(item2)


        item3 = doc.createElement('extra')
        item3.setAttribute('key', 'com.websense.android.wms.extra.PACKAGE_NAME')
        item3.setAttribute('value', 'com.thirdparty.mdmapplication')
        root.appendChild(item3)
        
        #add rules for local network accesss
        self.add_vpn_ondemandrules(doc, root, vpn_bypass_except)
        dd = doc.toprettyxml(indent="\t").encode('UTF-8')

        return dd


    def add_vpn_ondemandrules(self, doc, root, vpn_bypass_except):
        attr_val = None
        attr_key = None
        attr_key_val = None

        base_cn = 'com.websense.android.wms.extra.'
        optional_cn = ''

        if vpn_bypass_except and isinstance(vpn_bypass_except, dict):
            attr_val = vpn_bypass_except.get('attributes')
        else:
            logger.info('the rules is not dict of local network access:%s',vpn_bypass_except)
            return None

        if attr_val and isinstance(attr_val, dict):
            for (k, v) in attr_val.items():
                if k == 'LocalNetworkAccessKey':
                    if v:
                        attr_key = v[0]
                if k == 'LocalNetworkAccessValue':
                    if v:        
                        attr_key_val = v[0]
 
        if attr_key == 'SSIDMatch':
            optional_cn = 'LOCAL_NETWORK_ACCESS_SSIDS'
        elif attr_key == 'DNSServerAddressMatch':
            optional_cn = 'LOCAL_NETWORK_ACCESS_DNS_SERVERS'
        elif attr_key == 'DNSDomainMatch':
            optional_cn = 'LOCAL_NETWORK_ACCESS_SEARCH_DOMAINS'
        else:
            logger.info('LocalNetworkAccessKey is not match')
            return None
       
        #cryptor = prcrypt('1234567890123456')
        LOCAL_NETWORK_ACCESS_VALUE = '1'
        #LOCAL_NETWORK_ACCESS_VALUE = cryptor.encrypted(LOCAL_NETWORK_ACCESS_VALUE)
        logger.info('LOCAL_NETWORK_ACCESS_VALUE is %s',LOCAL_NETWORK_ACCESS_VALUE)

        logger.info('attr_key_val is %s',attr_key_val)
        if attr_key_val:
            item0 = doc.createElement('extra')
            item0.setAttribute('key',base_cn + 'LOCAL_NETWORK_ACCESS')
            item0.setAttribute('value',LOCAL_NETWORK_ACCESS_VALUE)
            root.appendChild(item0)
            #attr_key_val = cryptor.encrypted(attr_key_val)
            item1 = doc.createElement('extra')
            item1.setAttribute('hey',base_cn + optional_cn)
            item1.setAttribute('value',attr_key_val)
            root.appendChild(item1)


    def update_pacfile_type(self, pacfile):
        try:
            pr = urlparse.urlparse(pacfile)
            prlst = list(pr)

            query = dict(urlparse.parse_qsl(pr.query))
            #use port 8081 of proxy
            query["a"] = "n"
            #data will be sent to cloud, not op, used for hybrid situation
            query["cli"] = "mob"
            prlst[4] = urllib.urlencode(query)
            return urlparse.ParseResult(*prlst).geturl()
        except Exception, e:
            logger.error("add mdm type to pac file url error %s" % repr(e))
            return pacfile

    def parse_cert(self, pemfile):
        try:
            file = open(pemfile, 'r')
            content = file.read()
            file.close()
            if content:
                begin = content.find('-----BEGIN CERTIFICATE-----')
                end = content.find('-----END CERTIFICATE-----')
                content = content[begin + len('-----BEGIN CERTIFICATE-----') : end].strip()
            return content
        except Exception, e:
            logger.error("load certificate from root ca error: %s", e)
            return None


#class prcrypt():
#    def __init__(self, key, mode = AES.MODE_CBC):
#        self.key = key
#        self.mode = mode
#
#    def encrypted(self, text):
#        #if the text is not enough 16 byte, supplement it
#        length = 16
#        count = len(text)
#        if  count < length:
#            add = (length - count)
#            text = text + ('\x00' * add)
#        elif count > length:
#            add = (length - (count % length))
#            text = text + ('\x00' * add)
#
#        cryptor = AES.new(self.key, self.mode)
#        ciphere_text = cryptor.encrypt(text)
#        out_put = base64.encodestring(ciphere_text)
#        return out_put
#
#    def decrypted(self, text):
#        cryptor = AES.new(self.key,self.mode)
#        ciphere_text = base64.decodestring(text)
#        out_put = cryptor.decrypt(ciphere_text)
#        return out_put


if __name__ == "__main__":
    vpn_profile = AndroidProfile()
    xml = vpn_profile.dumps("Username:scai@websense.com;DeviceID:scai", "pac_url://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") 
    print xml
