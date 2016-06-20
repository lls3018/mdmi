#! /usr/bin/python
# encoding = UTF-8

import os
import sys
import ConfigParser
import string
import json
from datetime import datetime
sys.path.append("/opt/mdmi/modules")
from utils import logger
from hosteddb.hosted_device import HostedDevice
from airwatch.vpn_profile import AirwatchVPNProfile 
from utils.error import MDMiHttpError

MASTER_SERVER_FILE = '/etc/sysconfig/mdmi.config'
CRONJOB_CONFIG_DIR = '/tmp/mdmi/'
CRONJOB_CONFIG_FILE = '/tmp/mdmi/mdmi-cronjob-updatevpnprofile.ini'
CRONJOB_DEVICE_INFO_DIR = '/tmp/mdmi/device/'

class UpdateVPNProfile():
	
	g_total_num = 0
	g_threshold_num = 100
	g_list_content = []
		
	def check_master_server(self):
		'''
			check whether the current server is master server
		'''
		if(os.path.isfile(MASTER_SERVER_FILE)):
			return True
		else:
			return False

	def initial_configuration(self):
		'''
			record current retrieve device time and , avoid multiple retrieving device info one day.
		'''
		if not os.path.exists(CRONJOB_DEVICE_INFO_DIR):
			os.makedirs(CRONJOB_DEVICE_INFO_DIR)
	
		if os.path.exists(CRONJOB_CONFIG_DIR):
			if os.path.isfile(CRONJOB_CONFIG_FILE):
				return self.parse_configuration_file()
			else:
				return self.create_configuration_file()
		else:
			os.mkdir(CRONJOB_CONFIG_DIR)
			return self.create_configuration_file()
		pass

	def get_devices(self):
		'''
			get devices from RS, return all the devices that vpn will expire in 7 days
		'''
		device = HostedDevice()
		rtn = 1
		page_num = 0
		page_size = 400
		while rtn > 0:
			result = device.do_get_many(page_num, page_size, 'devicePlatform')
			page_num += 1
			val = json.loads(result.content)
			self.parse_expire_device(val)
			rtn = len(val)
		self.save_expire_device()
		self.record_retrieve_date()

	def record_retrieve_date(self):
		conf = ConfigParser.SafeConfigParser()
		try:
			if not conf.read(CRONJOB_CONFIG_FILE):
				logger.info('Can not read %s' % CRONJOB_CONFIG_FILE)
			conf.set('mdmi-updatevpnprofile', 'cronjob_retrieve_device_date', datetime.now().strftime('%Y-%m-%d'))
			conf.write(open(CRONJOB_CONFIG_FILE, 'w'))
		except Exception, e:
			logger.error('record retrieve device date error %s ' % e)

	def parse_expire_device(self, result):
		for key in result:
			if key.has_key('attributes'):
				attr = key['attributes']
				if attr.has_key('certExpiryDate') and attr.has_key('UDID') and attr.has_key('mdmProfileId') and attr.has_key('account'):
					self.statistic_expire_num(attr)
					
	def statistic_expire_num(self, attributes):
		ed = attributes['certExpiryDate'][0]
		if self.compare_date(ed):
			self.g_list_content.append(attributes)
			self.g_total_num += 1
					
	def save_expire_device(self):
		'''
			save the device info to file, if the number of device is greater than threhold, save device info to different files and the number of device inro in each file is perhour_num
		'''
		if self.g_total_num > self.g_threshold_num:
			per_hour_num = self.g_total_num / 24
			for i in range(0, 23):
				filename = datetime.now().strftime('%Y%m%d') + "_" + str(i) 
				if i == 0:
					if len(self.g_list_content[0 : per_hour_num]) > 0:
						self.write_file(filename, json.dumps(self.g_list_content[0 : per_hour_num]))
				elif i == 22:
					if len(self.g_list_content[i * per_hour_num : ]) > 0:
						self.write_file(filename, json.dumps(self.g_list_content[i * per_hour_num : ]))
				else:
					if len(self.g_list_content[i * per_hour_num : (i + 1) * per_hour_num]) > 0:
						self.write_file(filename, json.dumps(self.g_list_content[i * per_hour_num : (i + 1) * per_hour_num]))
		else:
			filename = datetime.now().strftime('%Y%m%d')
			self.write_file(filename, json.dumps(self.g_list_content[0 : ]))
		pass

	def compare_date(self, expire_date):
		now = datetime.now()
		rd = datetime.strptime(expire_date, '%Y/%m/%d')
		delta = rd - now
		if delta.days < 7:
			return True
		else:
			return False
		pass

	def write_file(self, filename, content):
		try:
			file = open(CRONJOB_DEVICE_INFO_DIR + filename, 'a')
			file.write(content)
			file.close()
		except Exception, e:
			logger.error('write device info to tmp file error %s ' % e)

	def read_file(self):
		content = None
		try:
			for item in os.listdir(CRONJOB_DEVICE_INFO_DIR):
				itemsrc = os.path.join(CRONJOB_DEVICE_INFO_DIR, item)
				file = open(itemsrc, 'r')
				content = file.read()
				file.close()
				os.remove(itemsrc)
				break
		except Exception, e:
			content = None
			logger.error('read device info from tmp file error %s' % e)
		return content

	def has_retrieved(self, retrieve_date):
		now = datetime.now()
		rd = datetime.strptime(retrieve_date, '%Y-%m-%d')
		delta = now - rd
		if delta.days > 0:
			return False
		else:
			return True
		pass

	def parse_configuration_file(self):
		conf = ConfigParser.SafeConfigParser()
		try:
			if not conf.read(CRONJOB_CONFIG_FILE):
				logger.info('Can not read %s' % CRONJOB_CONFIG_FILE)
				return None, None
			retrieve_date = conf.get('mdmi-updatevpnprofile', 'cronjob_retrieve_device_date')
			threshold_num = string.atoi(conf.get('mdmi-updatevpnprofile', 'cronjob_threshold_num'))
			self.g_threshold_num = threshold_num
			return retrieve_date, threshold_num
		except Exception, e:
			logger.error('parse configuration file error %s' % e)
			return None, None

	def create_configuration_file(self):
		try:
			now = datetime.now().strftime('%Y-%m-%d')
			threshold_num = 100
			file = open(CRONJOB_CONFIG_FILE, 'w')
			file.write('[mdmi-updatevpnprofile]\n')
			file.write('cronjob_threshold_num=%d\n' % threshold_num)
			file.write('cronjob_retrieve_device_date=%s\n' % now)
			self.g_threshold_num = threshold_num
			file.close()
			return now, threshold_num 
		except Exception, e:
			logger.error('create configuration file error %s' % e)
			return None, None
		pass


	def push_vpn_profile_to_airwatch(self):
		'''
			push vpn profile to end device before VPN profile expiration in 7 days
		'''
		try:
			content = self.read_file()
			if content:
				logger.info('push vpn profile to device start...')
				attrs = json.loads(content)
				for attr in attrs:
					profile = AirwatchVPNProfile(int(attr['account'][0]))
					rtn_install = profile.install_profile_by_udid(attr['mdmProfileId'][0], attr['UDID'][0])
					if rtn_install:
						logger.info('install profile to device by UDID: %s success' % attr['UDID'][0])
					else:
						logger.error('install profile to device by UDID: %s fail' % attr['UDID'][0])
			else:
				logger.info('there is no vpn profile need to push ...')
		except MDMiHttpError, m1:
			logger.error('access airwtch error, update vpn profile failed %s' % m1)
		except Exception, e:
			logger.error('update vpn profile failed %s' % e)
		pass



if __name__ == '__main__':
    #estimate localhost is master
    result =  os.path.exists('/etc/sysconfig/mes.primary')
    if result:
        logger.info('update vpn profile cronjob start...')
        try:
		    updateVPN = UpdateVPNProfile()
		    logger.info('check whether current server is master')
		    #check_master = updateVPN.check_master_server()
		    #if check_master:
		    #logger.info('current server is the master server')
		    logger.info('initial configuration')
		    retrieve_date, threshold_num = updateVPN.initial_configuration()
		    rtn_retrieve = updateVPN.has_retrieved(retrieve_date)
		    if not rtn_retrieve:
			    logger.info('get devices from RS start')
			    updateVPN.get_devices()
			    logger.info('get devices from RS end, the number of device that vpn expire in 7 days is %d ' % updateVPN.g_total_num)
		    logger.info('re-install vpn profile')
		    updateVPN.push_vpn_profile_to_airwatch()
		    #else:
		    #	logger.info('current server is not the master server')
        except Exception, e:
		    logger.info('update vpn profile cronjob error %s' % e)
        logger.info('update vpn profile cronjob end...')
    else:
        logger.info('localhost is not master')



















