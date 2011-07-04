# coding: utf-8

import time

from django.core.cache import cache


class LocalSyncCache(dict):
    last_reset = time.time()

    def __init__(self, id=None):
        if id is None:
            raise AssertionError("LocalSyncCache must take a id as argument.")
        self.id = id

    def start_request(self):
        """
        Check if we
        """
        global_update_time = cache.get(self.id)
        if global_update_time and self.last_reset < global_update_time:
            # We have outdated data -> reset dict
            dict.clear()
            self.last_reset = time.time()

    def clear(self):
        """
        Must be called from the process/thread witch change the data
        """
        self.clear(self)
        self.last_reset = time.time()
        cache.set(self.id, self.last_reset)


