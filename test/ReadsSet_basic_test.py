# -*- coding: utf-8 -*-
import os
import time
import unittest
from pprint import pprint
from test.conftest import INFO_LENGTH, WS_NAME, test_config
from test.util import make_fake_sampleset

import pytest
from installed_clients.FakeObjectsForTestsClient import FakeObjectsForTests


class SetAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        props = test_config()
        for prop in ["cfg", "ctx", "serviceImpl", "wsClient", "wsName", "wsURL"]:
            setattr(cls, prop, props[prop])

        foft = FakeObjectsForTests(os.environ["SDK_CALLBACK_URL"])
        [info1, info2, info3] = foft.create_fake_reads(
            {"ws_name": WS_NAME, "obj_names": ["reads1", "reads2", "reads3"]}
        )
        cls.read1ref = str(info1[6]) + "/" + str(info1[0]) + "/" + str(info1[4])
        cls.read2ref = str(info2[6]) + "/" + str(info2[0]) + "/" + str(info2[4])
        cls.read3ref = str(info3[6]) + "/" + str(info3[0]) + "/" + str(info3[4])

        cls.fake_sampleset_ref = make_fake_sampleset(
            "test_sampleset",
            [cls.read1ref, cls.read2ref, cls.read3ref],
            ["wt", "cond1", "cond2"],
            WS_NAME,
            cls.wsClient,
        )

    def getWsClient(self):
        return self.__class__.wsClient

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    # NOTE: According to Python unittest naming rules test method names should start from 'test'.
    def test_basic_save_and_get(self):
        workspace = WS_NAME
        setObjName = "set_o_reads"

        # create the set object
        set_data = {
            "description": "my first reads",
            "items": [
                {"ref": self.read1ref, "label": "reads1"},
                {"ref": self.read2ref, "label": "reads2"},
                {"ref": self.read3ref},
            ],
        }

        # test a save
        setAPI = self.getImpl()
        res = setAPI.save_reads_set_v1(
            self.getContext(),
            {
                "data": set_data,
                "output_object_name": setObjName,
                "workspace": workspace,
            },
        )[0]
        assert "set_ref" in res
        assert "set_info" in res
        assert len(res["set_info"]) == INFO_LENGTH

        assert res["set_info"][1] == setObjName
        assert "item_count" in res["set_info"][10]
        assert res["set_info"][10]["item_count"] == "3"

        # test get of that object
        d1 = setAPI.get_reads_set_v1(
            self.getContext(), {"ref": workspace + "/" + setObjName}
        )[0]
        assert "data" in d1
        assert "info" in d1
        assert len(d1["info"]) == INFO_LENGTH
        assert "item_count" in d1["info"][10]
        assert d1["info"][10]["item_count"] == "3"

        assert d1["data"]["description"] == "my first reads"
        assert len(d1["data"]["items"]) == 3

        item2 = d1["data"]["items"][1]
        assert "info" not in item2
        assert "ref" in item2
        assert "label" in item2
        assert item2["label"] == "reads2"
        assert item2["ref"] == self.read2ref

        item3 = d1["data"]["items"][2]
        assert "info" not in item3
        assert "ref" in item3
        assert "label" in item3
        assert item3["label"] == ""
        assert item3["ref"] == self.read3ref

        # test the call to make sure we get info for each item
        d2 = setAPI.get_reads_set_v1(
            self.getContext(),
            {
                "ref": res["set_ref"],
                "include_item_info": 1,
                "include_set_item_ref_paths": 1,
            },
        )[0]
        assert "data" in d2
        assert "info" in d2
        assert len(d2["info"]) == INFO_LENGTH
        assert "item_count" in d2["info"][10]
        assert d2["info"][10]["item_count"] == "3"

        assert d2["data"]["description"] == "my first reads"
        assert len(d2["data"]["items"]) == 3

        item2 = d2["data"]["items"][1]
        assert "info" in item2
        assert len(item2["info"]), INFO_LENGTH
        assert "ref" in item2
        assert item2["ref"] == self.read2ref

        assert "ref_path" in item2
        assert item2["ref_path"] == res["set_ref"] + ";" + item2["ref"]
        pprint(d2)

    # NOTE: Comment the following line to run the test
    @unittest.skip("skipped test_save_and_get_of_emtpy_set")
    def test_save_and_get_of_empty_set(self):
        workspace = WS_NAME
        setObjName = "nada_set"

        # create the set object
        set_data = {"description": "nothing to see here", "items": []}

        # test a save
        setAPI = self.getImpl()
        res = setAPI.save_reads_set_v1(
            self.getContext(),
            {
                "data": set_data,
                "output_object_name": setObjName,
                "workspace": workspace,
            },
        )[0]
        assert "set_ref" in res
        assert "set_info" in res
        assert len(res["set_info"]) == INFO_LENGTH

        assert res["set_info"][1] == setObjName
        assert "item_count" in res["set_info"][10]
        assert res["set_info"][10]["item_count"] == "0"

        # test get of that object
        d1 = setAPI.get_reads_set_v1(
            self.getContext(), {"ref": workspace + "/" + setObjName}
        )[0]
        assert "data" in d1
        assert "info" in d1
        assert len(d1["info"]) == INFO_LENGTH
        assert "item_count" in d1["info"][10]
        assert d1["info"][10]["item_count"] == "0"

        assert d1["data"]["description"] == "nothing to see here"
        assert len(d1["data"]["items"]) == 0

        d2 = setAPI.get_reads_set_v1(
            self.getContext(), {"ref": res["set_ref"], "include_item_info": 1}
        )[0]

        assert "data" in d2
        assert "info" in d2
        assert len(d2["info"]) == INFO_LENGTH
        assert "item_count" in d2["info"][10]
        assert d2["info"][10]["item_count"] == "0"

        assert d2["data"]["description"] == "nothing to see here"
        assert len(d2["data"]["items"]) == 0

    def test_get_sampleset_as_readsset(self):
        param_set = [
            {"ref": self.fake_sampleset_ref},
            {"ref": self.fake_sampleset_ref, "include_item_info": 0},
            {"ref": self.fake_sampleset_ref, "include_item_info": 1},
        ]
        for params in param_set:
            res = self.getImpl().get_reads_set_v1(self.getContext(), params)[0]
            assert "data" in res
            assert "items" in res["data"]
            assert "info" in res
            assert len(res["info"]) == INFO_LENGTH
            assert "item_count" in res["info"][10]
            assert res["info"][10]["item_count"] == 3
            for item in res["data"]["items"]:
                assert "ref" in item
                if params.get("include_item_info", 0) == 1:
                    assert "info" in item
                    assert len(item["info"]) == INFO_LENGTH
                else:
                    assert "info" not in item

    def test_get_reads_set_bad_ref(self):
        with pytest.raises(
            ValueError, match='"ref" parameter must be a valid workspace reference'
        ):
            self.getImpl().get_reads_set_v1(self.getContext(), {"ref": "not_a_ref"})

    def test_get_reads_set_bad_type(self):
        with pytest.raises(ValueError, match="is invalid for get_reads_set_v1"):
            self.getImpl().get_reads_set_v1(self.getContext(), {"ref": self.read1ref})
