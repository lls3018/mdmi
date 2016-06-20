# -*- coding: utf-8 -*-
import sys
if '/opt/mdmi/modules' not in sys.path:
    sys.path.append('/opt/mdmi/modules')
import json
import ldap.filter

from utils import logger

from hosteddb.hosted_access import HostedAccess

BASE_INFINITE = -1
MAX_RS_RESULT_SIZE = 500

class HostedBase(object):
    def __init__(self, account_id, version=1):
        self.account_id = account_id
        self.version = 1
        self.rest = HostedAccess()
        self.vlv_enable = False
        self.vlv_sortby = 'cn'
        self.vlv_page_size = MAX_RS_RESULT_SIZE
        self.vlv_enable_refresh = True

    def __del__(self):
        try:
            if self.rest:
                del self.rest
        except Exception as e:
            logger.error("exception in defining variable: %s", e)

    def get_by_filter(self, extra_attrs, filter, *args):
        filter = self._generate_filter(extra_attrs, True, filter, None, *args)
        return self._do_get_action(filter)

    def get_by_filter_without_base(self, extra_attrs, filter, *args):
        filter = self._generate_filter(extra_attrs, False, filter, None, *args)
        return self._do_get_action(filter)

    def init_vlv(self, enable=False, sortby='', max_page_size=MAX_RS_RESULT_SIZE):
        self.vlv_enable = enable
        if self.vlv_enable:
            assert((sortby) and (max_page_size > 0)) #check params were available
            self.vlv_sortby = sortby
            self.vlv_page_size = max_page_size
            self.vlv_enable_refresh = True #force to refresh records section at first round

    def _generate_vlv_filter(self, page_idx, page_size):
        filter = {}
        filter['sort'] = [self.vlv_sortby] #require a list

        vlvdic = {}
        vlvdic['before'] = 0
        vlvdic['after'] = page_size - 1
        vlvdic['offset'] = page_idx * page_size + 1
        if self.vlv_enable_refresh:
            self.vlv_enable_refresh = False
            vlvdic['force_new_session'] = True
        filter['vlv'] = vlvdic
        return filter

    def _do_get_action(self, filter):
        resource = "/rs/v-%d/search" % self.version
        result = self.rest.do_access(resource, method_name="POST", data=filter)
        if not result:
            return result
        d = self.parse_result(result)
        while isinstance(d, list) and len(d) == 1:
            d = d[0]
        if isinstance(d, dict) and d.has_key('attributes') and isinstance(d['attributes'], dict):
            for k in d['attributes']:
                if isinstance(d['attributes'][k], list) and len(d['attributes'][k]) == 1:
                    d['attributes'][k] = d['attributes'][k][0]
        elif isinstance(d, list):
            for item in d:
                if item.has_key('attributes'):
                    if isinstance(item['attributes'], list):
                        for k in item['attributes']:
                            if isinstance(item['attributes'][k], list) and len(item['attributes'][k]) == 1:
                                item['attributes'][k] = item['attributes'][k][0]
                    else:
                        attributes = item['attributes']
                        for k in attributes:
                            if isinstance(attributes[k], list) and len(attributes[k]) == 1:
                                attributes[k] = attributes[k][0]

        return d

    def parse_result(self, data):
        if data.content_length > 0 and data.content_type == "application/json":
                return json.loads(data.content)
        else:
            return None

    def parse_param(self, data):
        if isinstance(data, dict):
            return json.dumps(data)
        
        return data

    def _generate_filter(self, extra_attrs, use_base, filter, vlvfilter, *args):
        dic = {}
        if vlvfilter:
            dic = vlvfilter #fill vlv settings

        if use_base:
            dic["base"] = '='.join(['account', str(self.account_id)])

        if args:
            escaped_args = [ldap.filter.escape_filter_chars(arg) if isinstance(arg, basestring) else arg for arg in args]
            filter = filter % tuple(escaped_args)
        dic['filter'] = filter
        attrs = self._generate_attrs(extra_attrs)
        if attrs:
            dic['attrs'] = attrs

        return json.dumps(dic)

    def _generate_attrs(self, extra):
        #implement at subclass
        return []

    def get_records_in_order(self, max, base_enable, extra_attrs, filter, *args):
        assert(self.vlv_enable) #Requires called init_vlv at first
        retval = []
        idx = 0
        page_size = self.vlv_page_size
        if max <= BASE_INFINITE: #require for all records
            page_size = self.vlv_page_size
        elif max < self.vlv_page_size:
            page_size = max

        while True:
            vlv_filter = self._generate_vlv_filter(idx, page_size)
            search_filter = self._generate_filter(extra_attrs, base_enable, filter, vlv_filter, *args)
            results = self._do_get_action(search_filter)
            if isinstance(results, dict): #RS would return a dict if there was only one record
                results = [results]
            if results and isinstance(results, list):
                retval.extend(results)
            else:
                logger.warning('Unexpected data!')
                break #unexpected data
            if len(results) == max:
                break
            elif len(results) < self.vlv_page_size: #get all information already
                break
            else:
                idx += 1
        return retval

    def get_all_records_in_order(self, sortby, base_enable, extra_attrs, filter, *args):
        self.init_vlv(True, sortby, MAX_RS_RESULT_SIZE)
        return self.get_records_in_order(BASE_INFINITE, True, extra_attrs, filter, *args)

