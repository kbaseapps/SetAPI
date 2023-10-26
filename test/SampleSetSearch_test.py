# -*- coding: utf-8 -*-
import os
import time
import json
import unittest
from test.test_config import get_test_config
import pytest
from installed_clients.DataFileUtilClient import DataFileUtil


class SetAPITest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        props = get_test_config()
        for prop in ['cfg', 'ctx', 'serviceImpl', 'wsClient', 'wsName', 'wsURL']:
            setattr(cls, prop, props[prop])
        cls.dfu = DataFileUtil(os.environ['SDK_CALLBACK_URL'])
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
        assert s1['num_found'] == s2['num_found']
        assert s1['start'] == s2['start']
        assert s1['samples'] == s2['samples']

    # @unittest.skip('x')
    def test_param_error_conditions(self):
        # test without ref argument
        with pytest.raises(ValueError):
            self.serviceImpl.sample_set_to_samples_info(self.ctx, {
                "start": 0,
                "limit": 10
            })

        with pytest.raises(ValueError):
            self.serviceImpl.sample_set_to_samples_info(self.ctx, {})

    @unittest.skip('x')
    # test_sample_set_to_sample_info
    def test_sample_set_to_sample_info(self):
        # test defaults of "start" and "limit" variables
        ret = self.serviceImpl.sample_set_to_samples_info(self.ctx, {
            "ref": self.sample_set_ref,
        })[0]
        with open('data/sample_set_search_compare.json') as f:
            compare_to = json.load(f)
        self._compare_samples(ret, compare_to)

    @unittest.skip('x')
    # skipped because only particular users have permission to search
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

    @unittest.skip('x')
    # skipped because only particular users have permission to search
    def test_prefix_query_search(self):
        ret = self.serviceImpl.sample_set_to_samples_info(self.ctx, {
            "ref": self.sample_set_ref,
            "query": "Germa"
        })[0]
        with open("data/sample_set_search_compare.json") as f:
            compare_to = json.load(f)
        # get the samples with country 'Germany' only
        compare_to['samples'] = [s for s in compare_to['samples'] if s.get('country') and s['country'][0] == "Germany"]
        compare_to['num_found'] = len(compare_to['samples'])
        self._compare_samples(ret, compare_to)

    @unittest.skip('x')
    # skipped because only particular users have permission to search
    def test_prefix_query_search_2(self):
        ret = self.serviceImpl.sample_set_to_samples_info(self.ctx, {
            "ref": self.sample_set_ref,
            "query": "Ge"
        })[0]
        with open("data/sample_set_search_compare.json") as f:
            compare_to = json.load(f)
        # get the samples with country 'Germany' only
        compare_to['samples'] = [s for s in compare_to['samples'] if (s.get('country') and s['country'][0] == "Germany") or (s.get('state_province') and s['state_province'][0] == "Georgia")]
        compare_to['num_found'] = len(compare_to['samples'])
        self._compare_samples(ret, compare_to)
