#!/usr/bin/env python2.6
#encoding=utf-8

import json
import os
import base64

import sys
if '/opt/mdmi/modules' not in sys.path:
	sys.path.append('/opt/mdmi/modules')

from hosteddb.hosted_taskqueue import HostedTaskQueue

class Email(object):
	'''
	class Email
		This class implements the operations about email
	
	Attributes:
		None
	'''
	def __init__(self):
		pass

	def send(self, account=1, mailfrom='bounce@websense.com', rcptto=None, substitutions=None, template=None, tags=None):
		'''
		TODO: Send email

		Params:
			account: Account ID.
			mailfrom: sender name.
			rcptto: Receiver name.
			substitutions: Email data.
			template: Template href.
			tags: User defined data in list.

		Return:
			=0 : Operation success.
			< 0 : Failed.
		'''
		if not rcptto or not substitutions or not template:
			raise Exception('Invalid input!')

		request = HostedTaskQueue()
		retval = 0
		data = {'mailfrom' : mailfrom,
				'rcptto' : rcptto,
				'substitutions' : substitutions,
				'template_href' : template
				}
		payload = json.dumps(data)
		payload = base64.encodestring(payload)
		result = request.do_add(tqname='email', namespace='email', account=account, version=1, payload=payload, tags=tags)
		if (retval >= 0) and ((result.code - 200) < 10):
			retval = 0
		else:
			retval = -1
		return retval
		pass

	def format_email_template_href(self, account=1, version=1, section=None):
		'''
		TODO: Format email template href

		Params:
			account: Account ID.
			version: Version of the resource.
			section: section name of the template.

		Return:
			href url.
		'''
		if section == None:
			raise Exception('Invalid input!')

		resource = 'https://wrest:8085/os/v-%d/account-%d/namespace-mobileglobal/object-emailtemplates/section-%s'
		href = resource % (version, account, section)
		return href
		pass
#end of Class Email

