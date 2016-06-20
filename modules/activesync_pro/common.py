#!/usr/bin/env python2.6

import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
from hosteddb.hosted_device import HostedDevice
from hosteddb.hosted_user import HostedUser
from hosteddb.hosted_account import HostedAccount
from utils import logger
from airwatch.vpn_profile import AirwatchVPNProfile
from ConfigParser import ConfigParser
from M2Crypto.EVP import Cipher
import struct
import string

def get_serial_from_zpush(dev_id):
    if dev_id.startswith('appl'):
        return dev_id[len('appl'):]
    else:
        return None
    #return 'DMPJ89PUDVGK'

def get_device_info(serial_number):
    if not type(serial_number) == str:
        raise Exception('device serial number invalid')

    hosted_device = HostedDevice()
    dev_info = hosted_device.get_device_by_serial_number(serial_number)
    logger.debug('get dev info: %s' % dev_info)
    dev_info = dev_info['attributes']

    dev_owner = ''
    account_id = ''
    mdm_profile_id = ''

    if isinstance(dev_info, dict):
        if isinstance(dev_info['deviceOwner'], list) and len(dev_info['deviceOwner']) > 0:
            dev_owner = dev_info['deviceOwner'][0]
        else:
            dev_owner = dev_info['deviceOwner']

        if isinstance(dev_info['account'], list) and len(dev_info['account']) > 0:
            account_id = dev_info['account'][0]
        else:
            account_id = dev_info['account']

        if isinstance(dev_info['mdmProfileId'], list) and len(dev_info['mdmProfileId']) > 0:
            mdm_profile_id = dev_info['mdmProfileId'][0]
        else:
            mdm_profile_id = dev_info['mdmProfileId']
    else:
        logger.error('device info invalid: %s'% dev_info)
        raise Exception('device info type invalid')

    return dev_owner,account_id, mdm_profile_id

def get_user_object_class(dev_owner, account_id):
    hosted_user = HostedUser(account_id)
    user_info = hosted_user.get_user(dev_owner, 'objectClass')

    if isinstance(user_info, dict):
        d_user_info = user_info
    elif isinstance(user_info, list):
        if len(user_info) < 1:
            raise Exception('error ,get no user info')

        if type(user_info[0])!= dict:
            raise Exception('error, user info should be a dict')
        else:
            d_user_info = user_info[0]
    else:
        logger.error('user info invalid: %s' % user_info)
        raise Exception('user info invalid')

    object_class = d_user_info['attributes']['objectClass']

    return object_class


def get_activesync_whitelists(account, user_type):
    #get whitelist settings from RS first, and insert internal ip range, notice: should know user type (hosted, hybrid) first
    whitelist = []

    hosted_account = HostedAccount(account)
    hosted_networks = hosted_account.get_hosted_networks()
    logger.debug('hosted_networks are: %s'% hosted_networks)
    '''
    #for test
    hosted_networks = [
        {
            "href" : "https://localhost:8085/rs/v-1/account-130/cn-connection1%20%2828%29",
            "attributes" :
            {
                "cn" : [
                "connection1 (28)"
                ],
                "policy" : [
                "71"
                ],
                "objectClass" : [
                "hostedNetwork"
                ],
                "ipaddress" : [
                "10.255.40.1"
                ],
                "description" : [
                "connection1"
                ],
                "scope" : [
                "external"
                ]
            },
            "dn" : "cn=connection1 (28),account=130,dc=blackspider,dc=com"
        }
    ]
    '''
    if not isinstance(hosted_networks, list):
        hosted_networks = [hosted_networks]

    for item in hosted_networks:
        addr_from = ''
        addr_to = ''
        ip = ''

        item = item['attributes']
        #ipaddress
        if item.has_key('ipaddress'):
            condition = isinstance(item['ipaddress'], list)
            ip = item['ipaddress'][0] if condition else item['ipaddress']
            whitelist.append(ip)
        #iprange
        elif item.has_key('iprange'):
            #condition = isinstance(item['addrFrom'], list)
            (addr_from, addr_to) = item['iprange'].split('-')
            whitelist.append({'addrFrom':addr_from, 'addrTo':addr_to})
        #subnet
        elif item.has_key('subnet'):
            (subnet, cidr) = item['subnet'].split('/')
            whitelist.append({'subnet':subnet, 'cidr':cidr})
        else:
            logger.error('unrecgnized hosted network:%s' % item)
            pass
        
        #return internal ip range as default

    return whitelist;

def get_ip_int_value(str_ip):
    a, b, c, d = str_ip.split('.')
    a= string.atoi(a)
    b= string.atoi(b)
    c= string.atoi(c)
    d= string.atoi(d)
    data = struct.pack('BBBB', a, b, c, d)
    int_ip = struct.unpack('>I', data)
    int_ip = int_ip[0]
    return int_ip

def get_network_num(str_ip, str_cidr):
    int_ip = get_ip_int_value(str_ip)

    bit_len_network = string.atoi(str_cidr)

    int_network = int_ip >> (32-bit_len_network)

    return int_network

def srcip_allowed(src_ip, whitelists):
    #TODO:comare the ip address as expect format
    allowed = False
    for ip_item in whitelists:
        if isinstance(ip_item, dict):
            if ip_item.get('addrFrom') and ip_item.get('addrTo'):
                addr_from = ip_item.get('addrFrom')
                addr_to = ip_item.get('addrTo')
                int_addr_from = get_ip_int_value(addr_from)
                int_addr_to = get_ip_int_value(addr_to)
                int_src_ip = get_ip_int_value(src_ip)
                if (int_src_ip >= int_addr_from) and (int_src_ip <= int_addr_to):
                    logger.debug('source ip is in the range')
                    allowed = True
                    break
                else:
                    logger.debug('source ip is not in the range')
            elif ip_item.get('subnet') and ip_item.get('cidr'):
                subnet = ip_item.get('subnet')
                cidr = ip_item.get('cidr')

                network_num1 = get_network_num(subnet, cidr)
                network_num2 = get_network_num(src_ip, cidr)
                if network_num1 == network_num2:
                    allowed = True
                    break

        elif isinstance(ip_item, basestring):
            if ip_item == src_ip:
                allowed = True
                break
        else:
            continue
    return allowed

def repush_profile(account_id, serial_number, mdm_profile_id):
    try:
        aw_vpn_profile = AirwatchVPNProfile(account_id)
        aw_vpn_profile.install_profile_by_serialnumber(mdm_profile_id, serial_number)
        return 0
    except Exception, e:
        logger.error('install profile by serial number failed: %s' % serial_number)
        return 1

def decryptPasswd(buf, passKey, iv = '\x00' * 16):
    cipher = Cipher(alg='aes_128_cbc', key=passKey, iv=iv, op=0) # 0 is decrypt  
    cipher.set_padding(padding=7)
    v = cipher.update(buf)
    v = v + cipher.final()
    del cipher
    return v

def getPassKeyFromConfig(configFile = "/opt/mdmi/etc/mdmi.conf"):
    try:
        config = ConfigParser()
        config.read(configFile)
        if config._sections.has_key('vpn'):
            config = config._sections['vpn']
            if not config.has_key('passout'):
                logger.error('error, config file %s do not has key passout' % configFile)
                passKey = None
            else:
                passKey = config['passout']
        else:
            logger.error('error, %s do not have section vpn' % configFile)
            passKey = None
        return config['passout']
    except Exception, e:
        logger.error('error, can not get passout from %s' % configFile)
        return None
        

