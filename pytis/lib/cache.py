#import memcache
class Cache(object):
    pass 
    """
    def __init__(self, url, timeout=None, prefix=None):
        self.mc = memcache.Client([url]) 
        self.timeout = timeout or 300 
        self.prefix = prefix 

        if not self.mc.set('x', 'x', 1):
            raise InvalidCacheBackendError("Cannot connect to Memcached")

    def get(self, key): 
        return self.mc.get(key) 

    def set(self, key, value, timeout=None):
        if self.prefix: 
            key = self.prefix + key 

        self.mc.set(key, value, timeout or self.timeout)
    """