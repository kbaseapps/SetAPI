# -*- coding: utf-8 -*-
import os
import time
import unittest
from pprint import pprint
from test.conftest import INFO_LENGTH, WS_NAME, test_config

from installed_clients.FakeObjectsForTestsClient import FakeObjectsForTests


class SetAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        props = test_config()
        for prop in ["cfg", "ctx", "serviceImpl", "wsClient", "wsName", "wsURL"]:
            setattr(cls, prop, props[prop])

        foft = FakeObjectsForTests(os.environ["SDK_CALLBACK_URL"])
        [info1, info2] = foft.create_fake_genomes(
            {"ws_name": WS_NAME, "obj_names": ["genome_obj_1", "genome_obj_2"]}
        )
        cls.genome1ref = str(info1[6]) + "/" + str(info1[0]) + "/" + str(info1[4])
        cls.genome2ref = str(info2[6]) + "/" + str(info2[0]) + "/" + str(info2[4])

    def getWsClient(self):
        return self.__class__.wsClient

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    # NOTE: According to Python unittest naming rules test method names should start from 'test'.
    def test_basic_save_and_get(self):
        workspace = WS_NAME
        setObjName = "set_of_genomes"

        # create the set object
        set_data = {
            "description": "my first genome set",
            "items": [
                {"ref": self.genome1ref, "label": "genome1"},
                {"ref": self.genome2ref, "label": "genome2"},
            ],
        }

        # test a save
        setAPI = self.getImpl()
        res = setAPI.save_genome_set_v1(
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
        assert res["set_info"][10]["item_count"] == "2"

        # test get of that object
        d1 = setAPI.get_genome_set_v1(
            self.getContext(), {"ref": workspace + "/" + setObjName}
        )[0]
        assert "data" in d1
        assert "info" in d1
        assert len(d1["info"]) == INFO_LENGTH
        assert "item_count" in d1["info"][10]
        assert d1["info"][10]["item_count"] == "2"

        assert d1["data"]["description"] == "my first genome set"
        assert len(d1["data"]["items"]) == 2

        item2 = d1["data"]["items"][1]
        assert "info" not in item2
        assert "ref" in item2
        assert "label" in item2
        assert item2["label"] == "genome2"
        assert item2["ref"] == self.genome2ref

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
        assert d2["info"][10]["item_count"] == "2"

        assert d2["data"]["description"] == "my first genome set"
        assert len(d2["data"]["items"]) == 2

        item2 = d2["data"]["items"][1]
        assert "info" in item2
        assert len(item2["info"]), INFO_LENGTH
        assert "ref" in item2
        assert item2["ref"] == self.genome2ref

        assert "ref_path" in item2
        assert item2["ref_path"] == res["set_ref"] + ";" + item2["ref"]
        pprint(d2)

    def test_save_and_get_kbasesearch_genome(self):
        workspace = WS_NAME
        setObjName = "set_of_kbasesearch_genomes"

        # create the set object
        set_data = {
            "description": "my kbasesearch genome set",
            "elements": {
                self.genome1ref: {
                    "ref": self.genome1ref,
                    "metadata": {"test_metadata": "metadata"},
                },
                self.genome2ref: {
                    "ref": self.genome2ref,
                    "metadata": {"test_metadata": "metadata"},
                },
            },
        }

        # test a save
        setAPI = self.getImpl()
        res = setAPI.save_genome_set_v1(
            self.getContext(),
            {
                "data": set_data,
                "output_object_name": setObjName,
                "workspace": workspace,
                "save_search_set": True,
            },
        )[0]

        assert "set_ref" in res
        assert "set_info" in res
        assert len(res["set_info"]) == INFO_LENGTH

        assert res["set_info"][1] == setObjName
        assert "KBaseSearch.GenomeSet" in res["set_info"][2]

        # test get of that object
        d1 = setAPI.get_genome_set_v1(
            self.getContext(), {"ref": workspace + "/" + setObjName}
        )[0]
        assert "data" in d1
        assert "info" in d1
        assert len(d1["info"]) == INFO_LENGTH
        assert "KBaseSearch.GenomeSet" in res["set_info"][2]

        assert d1["data"]["description"] == "my kbasesearch genome set"
        assert len(d1["data"]["elements"]) == 2

        elements = d1["data"]["elements"]
        assert self.genome1ref in elements
        assert self.genome2ref in elements

        genome_2 = elements.get(self.genome2ref)
        assert "ref" in genome_2
        assert genome_2.get("ref") == self.genome2ref
        assert genome_2["metadata"]["test_metadata"] == "metadata"

    # NOTE: Comment the following line to run the test
    @unittest.skip("skipped test_save_and_get_of_emtpy_set")
    def test_save_and_get_of_emtpy_set(self):
        workspace = WS_NAME
        setObjName = "nada_set"

        # create the set object
        set_data = {"description": "nothing to see here", "items": []}
        # test a save
        setAPI = self.getImpl()
        res = setAPI.save_genome_set_v1(
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
        d1 = setAPI.get_genome_set_v1(
            self.getContext(), {"ref": workspace + "/" + setObjName}
        )[0]
        assert "data" in d1
        assert "info" in d1
        assert len(d1["info"]) == INFO_LENGTH
        assert "item_count" in d1["info"][10]
        assert d1["info"][10]["item_count"] == "0"

        assert d1["data"]["description"] == "nothing to see here"
        assert len(d1["data"]["items"]) == 0

        d2 = setAPI.get_genome_set_v1(
            self.getContext(), {"ref": res["set_ref"], "include_item_info": 1}
        )[0]

        assert "data" in d2
        assert "info" in d2
        assert len(d2["info"]) == INFO_LENGTH
        assert "item_count" in d2["info"][10]
        assert d2["info"][10]["item_count"] == "0"

        assert d2["data"]["description"] == "nothing to see here"
        assert len(d2["data"]["items"]) == 0
