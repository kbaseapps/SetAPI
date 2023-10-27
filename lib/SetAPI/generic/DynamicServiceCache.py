# -*- coding: utf-8 -*-

import time

from installed_clients.baseclient import BaseClient


class DynamicServiceCache:
    def __init__(self, sw_url, service_ver, module_name, refresh_cycle_seconds=300):
        self.sw_url = sw_url
        self.service_ver = service_ver
        self.module_name = module_name
        self.refresh_cycle_seconds = refresh_cycle_seconds
        self.cached_url = None
        self.last_refresh_time = None

    def call_method(self, method, params_array, token):
        was_url_refreshed = False
        if (not self.cached_url) or (
            time.time() - self.last_refresh_time > self.refresh_cycle_seconds
        ):
            self._lookup_url()
            was_url_refreshed = True
        try:
            return self._call(method, params_array, token)
        except:
            if was_url_refreshed:
                raise  # Forwarding error with no changes
            else:
                self._lookup_url()
                return self._call(method, params_array, token)

    def _lookup_url(self):
        bc = BaseClient(url=self.sw_url, lookup_url=False)
        self.cached_url = bc.call_method(
            "ServiceWizard.get_service_status",
            [{"module_name": self.module_name, "version": self.service_ver}],
        )["url"]
        self.last_refresh_time = time.time()

    def _call(self, method, params_array, token):
        bc = BaseClient(url=self.cached_url, token=token, lookup_url=False)
        return bc.call_method(self.module_name + "." + method, params_array)
