#!/usr/bin/python

import base64
import threading
import urlparse
import urllib
import os

from uuid import uuid4
from ConfigParser import ConfigParser
from xml.etree import ElementTree
from M2Crypto.EVP import Cipher

from openssl import *
from utils import logger

config = ConfigParser()
config.read("/opt/mdmi/etc/mdmi.conf")
if config._sections.has_key('vpn'):
    config = config._sections['vpn']
    if not config.has_key('template') \
        or not config.has_key('remote_address') \
        or not config.has_key('root_ca') \
        or not config.has_key('vpn_ca') \
        or not config.has_key('issuer_ca') \
        or not config.has_key('issuer_key') \
        or not config.has_key('issuer_passcode') \
        or not config.has_key('passout') \
        or not config.has_key('ssl_ca'):
        config = None
else:
    config = None

SIGN_CA = "/opt/emserver/portal/www/profile/domain.crt"
INTER_CA = "/opt/emserver/portal/www/profile/intermediate.crt"
SIGN_KEY = "/opt/emserver/portal/www/profile/domain.key"

def encrypt_sn(sn):
    m=Cipher(alg = "aes_128_cbc", key = config['passout'], iv = '\x00' * 16, op = 1)
    m.set_padding(padding=7)
    v = m.update(sn)
    v = v + m.final()
    del m
    return v

def load_plist_from_file(file_name):
    try:
        result = ElementTree.parse(file_name)
        return result
    except Exception, e:
        return None

class VPNUtils(object):
    def __init__(self):
        pass

    def __del__(self):
        pass

    def dumps_list(self, tasks, error_tasks, vpn_bypass_except=None):
        pkey = generate_key(len(tasks))
        i = 0
        for index in xrange(len(tasks)-1, -1, -1):
            try:
                task = tasks[index]
                pacfile = task['payload']['policyPacUrl']
                user_info = "Username:%s;AccountID:%s;DeviceID:%s;DeviceType:%s;DeviceClass:%s;scanopt:2" % (task['payload']['EnrollmentEmailAddress'], task['account'], task['payload']['Udid'], task['payload']['Model'], task['payload']['Ownership'])
                user_info = user_info.encode('utf8')
        
                vpn_obj = VPNProfile(int(task['account']))
                plist, expire_date = vpn_obj.dumps(user_info, pacfile, task["vpnexceptlst"], pkey[i], vpn_bypass_except, task['payload']['HostedDevice']['deviceSerialNumber'])
                if plist and expire_date:
                    task['profile'] = plist
                    task['payload']['HostedDevice']['certExpiryDate'] = expire_date
                else:
                    error_msg = "generate vpn profile error profile is null or expire date is null"
                    logger.error(error_msg)
                    task['error_msg'] = error_msg
                    error_tasks.append(task)
                    del tasks[index]
                i += 1
                del vpn_obj
            except Exception, e:
                error_msg = "generate vpn profile error: %s" % str(e)
                logger.error(error_msg)
                task['error_msg'] = error_msg
                error_tasks.append(task)
                del tasks[index]

# Singleton class
class VPNProfile(object):
    objs = {}
    objs_locker = threading.Lock()
    def __new__(cls, *args, **kwargs):
        if cls in cls.objs:
            return cls.objs[cls]['obj']

        cls.objs_locker.acquire()
        # check again
        if cls in cls.objs:
            return cls.objs[cls]['obj']
        obj = object.__new__(cls)
        cls.objs[cls] = {'obj': obj, 'init': False}
        setattr(cls, '__init__', cls.private_vpn_init(cls.__init__))
        cls.objs_locker.release()
        return cls.objs[cls]['obj']

    @classmethod
    def private_vpn_init(cls, fn):
        def init_wrap(*args):
            if not cls.objs[cls]['init']:
                fn(*args)
                cls.objs[cls]['init'] = True
            return
        return init_wrap

    def get_child_node(self, node, child_node_name):
        node_childs = node.getchildren()
        for child in node_childs:
                if child.text == child_node_name:
                    return child
        return None        

    def add_node(self, node_dict, node_name, node_value, value_type):
        node_pl_key = ElementTree.SubElement(node_dict, 'key')
        node_pl_key.text = node_name
        node_pl_string = ElementTree.SubElement(node_dict, value_type)
        node_pl_string.text = node_value
        return node_dict
    
    def add_bool_node(self, node_dict, node_name, node_value=False):
        node_pl_key = ElementTree.SubElement(node_dict, 'key')
        node_pl_key.text = node_name
        if node_value is True:
            ElementTree.SubElement(node_dict, 'true')
        else:
            ElementTree.SubElement(node_dict, 'false')

    def read_p12_data(self, p12):
        if p12:
            return file(p12, 'rb').read()
        else:
            return None

    def generate_payload(self):
        node_dict = ElementTree.Element('dict')
        self.add_node(node_dict, 'PayloadVersion', '1', 'integer')
        self.add_node(node_dict, 'PayloadDescription', 'Wensense Mobile Security Profile' ,'string')
        self.add_node(node_dict, 'PayloadOrganization', 'Websense,Inc.', 'string')
        self.add_node(node_dict, 'PayloadUUID', str(uuid4()).upper(), 'string')
        return node_dict

    def get_next_node(self, node, child_node_name):
        if node:
            node_childs = node.getchildren()
            next_node = False
            for child in node_childs:
                if next_node:
                    return child
                elif child.text == child_node_name:
                    next_node = True
        return None        
        

    def __init__(self, account=None):
        logger.debug("Begin to init vpn profile")
        self.init_done = 0
        if not config:
            return
        logger.debug("profile template in config file: %s, account: %s", config['template'], account) # templete is not right
        #for customed vpn profile
        self.profile = None
        self.activesync_ca_data = None

        if account:
            template_dir = os.path.dirname(config['template'])
            customed_vpn_template_path = template_dir + '/customized_VPN_profile_'+ str(account)
            possible_file_name_list = [customed_vpn_template_path, config['template']]
        else:
            possible_file_name_list = [config['template']]

        logger.debug('possible_file_name_list: %s', possible_file_name_list)
        for name in possible_file_name_list:
            if os.path.isfile(name):
                self.profile = load_plist_from_file(name)
                logger.debug('will use template: %s', name)
                break

        if not self.profile:
            logger.error("load profile error: %s", config['template'])
            return
        
        self.node_root = self.profile.getroot()
        node_dict = self.node_root.getchildren()[0]
        if not node_dict:
            logger.error("profile do not contains any payload")
      
        node_ident = self.get_child_node(node_dict, 'PayloadIdentifier')
        if not node_ident.text:
            logger.error("profile do not contains payload identifier")
            return
        else:
            identifier = self.get_next_node(node_dict, 'PayloadIdentifier')
            logger.debug("Payload identifier: %s", identifier.text)

        node_payloads = self.get_child_node(node_dict, 'PayloadContent') 
        if not node_payloads.text:
            logger.error("profile do not contains any payload content");
            return
        
        node_payloads_val = self.get_next_node(node_dict, 'PayloadContent')
        if node_payloads_val.tag != 'array' or len(node_payloads_val.getchildren()) < 1:
            logger.error("The format of profile's payload content is invalid")
            return
        
        self.node_vpn = node_payloads_val.getchildren()[0]
        logger.debug('remote address: %s', config['remote_address'])
        node_ipsec_val = self.get_next_node(self.node_vpn, 'IPSec')
        node_ipsec_remote_addr_val = self.get_next_node(node_ipsec_val, 'RemoteAddress')
        node_ipsec_remote_addr_val.text = config['remote_address']
        self.node_ipsec_v = self.get_next_node(self.node_vpn, 'IPSec')

        root_ca = load_ca_from_file(config['root_ca'])
        if not root_ca:
            logger.error("load root ca error: %s", config['root_ca'])
            return
        vpn_ca = load_ca_from_file(config['vpn_ca'])
        if not vpn_ca:
            logger.error("load vpn ca error: %s", config['vpn_ca'])
            return
        self.issuer_ca = load_ca_from_file(config['issuer_ca'])
        if not self.issuer_ca:
            logger.error("load issuer ca error: %s", config['issuer_ca'])
            return
        self.issuer_key = load_key_from_file(config['issuer_key'], config['issuer_passcode'])
        if not self.issuer_key:
            logger.error("load issuer key error: %s", config['issuer_key'])
            return
        self.ssl_ca = load_ca_from_file(config['ssl_ca'])
        if not self.ssl_ca:
            logger.error("load ssl ca error: %s", config['ssl_ca'])
            return
        logger.debug("Finish loading ca and key from file")

        # root ca payload
        root_ca_payload = self.generate_payload()
        self.add_node(root_ca_payload, 'PayloadIdentifier', identifier.text + '.credential1', 'string')
        self.add_node(root_ca_payload, 'PayloadType', 'com.apple.security.root', 'string')
        self.add_node(root_ca_payload, 'PayloadDisplayName', 'MOBILEVPN ROOT CA', 'string')
        self.add_node(root_ca_payload, 'PayloadCertificateFileName', 'MOBILEVPN ROOT CA', 'string')
        self.add_node(root_ca_payload, 'PayloadContent', base64.encodestring(dumps_ca_to_string(root_ca)), 'data')
        node_payloads_val.append(root_ca_payload)
 
        # vpn ca payload
        vpn_ca_payload = self.generate_payload()
        self.add_node(vpn_ca_payload, 'PayloadIdentifier', identifier.text + '.credential2', 'string')
        self.add_node(vpn_ca_payload, 'PayloadType', 'com.apple.security.pkcs1', 'string')
        self.add_node(vpn_ca_payload, 'PayloadDisplayName', 'MOBILEVPN VPN CA', 'string')
        self.add_node(vpn_ca_payload, 'PayloadCertificateFileName', 'MOBILEVPN VPN CA', 'string')
        self.add_node(vpn_ca_payload, 'PayloadContent', base64.encodestring(dumps_ca_to_string(vpn_ca)), 'data')
        node_payloads_val.append(vpn_ca_payload)

        # issuer ca payload
        issuer_ca_payload = self.generate_payload()
        self.add_node(issuer_ca_payload, 'PayloadIdentifier', identifier.text + '.credential3', 'string')
        self.add_node(issuer_ca_payload, 'PayloadType', 'com.apple.security.pkcs1', 'string')
        self.add_node(issuer_ca_payload, 'PayloadDisplayName', 'MOBILE ES CA', 'string')
        self.add_node(issuer_ca_payload, 'PayloadCertificateFileName', 'MOBILE ES CA', 'string')
        self.add_node(issuer_ca_payload, 'PayloadContent', base64.encodestring(dumps_ca_to_string(self.issuer_ca)), 'data')
        node_payloads_val.append(issuer_ca_payload)

        # user certificate payload
        self.user_ca_payload = self.generate_payload()
        self.add_node(self.user_ca_payload, 'PayloadIdentifier', identifier.text + '.credential4', 'string')
        self.add_node(self.user_ca_payload, 'PayloadType', 'com.apple.security.pkcs12', 'string')
        self.add_node(self.user_ca_payload, 'Password', config['passout'], 'string')
        node_payloads_val.append(self.user_ca_payload)
        
        node_ipsec_udid_val = self.get_next_node(node_ipsec_val, 'PayloadCertificateUUID')
        node_ipsec_udid_val.text = self.get_next_node(self.user_ca_payload, 'PayloadUUID').text

        # ssl root ca
        ssl_ca_payload = self.generate_payload()
        self.add_node(ssl_ca_payload, 'PayloadIdentifier', identifier.text + '.credential5', 'string')
        self.add_node(ssl_ca_payload, 'PayloadType', 'com.apple.security.root', 'string')
        self.add_node(ssl_ca_payload, 'PayloadDisplayName', 'MOBILEProxy ROOT CA', 'string')
        self.add_node(ssl_ca_payload, 'PayloadCertificateFileName', 'MOBILEProxy ROOT CA', 'string')
        self.add_node(ssl_ca_payload, 'PayloadContent', base64.encodestring(dumps_ca_to_string(self.ssl_ca)), 'data')
        node_payloads_val.append(ssl_ca_payload)
        
        # activesync account
        self.activesync_payload = self.generate_payload()
        self.add_node(self.activesync_payload, 'PayloadIdentifier', 'com.websense.activesync.account', 'string')
        self.add_node(self.activesync_payload, 'PayloadType', 'com.apple.eas.account', 'string')
        self.add_node(self.activesync_payload, 'PayloadDisplayName', 'websense exchange activesync', 'string')
        #should read these information from conf
        self.add_node(self.activesync_payload, 'Host', config['asa_host'], 'string')
        self.add_node(self.activesync_payload, 'EmailAddress', config['asa_email_addr'], 'string') #just to work around password popup
        self.add_node(self.activesync_payload, 'CertificatePassword', config['passout'], 'string')
        self.add_node(self.activesync_payload, 'MailNumberOfPastDaysToSync', '0', 'integer')
        self.add_bool_node(self.activesync_payload, 'SSL', True)
        self.add_bool_node(self.activesync_payload, 'PreventMove', True)
        self.add_bool_node(self.activesync_payload, 'PreventAppSheet', True)


        node_payloads_val.append(self.activesync_payload)

        #set flag
        self.init_done = 1

 
    def dumps(self, user_info, pac_url, exceptlst, pkey, vpn_bypass_except, sn=None):
        """
        Dumps vpn profile to plist string.
        Parameter Notes:
            user_info(string): must contains Username and DeviceID keyword,
                        like "Username:someone@websense.com;DeviceID:someone's device"
            pack_url(string): a valid http or https url
        """
        p12, cn, expire_date = issuer_certificate(self.issuer_ca, self.issuer_key, user_info, config['passout'], pkey)
        if not p12 or not cn:
            return None,None

        data = dumps_p12_to_string(p12)
        if not data:
            return None,None
        
        self.activesync_ca_data = base64.encodestring(data);
        self.add_node(self.user_ca_payload, 'PayloadCertificateFileName', cn, 'string')
        self.add_node(self.user_ca_payload, 'PayloadDisplayName', cn, 'string')
        self.add_node(self.user_ca_payload, 'PayloadContent', self.activesync_ca_data, 'data')
        

        node_proxy_val = self.get_next_node(self.node_vpn, 'Proxies')
        node_proxy_url = self.get_next_node(node_proxy_val, 'ProxyAutoConfigURLString')
        node_proxy_url.text = self.update_pacfile_type(pac_url)

        if len(exceptlst) > 0:
            domain_match_node = self.get_next_node(self.node_ipsec_v, 'OnDemandMatchDomainsNever')
            d_node_val = self.get_domainaction_node() 

            for vpnexcept in exceptlst:
                try:
                    assert vpnexcept.has_key('attributes'), 'vpn exception dict do not has key: attributes'
                    node_except_string = ElementTree.SubElement(domain_match_node, 'string')
                    node_except_string1 = ElementTree.SubElement(d_node_val, 'string')

                    if vpnexcept['attributes'].has_key('domainName'):
                        node_except_string.text = vpnexcept["attributes"]["domainName"] 
                        node_except_string1.text = vpnexcept["attributes"]["domainName"]
                    elif vpnexcept['attributes'].has_key('ipaddress'):
                        node_except_string.text = vpnexcept["attributes"]["ipaddress"]
                        node_except_string1.text = vpnexcept["attributes"]["ipaddress"]
                    elif vpnexcept['attributes'].has_key('subnet'):
                        node_except_string.text = vpnexcept["attributes"]["subnet"]
                        node_except_string1.text = vpnexcept["attributes"]["subnet"]
                    else:
                        logger.debug('no domainName, ipaddress and subnet in vpn exception dict: %s' % vpnexcept)
                except Exception, ve:
                    logger.error("add vpn exception value to vpn profile error %s" % repr(ve))

        #add rules for local network access
        ondemandrules_node = self.get_next_node(self.node_ipsec_v, "OnDemandRules");
        self.add_vpn_ondemandrules(ondemandrules_node, vpn_bypass_except);

        # activesync account
        self.add_node(self.activesync_payload, 'Certificate', self.activesync_ca_data, 'data') #same with self.user_ca_payload

        #add encrypted serial number as user name for activesync
        if sn:
            logger.debug('will ADD username to activesync payload')
            #encrypted_sn = base64.b32encode(encrypt_sn(sn))
            encrypted_sn = base64.b32encode(sn)
            
            self.add_node(self.activesync_payload, 'UserName', encrypted_sn, 'string')
            self.add_node(self.activesync_payload, 'Password', 'fakedata', 'string')
        else:
            logger.debug('will NOT ADD username to activesync payload')

        try:
            plist = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n' + ElementTree.tostring(self.node_root)
            return plist, expire_date
        except Exception, e:
            return None,None
        return None,None
        pass

    def add_vpn_ondemandrules(self, node, vpn_bypass_except):
        if node is None:
            logger.info('OnDemandRules NOT found!');
            return;
        attr_val = None;
        if vpn_bypass_except and isinstance(vpn_bypass_except, dict):
            attr_val = vpn_bypass_except.get('attributes');
        attr_key = None;
        attr_key_val = None;
        if attr_val and isinstance(attr_val, dict):
            for (k, v) in attr_val.items():
                if k == 'LocalNetworkAccessKey':
                    if v:
                        attr_key = v[0]; #get value from list
                if k == 'LocalNetworkAccessValue':
                    if v:
                        attr_key_val = v[0];

        rules_array = node.getchildren(); #array in plist, list in python
        key_is_found = False;
        for element in rules_array: #element should be a dict
            for item in element:
                if item.text == attr_key:
                    key_is_found = True; #found!
                    continue;
                if key_is_found:
                    self.add_vpnexception(item, attr_key_val);
                    key_is_found = False; #clear!
                    break;

    def add_vpnexception(self, node, node_value):
        if node_value:
            except_list = node_value.split(',')
            for item in except_list:
                if item:
                    wifi_except_stringi= ElementTree.SubElement(node, 'string')
                    wifi_except_stringi.text = item;
        pass

    def get_domainaction_node(self):
        da_node_val = self.get_next_node(self.node_ipsec_v, 'OnDemandRules')
        da_node_dict = da_node_val.getchildren()[3]
        ap_node_val = self.get_next_node(da_node_dict, 'ActionParameters')
        if ap_node_val:
            ap_node_dict = ap_node_val.getchildren()[0]
        else:
            ap_node_dict = None
        d_node_val = self.get_next_node(ap_node_dict, 'Domains')
        return d_node_val

    def is_init_done(self):
        if self.init_done == 1:
            return True
        return False

    def init_status(self):
        return self.init_done

    def update_pacfile_type(self, pacfile):
        try:
            pr = urlparse.urlparse(pacfile)
            prlst = list(pr)

            query = dict(urlparse.parse_qsl(pr.query))
            #use port 8081 of proxy
            query["a"] = "n"
            #data will be send to cloud, not op, used for hybrid situation
            query["cli"] = "mob"
            prlst[4] = urllib.urlencode(query)
            return urlparse.ParseResult(*prlst).geturl()
        except Exception, e:
            logger.error("add mdm type to pac file url error %s" % repr(e))
            return pacfile

if __name__ == "__main__":
    vpn_profile = VPNProfile()
    pkey = generate_key(1)
    plist, edate= vpn_profile.dumps("Username:xli@websense.com;DeviceID:xli", "pac_url://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", [], pkey[0], {u'attributes': {u'LocalNetworkAccessValue': [u'MSG-Demo,Guest'], u'LocalNetworkAccessKey': [u'SSIDMatch']}});
    #plist, edate= vpn_profile.dumps("Username:endyongpeng1@websense.com;DeviceID:endyongpeng1", "pac_url://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", [], pkey[0],  {u'attributes': {u'LocalNetworkAccessValue': [u'10.32.8.10,10.32.8.11'], u'LocalNetworkAccessKey': [u'DNSServerAddressMatch']}}) 
    file = open('vpn.mobileconfig', 'w')
    file.write(plist)
    file.close()

