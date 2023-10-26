# -*- coding: utf-8 -*-
import os
import unittest
from test.test_config import get_test_config
import pytest

from installed_clients.FakeObjectsForTestsClient import FakeObjectsForTests
from test.util import info_to_ref, make_fake_feature_set


class FeatureSetSetAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        props = get_test_config()
        for prop in ["cfg", "ctx", "serviceImpl", "wsClient", "wsName", "wsURL"]:
            setattr(cls, prop, props[prop])

        foft = FakeObjectsForTests(os.environ["SDK_CALLBACK_URL"])

        # Make fake genomes
        [fake_genome, fake_genome2] = foft.create_fake_genomes(
            {"ws_name": cls.wsName, "obj_names": ["fake_genome", "fake_genome2"]}
        )
        cls.genome_refs = [info_to_ref(fake_genome), info_to_ref(fake_genome2)]

        # Make some fake feature sets
        cls.featureset_refs = [
            make_fake_feature_set(
                "feature_set_{}".format(i), cls.genome_refs[0], cls.wsName, cls.wsClient
            )
            for i in range(3)
        ]

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "wsName"):
            cls.wsClient.delete_workspace({"workspace": cls.wsName})
            print("Test workspace was deleted")

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        return self.__class__.wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def test_save_feature_set_set(self):
        set_name = "test_feature_set_set"
        set_items = list()
        for ref in self.featureset_refs:
            set_items.append({"label": "foo", "ref": ref})
        expression_set = {"description": "test_expressions", "items": set_items}
        result = self.getImpl().save_feature_set_set_v1(
            self.getContext(),
            {
                "workspace": self.getWsName(),
                "output_object_name": set_name,
                "data": expression_set,
            },
        )[0]
        assert result is not None
        assert "set_ref" in result
        assert "set_info" in result
        assert result["set_ref"] == info_to_ref(result["set_info"])
        assert result["set_info"][1] == set_name
        assert "KBaseSets.FeatureSetSet" in result["set_info"][2]

    def test_save_feature_set_set_no_data(self):
        with pytest.raises(
            ValueError, match='"data" parameter field required to save a FeatureSetSet'
        ):
            self.getImpl().save_feature_set_set_v1(
                self.getContext(),
                {
                    "workspace": self.getWsName(),
                    "output_object_name": "foo",
                    "data": None,
                },
            )

    @unittest.skip("Currently allow empty FeatureSetSets")
    def test_save_feature_set_set_empty(self):
        with pytest.raises(
            ValueError,
            match="At least one FeatureSet is required to save a FeatureSetSet.",
        ):
            self.getImpl().save_feature_set_set_v1(
                self.getContext(),
                {
                    "workspace": self.getWsName(),
                    "output_object_name": "foo",
                    "data": {"description": "empty_set", "items": []},
                },
            )

    def test_get_feature_set_set(self):
        set_name = "test_featureset_set2"
        set_items = list()
        for ref in self.featureset_refs:
            set_items.append({"label": "wt", "ref": ref})
        featureset_set = {"description": "test_alignments", "items": set_items}
        featureset_set_ref = self.getImpl().save_feature_set_set_v1(
            self.getContext(),
            {
                "workspace": self.getWsName(),
                "output_object_name": set_name,
                "data": featureset_set,
            },
        )[0]["set_ref"]

        fetched_set = self.getImpl().get_feature_set_set_v1(
            self.getContext(), {"ref": featureset_set_ref, "include_item_info": 0}
        )[0]
        assert fetched_set is not None
        assert "data" in fetched_set
        assert "info" in fetched_set
        assert len(fetched_set["data"]["items"]) == 3
        assert featureset_set_ref == info_to_ref(fetched_set["info"])
        for item in fetched_set["data"]["items"]:
            assert "info" not in item
            assert "ref_path" not in item
            assert "ref" in item
            assert "label" in item

        fetched_set_with_info = self.getImpl().get_feature_set_set_v1(
            self.getContext(),
            {
                "ref": featureset_set_ref,
                "include_item_info": 1,
                "include_set_item_ref_paths": 1,
            },
        )[0]
        assert fetched_set_with_info is not None
        assert "data" in fetched_set_with_info
        for item in fetched_set_with_info["data"]["items"]:
            assert "info" in item
            assert "ref" in item
            assert "label" in item
            assert "ref_path" in item
            assert item["ref_path"] == featureset_set_ref + ";" + item["ref"]

    def test_get_feature_set_set_bad_ref(self):
        with pytest.raises(
            ValueError, match='"ref" parameter must be a valid workspace reference'
        ):
            self.getImpl().get_feature_set_set_v1(
                self.getContext(), {"ref": "not_a_ref"}
            )

    def test_get_feature_set_set_bad_path(self):
        with pytest.raises(Exception):
            self.getImpl().get_feature_set_set_v1(
                self.getContext(), {"ref": "1/2/3", "path_to_set": ["foo", "bar"]}
            )

    def test_get_feature_set_set_no_ref(self):
        with pytest.raises(
            ValueError,
            match='"ref" parameter field specifiying the FeatureSet set is required',
        ):
            self.getImpl().get_feature_set_set_v1(self.getContext(), {"ref": None})
