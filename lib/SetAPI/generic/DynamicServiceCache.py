# -*- coding: utf-8 -*-

try:
    # baseclient and this client are in a package
    from .baseclient import BaseClient as _BaseClient  # @UnusedImport
except:
    # no they aren't
    from baseclient import BaseClient as _BaseClient  # @Reimport

class DynamicServiceCache:

    def __init__(self, sw_url, service_ver, module_name):
        self.sw_url = sw_url
        self.service_ver = service_ver
        self.module_name = module_name
        self.cached_url = None

    def call_method(self, method, params_array, token):
        was_url_refreshed = False
        if not self.cached_url:
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
        bc = _BaseClient(url=self.sw_url, lookup_url=False)
        self.cached_url = bc.call_method('ServiceWizard.get_service_status',
                                         [{'module_name': self.module_name, 
                                           'version': self.service_ver}])['url']

    def _call(self, method, params_array, token):
        bc = _BaseClient(url=self.cached_url, token=token, lookup_url=False)
        return bc.call_method(self.module_name + '.' + method, params_array)
