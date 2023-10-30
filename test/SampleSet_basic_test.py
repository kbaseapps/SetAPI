# -*- coding: utf-8 -*-
import os
import time
import unittest
from pprint import pprint
from test.conftest import INFO_LENGTH, WS_NAME, test_config

import pytest
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.FakeObjectsForTestsClient import FakeObjectsForTests


class SetAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        props = test_config()
        for prop in ["cfg", "ctx", "serviceImpl", "wsClient", "wsName", "wsURL"]:
            setattr(cls, prop, props[prop])

        cls.dfu = DataFileUtil(os.environ["SDK_CALLBACK_URL"])
        foft = FakeObjectsForTests(os.environ["SDK_CALLBACK_URL"])
        [info1, info2, info3] = foft.create_fake_reads(
            {"ws_name": WS_NAME, "obj_names": ["reads1", "reads2", "reads3"]}
        )
        cls.read1ref = str(info1[6]) + "/" + str(info1[0]) + "/" + str(info1[4])
        cls.read2ref = str(info2[6]) + "/" + str(info2[0]) + "/" + str(info2[4])
        cls.read3ref = str(info3[6]) + "/" + str(info3[0]) + "/" + str(info3[4])

        cls.prepare_data()

    @classmethod
    def prepare_data(cls):
        # conditions
        cls.condition_1 = "WT"
        cls.condition_2 = "Cond1"
        cls.condition_3 = "HY"

        # create a conditition set
        workspace_id = cls.dfu.ws_name_to_id(WS_NAME)
        condition_set_object_name = "test_Condition_Set"
        condition_set_data = {
            "conditions": {
                cls.condition_1: ["0", "0"],
                cls.condition_2: ["0", "0"],
                cls.condition_3: ["0", "0"],
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

    def getWsClient(self):
        return self.__class__.wsClient

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    # NOTE: According to Python unittest naming rules test method names should start from 'test'.
    def test_basic_save_and_get(self):
        workspace = WS_NAME
        setObjName = "micromonas_rnaseq_test1_sampleset"

        # create the set object
        create_ss_params = {
            "ws_id": workspace,
            "sampleset_id": setObjName,
            "sampleset_desc": "first pass at testing algae GFFs from NCBI",
            "domain": "euk",
            "platform": "Illumina",
            "sample_n_conditions": [
                {"sample_id": [self.read1ref], "condition": self.condition_1},
                {
                    "sample_id": [self.read2ref, self.read3ref],
                    "condition": self.condition_2,
                },
            ],
            "source": "NCBI",
            "Library_type": "SingleEnd",
            "publication_id": "none",
            "string external_source_date": "not sure",
        }

        # test a save
        setAPI = self.getImpl()
        res = setAPI.create_sample_set(self.getContext(), create_ss_params)[0]

        print("======  Returned val from create_sample_set  ======")
        pprint(res)

        assert "set_ref" in res
        assert "set_info" in res
        assert len(res["set_info"]) == INFO_LENGTH

        assert res["set_info"][1] == setObjName
        assert "num_samples" in res["set_info"][10]
        assert res["set_info"][10]["num_samples"] == "3"

        # test get of that object
        d1 = setAPI.get_reads_set_v1(
            self.getContext(), {"ref": workspace + "/" + setObjName}
        )[0]
        assert "data" in d1
        assert "info" in d1
        assert len(d1["info"]) == INFO_LENGTH
        assert "item_count" in d1["info"][10]
        assert d1["info"][10]["item_count"] == 3

        assert d1["data"]["description"] == "first pass at testing algae GFFs from NCBI"
        assert len(d1["data"]["items"]) == 3

        item2 = d1["data"]["items"][1]
        assert "info" not in item2
        assert "ref" in item2
        assert "label" in item2
        assert item2["label"] == self.condition_2
        assert item2["ref"] == self.read2ref

        item3 = d1["data"]["items"][2]
        assert "info" not in item3
        assert "ref" in item3
        assert "label" in item3
        assert item3["label"] == self.condition_2
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
        assert d2["info"][10]["item_count"] == 3

        assert d2["data"]["description"] == "first pass at testing algae GFFs from NCBI"
        assert len(d2["data"]["items"]) == 3

        item2 = d2["data"]["items"][1]
        assert "info" in item2
        assert len(item2["info"]), INFO_LENGTH
        assert "ref" in item2
        assert item2["ref"] == self.read2ref

        assert "ref_path" in item2
        assert item2["ref_path"] == res["set_ref"] + ";" + item2["ref"]

        pprint(d2)

    def test_basic_save_and_get_condition_in_list(self):
        workspace = WS_NAME
        setObjName = "micromonas_rnaseq_test1_sampleset"

        # create the set object
        create_ss_params = {
            "ws_id": workspace,
            "sampleset_id": setObjName,
            "sampleset_desc": "first pass at testing algae GFFs from NCBI",
            "domain": "euk",
            "platform": "Illumina",
            "sample_n_conditions": [
                {"sample_id": [self.read1ref], "condition": [self.condition_1]},
                {
                    "sample_id": [self.read2ref, self.read3ref],
                    "condition": [self.condition_2],
                },
            ],
            "source": "NCBI",
            "Library_type": "SingleEnd",
            "publication_id": "none",
            "string external_source_date": "not sure",
        }

        # test a save
        setAPI = self.getImpl()
        res = setAPI.create_sample_set(self.getContext(), create_ss_params)[0]

        print("======  Returned val from create_sample_set  ======")
        pprint(res)

        assert "set_ref" in res
        assert "set_info" in res
        assert len(res["set_info"]) == INFO_LENGTH

        assert res["set_info"][1] == setObjName
        assert "num_samples" in res["set_info"][10]
        assert res["set_info"][10]["num_samples"] == "3"

        # test get of that object
        d1 = setAPI.get_reads_set_v1(
            self.getContext(), {"ref": workspace + "/" + setObjName}
        )[0]
        assert "data" in d1
        assert "info" in d1
        assert len(d1["info"]) == INFO_LENGTH
        assert "item_count" in d1["info"][10]
        assert d1["info"][10]["item_count"] == 3

        assert d1["data"]["description"] == "first pass at testing algae GFFs from NCBI"
        assert len(d1["data"]["items"]) == 3

        item2 = d1["data"]["items"][1]
        assert "info" not in item2
        assert "ref" in item2
        assert "label" in item2
        assert item2["label"] == self.condition_2
        assert item2["ref"] == self.read2ref

        item3 = d1["data"]["items"][2]
        assert "info" not in item3
        assert "ref" in item3
        assert "label" in item3
        assert item3["label"] == self.condition_2
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
        assert d2["info"][10]["item_count"] == 3

        assert d2["data"]["description"] == "first pass at testing algae GFFs from NCBI"
        assert len(d2["data"]["items"]) == 3

        item2 = d2["data"]["items"][1]
        assert "info" in item2
        assert len(item2["info"]), INFO_LENGTH
        assert "ref" in item2
        assert item2["ref"] == self.read2ref

        assert "ref_path" in item2
        assert item2["ref_path"] == res["set_ref"] + ";" + item2["ref"]

        pprint(d2)

    @unittest.skip("conditionset_ref not supported")
    def test_unmatched_conditions(self):
        workspace = WS_NAME
        setObjName = "micromonas_rnaseq_test1_sampleset"

        unmatching_condition = "unmatching_condition"
        # create the set object with unmatching conditions
        create_ss_params = {
            "ws_id": workspace,
            "sampleset_id": setObjName,
            "sampleset_desc": "first pass at testing algae GFFs from NCBI",
            "domain": "euk",
            "platform": "Illumina",
            "sample_n_conditions": [
                {"sample_id": [self.read1ref], "condition": unmatching_condition},
                {
                    "sample_id": [self.read2ref, self.read3ref],
                    "condition": self.condition_2,
                },
            ],
            "source": "NCBI",
            "Library_type": "SingleEnd",
            "publication_id": "none",
            "string external_source_date": "not sure",
            "conditionset_ref": self.condition_set_ref,
        }

        # test a save
        setAPI = self.getImpl()

        with pytest.raises(ValueError, match="ERROR: Given conditions"):
            setAPI.create_sample_set(self.getContext(), create_ss_params)

    def test_non_list_string_conditions(self):
        workspace = WS_NAME
        setObjName = "micromonas_rnaseq_test1_sampleset"

        digital_condition = 10
        # create the set object with unmatching conditions
        create_ss_params = {
            "ws_id": workspace,
            "sampleset_id": setObjName,
            "sampleset_desc": "first pass at testing algae GFFs from NCBI",
            "domain": "euk",
            "platform": "Illumina",
            "sample_n_conditions": [
                {"sample_id": [self.read1ref], "condition": digital_condition}
            ],
            "source": "NCBI",
            "Library_type": "SingleEnd",
            "publication_id": "none",
            "string external_source_date": "not sure",
        }

        # test a save
        setAPI = self.getImpl()

        with pytest.raises(
            ValueError, match="ERROR: condition should be either a list or a string"
        ):
            setAPI.create_sample_set(self.getContext(), create_ss_params)
