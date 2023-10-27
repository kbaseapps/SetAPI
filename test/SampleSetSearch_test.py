# -*- coding: utf-8 -*-
import json
import os
import time
import unittest
from test import TEST_BASE_DIR
from test.conftest import WS_NAME, test_config

import pytest
from installed_clients.DataFileUtilClient import DataFileUtil

SAMPLES_TEST_DATA = None
with open(os.path.join(TEST_BASE_DIR, "data", "sample_set_search_compare.json")) as f:
     SAMPLES_TEST_DATA = json.load(f)


class SetAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        props = test_config()
        for prop in ["cfg", "ctx", "serviceImpl", "wsClient", "wsName", "wsURL"]:
            setattr(cls, prop, props[prop])
        cls.dfu = DataFileUtil(os.environ["SDK_CALLBACK_URL"])
        cls.sample_set_ref = "45700/57/1"

    def getWsClient(self):
        return self.__class__.wsClient

    def serviceImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def _compare_samples(self, s1, s2):
        assert s1["num_found"] == s2["num_found"]
        assert s1["start"] == s2["start"]
        assert s1["samples"] == s2["samples"]

    # @unittest.skip('x')
    def test_param_error_conditions(self):
        # test without ref argument
        with pytest.raises(
            ValueError,
            match="Argument 'ref' must be specified, 'ref' = 'None'"
        ):
            self.serviceImpl.sample_set_to_samples_info(
                self.ctx, {"start": 0, "limit": 10}
            )

    def test_param_error_conditions_empty_params(self):
        with pytest.raises(
            ValueError,
            match="Argument 'ref' must be specified, 'ref' = 'None'"
        ):
            self.serviceImpl.sample_set_to_samples_info(self.ctx, {})

    @unittest.skip("only particular users have permission to search")
    # test_sample_set_to_sample_info
    def test_sample_set_to_sample_info(self):
        # test defaults of "start" and "limit" variables
        ret = self.serviceImpl.sample_set_to_samples_info(
            self.ctx,
            {
                "ref": self.sample_set_ref,
            },
        )[0]
        with open("data/sample_set_search_compare.json") as f:
            compare_to = json.load(f)
        self._compare_samples(ret, compare_to)

    @unittest.skip("only particular users have permission to search")
    # skipped because only particular users have permission to search
    def test_query_search(self):
        ret = self.serviceImpl.sample_set_to_samples_info(
            self.ctx,
            {"ref": self.sample_set_ref, "start": 0, "limit": 10, "query": "Georgia"},
        )[0]
        with open("data/sample_set_search_compare.json") as f:
            compare_to = json.load(f)
        # get the samples with state_province 'Georgia' only
        compare_to["samples"] = [
            s
            for s in compare_to["samples"]
            if s.get("state_province") and s["state_province"][0] == "Georgia"
        ]
        compare_to["num_found"] = len(compare_to["samples"])
        self._compare_samples(ret, compare_to)

    @unittest.skip("only particular users have permission to search")
    # skipped because only particular users have permission to search
    def test_prefix_query_search(self):
        ret = self.serviceImpl.sample_set_to_samples_info(
            self.ctx, {"ref": self.sample_set_ref, "query": "Germa"}
        )[0]
        with open("data/sample_set_search_compare.json") as f:
            compare_to = json.load(f)
        # get the samples with country 'Germany' only
        compare_to["samples"] = [
            s
            for s in compare_to["samples"]
            if s.get("country") and s["country"][0] == "Germany"
        ]
        compare_to["num_found"] = len(compare_to["samples"])
        self._compare_samples(ret, compare_to)

    @unittest.skip("only particular users have permission to search")
    # skipped because only particular users have permission to search
    def test_prefix_query_search_2(self):
        ret = self.serviceImpl.sample_set_to_samples_info(
            self.ctx, {"ref": self.sample_set_ref, "query": "Ge"}
        )[0]
        with open("data/sample_set_search_compare.json") as f:
            compare_to = json.load(f)
        # get the samples with country 'Germany' only
        compare_to["samples"] = [
            s
            for s in compare_to["samples"]
            if (s.get("country") and s["country"][0] == "Germany")
            or (s.get("state_province") and s["state_province"][0] == "Georgia")
        ]
        compare_to["num_found"] = len(compare_to["samples"])
        self._compare_samples(ret, compare_to)
