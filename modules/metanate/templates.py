# -*- coding: utf-8 -*-

import random, string
from datetime import datetime
from cStringIO import StringIO
from ldif import LDIFWriter, LDIFParser

from utils import logger

templates = {
    'CREATESESSION': [
            ("cn=Client", {
            "objectClass": ["Client"],
            "cn": ["Client"],
            "protocolVersion": ["1"],
            "sync": ["{object_class}"],
            "syncSource": ["{sync_source}"],
            "failedAttempts": ["1"], })
        ,
            ("cn=Attempt 1", {
            "objectClass": ["Attempt"],
            "cn": ["Attempt 1"],
            "dateAndTime": ["{current_time}"],
            })
    ],
    'CLOSESESSION': [
        ("cn=Summary", {
        "ObjectClass": ["Summary"],
        "cn": ["Summary"],
        "Additions": ["{additions}"],
        "Deletions": ["{deletions}"],
        "directoryLookupTime": ["{directory_lookup_time}"],
        "DeltaCalculationTime": ["{delta_calc_time}"],
        "SynchronisationTime": ["{sync_time}"],
        "CommitTime": ["{commit_time}"],
        "Report": ["{additions} additions, {deletions} deletions"],
        "Report": ["Total time {total_time} seconds"],
        "Logging": ["{log_msg}"], })
    ]
}

def generate_ldif(action, use_template=False, sync_source='MDM', **kwargs):
    """generate ldif string by kwargs or from template.
    Parameters:
        use_template: boolean,'CREATESESSION' and 'CLOSESESSION' should use template, others False.
        sync_source: 'MDM' or 'Directory'
        **kwargs: all items of dict.
    """
    output = StringIO()
    w = LDIFWriter(output)
    if use_template:
        if not templates.has_key(action):
            return ""

        d = templates[action]
        for i in d:
            w.unparse(*i)

        output.reset()
        r = output.read()
        output.close()

        if sync_source:
            r = r.format(sync_source=sync_source, current_time=datetime.today().strftime("%Y%m%d%H%M%SZ"), **kwargs)
        else:
            r = r.format(**kwargs)

        return r
    else:
        if not kwargs.has_key('dn'):
            output.close()
            return ""
        dn = kwargs.pop('dn')
        for k, v in kwargs.iteritems():
            if not isinstance(v, list):
                kwargs[k] = [v]

        w.unparse(dn, kwargs)

        output.reset()
        r = output.read()
        output.close()

        return r

def generate_ldif_from_list(action, array):
    """generate ldif string by array
    Parameters:
        array: a list contains several dicts which contains user or group info.
    """
    if isinstance(array, list):
        output = StringIO()
        w = LDIFWriter(output)
        for a in array:
            if a.has_key('dn'):
                dn = a.pop('dn')
                for k, v in a.iteritems():
                    if not isinstance(v, list):
                        a[k] = [v]

                w.unparse(dn, a)
            else:
                logger.error('the element of ldif does not have "dn": %s', a)


        output.reset()
        r = output.read()
        output.close()

        return r

def generate_boundary(length=5):
    """generate random string
    """
    r = random.SystemRandom()
    alphabet = string.ascii_letters + string.digits
    b = str().join(r.choice(alphabet) for _ in range(length))
    return b

def parse_ldif(ldif):
    """convert ldif to list; the item of list is tuple,
    the first item is dn, the second is a dict contains ldap attributes.
    """
    input = StringIO()
    input.write(ldif)
    # reset the file pointer, to make it point the begin of StringIO
    input.reset()
    parser = _MDMiLDIFParser(input)
    parser.parse()
    input.close()

    return parser.all_records

class _MDMiLDIFParser(LDIFParser):
    def __init__(self, input):
        LDIFParser.__init__(self, input)
        self.all_records = []

    def handle(self, dn, entry):
        self.all_records.append((dn, entry))

    def parse(self):
        """
        Continuously read and parse LDIF records
        """
        self._line = self._input_file.readline()

        while self._line and \
                (not self._max_entries or self.records_read < self._max_entries):
          # Reset record
          dn = None; changetype = None; entry = {}

          attr_type, attr_value = self._parseAttrTypeandValue()

          while attr_type != None and attr_value != None:
              if attr_type == 'dn':
                  # attr type and value pair was DN of LDIF record
                  if dn != None:
                      raise ValueError, 'Two lines starting with dn: in one record.'
                  dn = attr_value
              elif attr_type == 'version' and dn is None:
                  # version = 1
                  pass
              elif attr_type == 'changetype':
                  # attr type and value pair was DN of LDIF record
                  if dn is None:
                      raise ValueError, 'Read changetype: before getting valid dn: line.'
                  if changetype != None:
                      raise ValueError, 'Two lines starting with changetype: in one record.'
                  # if not valid_changetype_dict.has_key(attr_value):
                  if attr_value in ['add', 'delete', 'modify', 'modrdn']:
                      raise ValueError, 'changetype value %s is invalid.' % (repr(attr_value))
                  changetype = attr_value
              elif attr_value != None and \
                      not self._ignored_attr_types.has_key(attr_type.lower()):
                          # Add the attribute to the entry if not ignored attribute
                 if entry.has_key(attr_type):
                     entry[attr_type].append(attr_value)
                 else:
                     entry[attr_type] = [attr_value]

              # Read the next line within an entry
              attr_type, attr_value = self._parseAttrTypeandValue()

          if dn and entry:
              # append entry to result list
                self.handle(dn, entry)
                self.records_read = self.records_read + 1

        return  # parse()
