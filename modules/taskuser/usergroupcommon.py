#!/usr/bin/python

#TASK QUEUE NAME: enrollment
TASK_QUEUE_ENROLLMENT = 'enrollment'
#TASK QUEUE NAME: usergroup
TASK_QUEUE_USERGROUP = 'usergroup'
#TASK QUEUE NAME: usergrouperror
TASK_QUEUE_USERGROUP_ERROR = 'usergrouperror'
#TASK QUEUE NAME: usergrouppending
TASK_QUEUE_USERGROUP_PENDING = 'usergrouppending'
#TASK QUEUE NAME: usergroupretry
TASK_QUEUE_USERGROUP_RETRY = 'usergroupretry'
#TASK QUEUE NAME: usergroupperiodic
TASK_QUEUE_USERGROUP_PERIODIC = 'usergroupperiodic'
#Max retries on a single task
MAX_RETRIES = 5
#The account number for blackspider
ACCOUNT_BLACK_SPIDER = 1

TASK_QUEUE_OUTPUT_BEGIN = '--- TASK QUEUE PROCESSOR OUTPUT BEGIN ---'
TASK_QUEUE_OUTPUT_END = '--- TASK QUEUE PROCESSOR OUTPUT END ---'

def is_mdm_user(user):
    attr = user['attributes']
    return 'syncSource' in attr and attr['syncSource'] == 'MDM'

def is_directory_user(user):
    attr = user['attributes']
    return 'syncSource' in attr and attr['syncSource'] == 'Directory' or (
            'syncSource' not in attr and 'uid' in attr)

def convert_guid_to_binary_format(guid):
    try:
        reordered_guid = reorder_guid(guid)
        binary_format = reordered_guid.decode('hex')
        return binary_format
    except Exception:
        return guid

def reorder_guid(guid):
    parts = guid.split('-')
    for i in range(0, 3):
        length = len(parts[i])
        char_array = [None] * length
        for j in range(0, length, 2):
            char_array[j] = parts[i][length - j - 2]
            char_array[j + 1] = parts[i][length - j - 1]
        parts[i] = ''.join(char_array)
    return ''.join(parts)

class InvalidTaskException(Exception):
    def __init__(self, task, message):
        super(InvalidTaskException, self).__init__()
        self.message = str(message)
        self.task = task

    def __str__(self):
        return "InvalidTaskException: %s" % (self.message)

class DuplicatedEmailAddressException(Exception):
    def __init__(self, email_address):
        super(DuplicatedEmailAddressException, self).__init__()
        self.email_address = email_address

    def __str__(self):
        return 'Duplicated Email Address: %s' % self.email_address
