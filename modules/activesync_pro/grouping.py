#!/usr/bin/env python2.6

import memcache

class ASAMemcache(object):
    def __init__(self, memcached_host = "localhost", memcached_port = "11211"):
        self.mc = memcache.Client([":".join([memcached_host, memcached_port])], debug=0)

    def __del__(self):
        del self.mc

    def ip_is_incache(self, source_ip, grouping_timeout_val=60):
        val = self.mc.get(source_ip)
        if val:
            ret = True
        else:
            self.mc.set(source_ip, source_ip, grouping_timeout_val)
            ret = False

        return ret

    def memcache_delete(self, ip, timeout=0):
        return self.mc.delete(ip, timeout)
