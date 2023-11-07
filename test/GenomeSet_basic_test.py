# -*- coding: utf-8 -*-
import unittest
from pprint import pprint
from test.base_class import BaseTestClass
from test.conftest import INFO_LENGTH
from test.util import make_genome_refs


N_GENOME_REFS = 2

class GenomeSetAPITest(BaseTestClass):
    @classmethod
    def prepare_data(cls: BaseTestClass) -> None:
        """Set up fixtures for the class.

        :param cls: class object
        :type cls: BaseTestClass
        """
        cls.genome_refs = make_genome_refs(cls.foft, cls.ws_name)

    def test_basic_save_and_get(self):
        setObjName = "set_of_genomes"

        # create the set object
        set_data = {
            "description": "my first genome set",
            "items": [
                {"ref": self.genome_refs[0], "label": "genome1"},
                {"ref": self.genome_refs[1], "label": "genome2"},
            ],
        }

        # test a save
        res = self.set_api_client.save_genome_set_v1(
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
        assert res["set_info"][10]["item_count"] == str(N_GENOME_REFS)

        # test get of that object
        d1 = self.set_api_client.get_genome_set_v1(
            self.ctx, {"ref": self.ws_name + "/" + setObjName}
        )[0]
        assert "data" in d1
        assert "info" in d1
        assert len(d1["info"]) == INFO_LENGTH
        assert "item_count" in d1["info"][10]
        assert d1["info"][10]["item_count"] == str(N_GENOME_REFS)

        assert d1["data"]["description"] == "my first genome set"
        assert len(d1["data"]["items"]) == N_GENOME_REFS

        item2 = d1["data"]["items"][1]
        assert "info" not in item2
        assert "ref" in item2
        assert "label" in item2
        assert item2["label"] == "genome2"
        assert item2["ref"] == self.genome_refs[1]

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
        assert d2["info"][10]["item_count"] == str(N_GENOME_REFS)

        assert d2["data"]["description"] == "my first genome set"
        assert len(d2["data"]["items"]) == N_GENOME_REFS

        item2 = d2["data"]["items"][1]
        assert "info" in item2
        assert len(item2["info"]), INFO_LENGTH
        assert "ref" in item2
        assert item2["ref"] == self.genome_refs[1]

        assert "ref_path" in item2
        assert item2["ref_path"] == res["set_ref"] + ";" + item2["ref"]
        pprint(d2)

    def test_save_and_get_kbasesearch_genome(self):
        setObjName = "set_of_kbasesearch_genomes"

        # create the set object
        set_data = {
            "description": "my kbasesearch genome set",
            "elements": {
                self.genome_refs[0]: {
                    "ref": self.genome_refs[0],
                    "metadata": {"test_metadata": "metadata"},
                },
                self.genome_refs[1]: {
                    "ref": self.genome_refs[1],
                    "metadata": {"test_metadata": "metadata"},
                },
            },
        }

        # test a save
        res = self.set_api_client.save_genome_set_v1(
            self.ctx,
            {
                "data": set_data,
                "output_object_name": setObjName,
                "workspace": self.ws_name,
                "save_search_set": True,
            },
        )[0]

        assert "set_ref" in res
        assert "set_info" in res
        assert len(res["set_info"]) == INFO_LENGTH

        assert res["set_info"][1] == setObjName
        assert "KBaseSearch.GenomeSet" in res["set_info"][2]

        # test get of that object
        d1 = self.set_api_client.get_genome_set_v1(
            self.ctx, {"ref": self.ws_name + "/" + setObjName}
        )[0]
        assert "data" in d1
        assert "info" in d1
        assert len(d1["info"]) == INFO_LENGTH
        assert "KBaseSearch.GenomeSet" in res["set_info"][2]

        assert d1["data"]["description"] == "my kbasesearch genome set"
        assert len(d1["data"]["elements"]) == N_GENOME_REFS

        elements = d1["data"]["elements"]
        assert self.genome_refs[0] in elements
        assert self.genome_refs[1] in elements

        genome_2 = elements.get(self.genome_refs[1])
        assert "ref" in genome_2
        assert genome_2.get("ref") == self.genome_refs[1]
        assert genome_2["metadata"]["test_metadata"] == "metadata"

    # NOTE: Comment the following line to run the test
    # @unittest.skip("skipped test_save_and_get_of_empty_set")
    def test_save_and_get_of_emtpy_set(self):
        setObjName = "nada_set"

        # create the set object
        set_data = {"description": "nothing to see here", "items": []}
        # test a save
        res = self.set_api_client.save_genome_set_v1(
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
        d1 = self.set_api_client.get_genome_set_v1(
            self.ctx, {"ref": self.ws_name + "/" + setObjName}
        )[0]
        assert "data" in d1
        assert "info" in d1
        assert len(d1["info"]) == INFO_LENGTH
        assert "item_count" in d1["info"][10]
        assert d1["info"][10]["item_count"] == "0"

        assert d1["data"]["description"] == "nothing to see here"
        assert len(d1["data"]["items"]) == 0

        d2 = self.set_api_client.get_genome_set_v1(
            self.ctx, {"ref": res["set_ref"], "include_item_info": 1}
        )[0]

        assert "data" in d2
        assert "info" in d2
        assert len(d2["info"]) == INFO_LENGTH
        assert "item_count" in d2["info"][10]
        assert d2["info"][10]["item_count"] == "0"

        assert d2["data"]["description"] == "nothing to see here"
        assert len(d2["data"]["items"]) == 0
