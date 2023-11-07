# -*- coding: utf-8 -*-
import unittest
from pprint import pprint
from test.base_class import BaseTestClass
from test.conftest import INFO_LENGTH
from test.util import make_fake_sampleset, make_reads_refs

import pytest


class SetAPITest(BaseTestClass):
@classmethod
def prepare_data(cls: BaseTestClass) -> None:
    """Set up fixtures for the class.

    :param cls: class object
    :type cls: BaseTestClass
    """
    cls.reads_refs = make_reads_refs(cls.foft, cls.ws_name)

    cls.fake_sampleset_ref = make_fake_sampleset(
        "test_sampleset",
        cls.reads_refs,
        ["wt", "cond1", "cond2"],
        cls.ws_name,
        cls.ws_client,
    )

def test_basic_save_and_get(self):
    setObjName = "set_o_reads"

    # create the set object
    set_data = {
        "description": "my first reads",
        "items": [
            {"ref": self.reads_refs[0], "label": "reads1"},
            {"ref": self.reads_refs[1], "label": "reads2"},
            {"ref": self.reads_refs[2]},
        ],
    }

    # test a save
    res = self.set_api_client.save_reads_set_v1(
        self.ctx,
        {
            "data": set_data,
            "output_object_name": setObjName,
            "workspace": self.ws_name,
        },
    )[0]
    assert "set_ref" in res
    assert "set_info" in res
    assert len(res["set_info"]) == INFO_LENGTH

    assert res["set_info"][1] == setObjName
    assert "item_count" in res["set_info"][10]
    assert res["set_info"][10]["item_count"] == "3"

    # test get of that object
    d1 = self.set_api_client.get_reads_set_v1(self.ctx, {"ref": self.ws_name + "/" + setObjName})[
        0
    ]
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
    assert item2["ref"] == self.reads_refs[1]

    item3 = d1["data"]["items"][2]
    assert "info" not in item3
    assert "ref" in item3
    assert "label" in item3
    assert item3["label"] == ""
    assert item3["ref"] == self.reads_refs[2]

    # test the call to make sure we get info for each item
    d2 = self.set_api_client.get_reads_set_v1(
        self.ctx,
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
    assert item2["ref"] == self.reads_refs[1]

    assert "ref_path" in item2
    assert item2["ref_path"] == res["set_ref"] + ";" + item2["ref"]
    pprint(d2)

# NOTE: Comment the following line to run the test
@unittest.skip("skipped test_save_and_get_of_emtpy_set")
def test_save_and_get_of_empty_set(self):
    setObjName = "nada_set"

    # create the set object
    set_data = {"description": "nothing to see here", "items": []}

    # test a save
    res = self.set_api_client.save_reads_set_v1(
        self.ctx,
        {
            "data": set_data,
            "output_object_name": setObjName,
            "workspace": self.ws_name,
        },
    )[0]
    assert "set_ref" in res
    assert "set_info" in res
    assert len(res["set_info"]) == INFO_LENGTH

    assert res["set_info"][1] == setObjName
    assert "item_count" in res["set_info"][10]
    assert res["set_info"][10]["item_count"] == "0"

    # test get of that object
    d1 = self.set_api_client.get_reads_set_v1(self.ctx, {"ref": self.ws_name + "/" + setObjName})[
        0
    ]
    assert "data" in d1
    assert "info" in d1
    assert len(d1["info"]) == INFO_LENGTH
    assert "item_count" in d1["info"][10]
    assert d1["info"][10]["item_count"] == "0"

    assert d1["data"]["description"] == "nothing to see here"
    assert len(d1["data"]["items"]) == 0

    d2 = self.set_api_client.get_reads_set_v1(
        self.ctx, {"ref": res["set_ref"], "include_item_info": 1}
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
        res = self.set_api_client.get_reads_set_v1(self.ctx, params)[0]
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
        self.set_api_client.get_reads_set_v1(self.ctx, {"ref": "not_a_ref"})

def test_get_reads_set_bad_type(self):
    with pytest.raises(ValueError, match="is invalid for get_reads_set_v1"):
        self.set_api_client.get_reads_set_v1(self.ctx, {"ref": self.reads_refs[0]})
