# -*- coding: utf-8 -*-
import os
import time
import json
import unittest
from configparser import ConfigParser
from os import environ
from pprint import pprint

from SetAPI.SetAPIImpl import SetAPI
from SetAPI.SetAPIServer import MethodContext
from SetAPI.authclient import KBaseAuth as _KBaseAuth
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.FakeObjectsForTestsClient import FakeObjectsForTests
from installed_clients.WorkspaceClient import Workspace as workspaceService


class SetAPITest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('SetAPI'):
            cls.cfg[nameval[0]] = nameval[1]
        authServiceUrl = cls.cfg.get('auth-service-url',
                "https://kbase.us/services/authorization/Sessions/Login")
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'SetAPI',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL, token=token)
        cls.serviceImpl = SetAPI(cls.cfg)
        cls.dfu = DataFileUtil(os.environ['SDK_CALLBACK_URL'])

        # setup data at the class level for now (so that the code is run
        # once for all tests, not before each test case.  Not sure how to
        # do that outside this function..)
        suffix = int(time.time() * 1000)
        wsName = "test_SetAPI_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': wsName})
        cls.wsName = wsName
        cls.prepare_data()

    @classmethod
    def prepare_data(cls):
        cls.sample_set_ref = "45700/57/1"

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_SetAPI_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})
        self.__class__.wsName = wsName
        return wsName

    def serviceImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def _compare_samples(self, s1, s2):
        self.assertEqual(s1['num_found'], s2['num_found'])
        self.assertEqual(s1['start'], s2['start'])
        self.assertEqual(s1['samples'], s2['samples'])

    # @unittest.skip('x')
    def test_sample_set_to_sample_info(self):
        ret = self.serviceImpl.sample_set_to_samples_info(self.ctx, {
            "ref": self.sample_set_ref,
            "start": 0,
            "limit": 10
        })[0]
        with open('data/sample_set_search_compare.json') as f:
            compare_to = json.load(f)
        self._compare_samples(ret, compare_to)

    # @unittest.skip('x')
    def test_query_search(self):
        ret = self.serviceImpl.sample_set_to_samples_info(self.ctx, {
            "ref": self.sample_set_ref,
            "start": 0,
            "limit": 10,
            "query": "Georgia"
        })[0]
        with open("data/sample_set_search_compare.json") as f:
            compare_to = json.load(f)
        # get the samples with state_province 'Georgia' only
        compare_to['samples'] = [s for s in compare_to['samples'] if s.get('state_province') and s['state_province'][0] == "Georgia"]
        compare_to['num_found'] = len(compare_to['samples'])
        self._compare_samples(ret, compare_to)
