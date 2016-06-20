#!/usr/bin/env python
'''
This script is used to update VPN certificate for given device UDID(s) via two ways(Command line option(-u) or file import(-f))
-f: Specify a file containing a device UDID each line
-u: a comma-separated option to specify device UDID(s). Notes: Please don't add white space after comma.
-a: Update all VPN certificates under given account(s) 
-w: How many update requests you want to send each second. Value 50 would be used by default. This option only takes effect with -a together.
-h: The Usage for this script
-v: When running, produce (slightly more) verbose output.

Output: This script will generate a file called 'failed_device.txt' which would contain the udid of the devices failed to update certificate.
You can retry to update by issuing 'python tools_update_certs.py -f failed_device.txt -v' after fixing the issue.
'''

import os
import sys
import time
import json
import getopt
import threading
mdmi_path = '/opt/mdmi/modules'
if not mdmi_path in sys.path:
    sys.path.append(mdmi_path)
from Queue import Queue
from hosteddb.hosted_device import HostedDevice
from hosteddb.hosted_account import HostedAccount
from airwatch.vpn_profile import AirwatchVPNProfile

def usage():
    s = os.path.basename(sys.argv[0])
    for opt in ['-%s' % short_opt for short_opt in short_opts] + ['--%s' % long_opt for long_opt in long_opts]:
        s += ' [%s]' % opt
        if len(s) > 80:
            print s
            s = '    '
    if s.strip():
        print s

short_opts = 'hvw:f:u:a:'
long_opts = ['help', 'verbose', 'worker=', 'file=', 'udids=', 'account=']
try:
    opts, args = getopt.getopt(sys.argv[1:], short_opts, long_opts)
except getopt.GetoptError, e:
    print e
    usage()
    sys.exit(1)

verbose = 0
worker_max = 50

file = None
udids = None
accounts = None

for o, a in opts:
    if o in ('-w', '--worker',):
        worker_max = int(a)
    elif o in ('-u', '--udids',):
        udids = a
    elif o in ('-a', '--account',):
        accounts = a
    elif o in ('-f', '--file',):
        file = a
    elif o in ('-v', '--verbose',):
        verbose += 1
    elif o in ('-h', '--help',):
        usage()
        sys.exit(0)

def update_certs_by_device_udid(udids=None):
    udid_array = udids.split(',')
    for udid in udid_array:
        do_update(udid)

def update_certs_by_accounts(accounts=None):
    if accounts == "all":
        account_array = HostedAccount().get_airwatch_account_ids()
    else:
        account_array = accounts.split(',')

    if verbose > 0:
        print "MDMi enabled accounts: %s" % account_array

    thread_list = []
    device_total = []
    for account_id in account_array:
        hosted_device = HostedDevice()
        idx = 0
        max = 100
        total = 0
        try:
            while idx >= 0:
                result = hosted_device.do_get_many(idx, max, 'account', account=account_id, deviceEnrollmentStatus='1')
                if result.code >= 200 and result.code < 300:
                    device_list = json.loads(result.content)
                    for device in device_list:
                        #udid = device['attributes']['UDID'][0]
                        device_total.append(device)
                    if len(device_list) == max:
                        idx = idx + 1
                    else:
                        idx = -1
        except Exception, e:
            print "Failed to update the certificate for the account: %s, error message: %s\n" % (account_id, str(e))
        finally:
            del hosted_device

    count = 1;
    for i in xrange(0, len(device_total)):
        device = device_total[i]
        worker = threading.Thread(target=do_update, args=(device['attributes']['UDID'][0], device,))
        worker.start()
        thread_list.append(worker)

        if i/worker_max == count:
            count += 1
            time.sleep(1)
    for worker in thread_list:
        worker.join()

def update_certs_by_file(file=None):
    with open(file, 'r') as f:
        for udid in f:
            do_update(udid.rstrip('\n').rstrip('\r\n'))

global queue
queue  = Queue()
def do_update(udid, device=None):
    try:
        if not device:
            hostedDevice = HostedDevice(udid)
            result = hostedDevice.do_get()
            device = json.loads(result.content)[0]

        if verbose > 0:
            print "Starting off update the certification for the device: %s" % udid
            print "Device information: %s" % str(device)

        device_attr = device['attributes']
        profile_id = device_attr['mdmProfileId'][0]
        account_id = device_attr['account'][0]
        if verbose > 0:
            print "The profile id for this device: %s" % profile_id

        if AirwatchVPNProfile(account_id).install_profile_by_udid(profile_id, udid):
            print "Succeeded in certificate update for the device: %s\n" % udid
        else:
            queue.put(udid)
            print "Failed to update the certificate for the device: %s\n" % udid
    except Exception, e:
        queue.put(udid)
        print "Failed to update the certificate for the device: %s, error message: %s\n" % (udid, str(e))

try:
    if udids:
        update_certs_by_device_udid(udids)
    elif accounts:
        update_certs_by_accounts(accounts)
    elif file:
        update_certs_by_file(file)

    f = open('failed_device.txt', 'w')
    while not queue.empty():
        f.write("%s\n" % queue.get())
except Exception, e:
    print "Failed to update VPN certificate, error message: %s" % e
finally:
    if f:
        f.close()
