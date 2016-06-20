#! /usr/bin/python
# fileName: setup.py
#encoding=utf-8

import sys
sys.path.append("/opt/mdmi/modules")

from utils import logger
from hosteddb.hosted_taskqueue import HostedTaskQueue

class SetUp(object):
	"""
	initialize taskqueues 'iosdeployretry', 'iosdeployerror', 'androiddeployretry', 'androiddeployerror'
	"""	
	def init_task(self):
		"""
		initialize deployment task queues
		"""
		self.init_task_queue('iosdeployretry')
		self.init_task_queue('iosdeployerror')
		self.init_task_queue('androiddeployretry')
		self.init_task_queue('androiddeployerror')

	def init_task_queue(self, qName):
		try:
			tq = HostedTaskQueue()
			data = {"description" : "deployment task queue", "max_leases" : "30", "max_age" : "0"}
			logger.info("initialize task queue start")
			result = tq.do_establish_taskqueue(tqname=qName, description=data)
			if not result:
				logger.error("taskqueue '%s' establish failed!" % qName)
			else:
				logger.info("taskqueue '%s' initialize end!" % (qName))
		except Exception, e:
			logger.error("initialize taskqueue '%s' error %s" % (qName, e))
			raise Exception("initialize taskqueue '%s' error" % qName)

def main():
	sp = SetUp()
	sp.init_task()

if __name__ == '__main__':
	try:
		main()	
	except Exception, e:
		logger.error("initialize deployment retry and error queue error %s" % e)
		sys.exit(1)	
	sys.exit(0)
