# -*- coding: utf-8 -*-
import os
import shutil
from pprint import pprint
from test import TEST_BASE_DIR
from test.base_class import BaseTestClass
from test.conftest import INFO_LENGTH


N_ASSEMBLIES = 2

class AssemblySetAPITest(BaseTestClass):
@classmethod
def prepare_data(cls: BaseTestClass) -> None:
    """Set up fixtures for the class.

    :param cls: class object
    :type cls: BaseTestClass
    """
    # copy test file to scratch area
    fna_filename = "seq.fna"
    fna_path = os.path.join(cls.config["scratch"], fna_filename)
    shutil.copy(os.path.join(TEST_BASE_DIR, "data", fna_filename), fna_path)

    cls.assembly1ref = cls.au.save_assembly_from_fasta(
        {
            "file": {"path": fna_path},
            "workspace_name": cls.ws_name,
            "assembly_name": "assembly_obj_1",
        }
    )
    cls.assembly2ref = cls.au.save_assembly_from_fasta(
        {
            "file": {"path": fna_path},
            "workspace_name": cls.ws_name,
            "assembly_name": "assembly_obj_2",
        }
    )

def test_basic_save_and_get(self):
    setObjName = "set_of_assemblies"

    # create the set object
    set_data = {
        "description": "my first assembly set",
        "items": [
            {"ref": self.assembly1ref, "label": "assembly1"},
            {"ref": self.assembly2ref, "label": "assembly2"},
        ],
    }

    # test a save
    res = self.set_api_client.save_assembly_set_v1(
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
    assert res["set_info"][10]["item_count"] == str(N_ASSEMBLIES)

    # test get of that object
    d1 = self.set_api_client.get_assembly_set_v1(
        self.ctx, {"ref": self.ws_name + "/" + setObjName}
    )[0]
    assert "data" in d1
    assert "info" in d1
    assert len(d1["info"]) == INFO_LENGTH
    assert "item_count" in d1["info"][10]
    assert d1["info"][10]["item_count"] == str(N_ASSEMBLIES)

    assert d1["data"]["description"] == "my first assembly set"
    assert len(d1["data"]["items"]) == N_ASSEMBLIES

    item2 = d1["data"]["items"][1]
    assert "info" not in item2
    assert "ref_path" not in item2
    assert "ref" in item2
    assert "label" in item2
    assert item2["label"] == "assembly2"
    assert item2["ref"] == self.assembly2ref

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
    assert d2["info"][10]["item_count"] == str(N_ASSEMBLIES)

    assert d2["data"]["description"] == "my first assembly set"
    assert len(d2["data"]["items"]) == N_ASSEMBLIES

    item2 = d2["data"]["items"][1]
    assert "info" in item2
    assert len(item2["info"]), INFO_LENGTH
    assert "ref" in item2
    assert item2["ref"] == self.assembly2ref

    assert "ref_path" in item2
    assert item2["ref_path"] == res["set_ref"] + ";" + item2["ref"]
    pprint(d2)

def test_save_and_get_of_empty_set(self):
    setObjName = "nada_set"

    # create the set object
    set_data = {"description": "nothing to see here", "items": []}
    # test a save
    res = self.set_api_client.save_assembly_set_v1(
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
    d1 = self.set_api_client.get_assembly_set_v1(
        self.ctx, {"ref": self.ws_name + "/" + setObjName}
    )[0]
    assert "data" in d1
    assert "info" in d1
    assert len(d1["info"]) == INFO_LENGTH
    assert "item_count" in d1["info"][10]
    assert d1["info"][10]["item_count"] == "0"

    assert d1["data"]["description"] == "nothing to see here"
    assert len(d1["data"]["items"]) == 0

    d2 = self.set_api_client.get_assembly_set_v1(
        self.ctx, {"ref": res["set_ref"], "include_item_info": 1}
    )[0]

    assert "data" in d2
    assert "info" in d2
    assert len(d2["info"]) == INFO_LENGTH
    assert "item_count" in d2["info"][10]
    assert d2["info"][10]["item_count"] == "0"

    assert d2["data"]["description"] == "nothing to see here"
    assert len(d2["data"]["items"]) == 0
