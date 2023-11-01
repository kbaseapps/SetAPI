# -*- coding: utf-8 -*-
import unittest
from pprint import pprint
from test.base_class import BaseTestClass
from test.conftest import INFO_LENGTH
from test.util import make_reads_refs
import pytest


N_READS = 3

class SetAPITest(BaseTestClass):
@classmethod
def prepare_data(cls: BaseTestClass) -> None:
    """Set up fixtures for the class.

    :param cls: class object
    :type cls: BaseTestClass
    """
    cls.reads_refs = make_reads_refs(cls.foft, cls.ws_name)

    # conditions
    cls.conditions = ["WT", "Cond1", "HY"]

    # create a conditition set
    workspace_id = cls.dfu.ws_name_to_id(cls.ws_name)
    condition_set_object_name = "test_Condition_Set"
    condition_set_data = {
        "conditions": {
            cls.conditions[0]: ["0", "0"],
            cls.conditions[1]: ["0", "0"],
            cls.conditions[2]: ["0", "0"],
        },
        "factors": [
            {
                "factor": "Time series design",
                "factor_ont_id": "Custom:Term",
                "factor_ont_ref": "KbaseOntologies/Custom",
                "unit": "Hour",
                "unit_ont_id": "Custom:Unit",
                "unit_ont_ref": "KbaseOntologies/Custom",
            },
            {
                "factor": "Treatment with Sirolimus",
                "factor_ont_id": "Custom:Term",
                "factor_ont_ref": "KbaseOntologies/Custom",
                "unit": "nanogram per milliliter",
                "unit_ont_id": "Custom:Unit",
                "unit_ont_ref": "KbaseOntologies/Custom",
            },
        ],
        "ontology_mapping_method": "User Curation",
    }
    save_object_params = {
        "id": workspace_id,
        "objects": [
            {
                "type": "KBaseExperiments.ConditionSet",
                "data": condition_set_data,
                "name": condition_set_object_name,
            }
        ],
    }

    dfu_oi = cls.dfu.save_objects(save_object_params)[0]
    cls.condition_set_ref = (
        str(dfu_oi[6]) + "/" + str(dfu_oi[0]) + "/" + str(dfu_oi[4])
    )

def test_basic_save_and_get(self):
    setObjName = "micromonas_rnaseq_test1_sampleset"

    # create the set object
    create_ss_params = {
        "ws_id": self.ws_name,
        "sampleset_id": setObjName,
        "sampleset_desc": "first pass at testing algae GFFs from NCBI",
        "domain": "euk",
        "platform": "Illumina",
        "sample_n_conditions": [
            {"sample_id": [self.reads_refs[0]], "condition": self.conditions[0]},
            {
                "sample_id": [self.reads_refs[1], self.reads_refs[2]],
                "condition": self.conditions[1],
            },
        ],
        "source": "NCBI",
        "Library_type": "SingleEnd",
        "publication_id": "none",
        "string external_source_date": "not sure",
    }

    # test a save
    res = self.set_api_client.create_sample_set(self.ctx, create_ss_params)[0]

    print("======  Returned val from create_sample_set  ======")
    pprint(res)

    assert "set_ref" in res
    assert "set_info" in res
    assert len(res["set_info"]) == INFO_LENGTH

    assert res["set_info"][1] == setObjName
    assert "num_samples" in res["set_info"][10]
    assert res["set_info"][10]["num_samples"] == str(N_READS)

    # test get of that object
    d1 = self.set_api_client.get_reads_set_v1(self.ctx, {"ref": self.ws_name + "/" + setObjName})[
        0
    ]
    assert "data" in d1
    assert "info" in d1
    assert len(d1["info"]) == INFO_LENGTH
    assert "item_count" in d1["info"][10]
    assert d1["info"][10]["item_count"] == N_READS

    assert d1["data"]["description"] == "first pass at testing algae GFFs from NCBI"
    assert len(d1["data"]["items"]) == N_READS

    item2 = d1["data"]["items"][1]
    assert "info" not in item2
    assert "ref" in item2
    assert "label" in item2
    assert item2["label"] == self.conditions[1]
    assert item2["ref"] == self.reads_refs[1]

    item3 = d1["data"]["items"][2]
    assert "info" not in item3
    assert "ref" in item3
    assert "label" in item3
    assert item3["label"] == self.conditions[1]
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
    assert d2["info"][10]["item_count"] == N_READS

    assert d2["data"]["description"] == "first pass at testing algae GFFs from NCBI"
    assert len(d2["data"]["items"]) == N_READS

    item2 = d2["data"]["items"][1]
    assert "info" in item2
    assert len(item2["info"]), INFO_LENGTH
    assert "ref" in item2
    assert item2["ref"] == self.reads_refs[1]

    assert "ref_path" in item2
    assert item2["ref_path"] == res["set_ref"] + ";" + item2["ref"]

    pprint(d2)

def test_basic_save_and_get_condition_in_list(self):
    setObjName = "micromonas_rnaseq_test1_sampleset"

    # create the set object
    create_ss_params = {
        "ws_id": self.ws_name,
        "sampleset_id": setObjName,
        "sampleset_desc": "first pass at testing algae GFFs from NCBI",
        "domain": "euk",
        "platform": "Illumina",
        "sample_n_conditions": [
            {"sample_id": [self.reads_refs[0]], "condition": [self.conditions[0]]},
            {
                "sample_id": [self.reads_refs[1], self.reads_refs[2]],
                "condition": [self.conditions[1]],
            },
        ],
        "source": "NCBI",
        "Library_type": "SingleEnd",
        "publication_id": "none",
        "string external_source_date": "not sure",
    }

    # test a save
    res = self.set_api_client.create_sample_set(self.ctx, create_ss_params)[0]

    print("======  Returned val from create_sample_set  ======")
    pprint(res)

    assert "set_ref" in res
    assert "set_info" in res
    assert len(res["set_info"]) == INFO_LENGTH

    assert res["set_info"][1] == setObjName
    assert "num_samples" in res["set_info"][10]
    assert res["set_info"][10]["num_samples"] == str(N_READS)

    # test get of that object
    d1 = self.set_api_client.get_reads_set_v1(self.ctx, {"ref": self.ws_name + "/" + setObjName})[
        0
    ]
    assert "data" in d1
    assert "info" in d1
    assert len(d1["info"]) == INFO_LENGTH
    assert "item_count" in d1["info"][10]
    assert d1["info"][10]["item_count"] == N_READS

    assert d1["data"]["description"] == "first pass at testing algae GFFs from NCBI"
    assert len(d1["data"]["items"]) == N_READS

    item2 = d1["data"]["items"][1]
    assert "info" not in item2
    assert "ref" in item2
    assert "label" in item2
    assert item2["label"] == self.conditions[1]
    assert item2["ref"] == self.reads_refs[1]

    item3 = d1["data"]["items"][2]
    assert "info" not in item3
    assert "ref" in item3
    assert "label" in item3
    assert item3["label"] == self.conditions[1]
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
    assert d2["info"][10]["item_count"] == N_READS

    assert d2["data"]["description"] == "first pass at testing algae GFFs from NCBI"
    assert len(d2["data"]["items"]) == N_READS

    item2 = d2["data"]["items"][1]
    assert "info" in item2
    assert len(item2["info"]), INFO_LENGTH
    assert "ref" in item2
    assert item2["ref"] == self.reads_refs[1]

    assert "ref_path" in item2
    assert item2["ref_path"] == res["set_ref"] + ";" + item2["ref"]

    pprint(d2)

@unittest.skip("conditionset_ref not supported")
def test_unmatched_conditions(self):
    setObjName = "micromonas_rnaseq_test1_sampleset"

    unmatching_condition = "unmatching_condition"
    # create the set object with unmatching conditions
    create_ss_params = {
        "ws_id": self.ws_name,
        "sampleset_id": setObjName,
        "sampleset_desc": "first pass at testing algae GFFs from NCBI",
        "domain": "euk",
        "platform": "Illumina",
        "sample_n_conditions": [
            {"sample_id": [self.reads_refs[0]], "condition": unmatching_condition},
            {
                "sample_id": [self.reads_refs[1], self.reads_refs[2]],
                "condition": self.conditions[1],
            },
        ],
        "source": "NCBI",
        "Library_type": "SingleEnd",
        "publication_id": "none",
        "string external_source_date": "not sure",
        "conditionset_ref": self.condition_set_ref,
    }

    # test a save
    with pytest.raises(ValueError, match="ERROR: Given conditions"):
        self.set_api_client.create_sample_set(self.ctx, create_ss_params)

def test_non_list_string_conditions(self):
    setObjName = "micromonas_rnaseq_test1_sampleset"

    digital_condition = 10
    # create the set object with unmatching conditions
    create_ss_params = {
        "ws_id": self.ws_name,
        "sampleset_id": setObjName,
        "sampleset_desc": "first pass at testing algae GFFs from NCBI",
        "domain": "euk",
        "platform": "Illumina",
        "sample_n_conditions": [
            {"sample_id": [self.reads_refs[0]], "condition": digital_condition}
        ],
        "source": "NCBI",
        "Library_type": "SingleEnd",
        "publication_id": "none",
        "string external_source_date": "not sure",
    }

    # test a save
    with pytest.raises(
        ValueError, match="ERROR: condition should be either a list or a string"
    ):
        self.set_api_client.create_sample_set(self.ctx, create_ss_params)
