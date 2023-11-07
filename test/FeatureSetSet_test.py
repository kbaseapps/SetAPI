# -*- coding: utf-8 -*-
import unittest
from test.base_class import BaseTestClass
from test.util import info_to_ref, make_fake_feature_set, make_genome_refs

import pytest
from installed_clients.baseclient import ServerError

N_FEATURESET_REFS = 3

class FeatureSetSetAPITest(BaseTestClass):
    @classmethod
    def prepare_data(cls: BaseTestClass) -> None:
        """Set up fixtures for the class.

        :param cls: class object
        :type cls: BaseTestClass
        """
        # Make fake genomes
        genome_refs = make_genome_refs(cls.foft, cls.ws_name)

        # Make some fake feature sets
        cls.featureset_refs = [
            make_fake_feature_set(
                f"feature_set_{i}", genome_refs[0], cls.ws_name, cls.ws_client
            )
            for i in range(N_FEATURESET_REFS)
        ]

    def test_save_feature_set_set(self):
        set_name = "test_feature_set_set"
        set_items = [{"label": "foo", "ref": ref} for ref in self.featureset_refs]
        expression_set = {"description": "test_expressions", "items": set_items}
        result = self.set_api_client.save_feature_set_set_v1(
            self.ctx,
            {
                "workspace": self.ws_name,
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
            self.set_api_client.save_feature_set_set_v1(
                self.ctx,
                {
                    "workspace": self.ws_name,
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
            self.set_api_client.save_feature_set_set_v1(
                self.ctx,
                {
                    "workspace": self.ws_name,
                    "output_object_name": "foo",
                    "data": {"description": "empty_set", "items": []},
                },
            )

    def test_get_feature_set_set(self):
        set_name = "test_featureset_set2"
        set_items = [{"label": "wt", "ref": ref} for ref in self.featureset_refs]
        featureset_set = {"description": "test_alignments", "items": set_items}
        featureset_set_ref = self.set_api_client.save_feature_set_set_v1(
            self.ctx,
            {
                "workspace": self.ws_name,
                "output_object_name": set_name,
                "data": featureset_set,
            },
        )[0]["set_ref"]

        fetched_set = self.set_api_client.get_feature_set_set_v1(
            self.ctx, {"ref": featureset_set_ref, "include_item_info": 0}
        )[0]
        assert fetched_set is not None
        assert "data" in fetched_set
        assert "info" in fetched_set
        assert len(fetched_set["data"]["items"]) == N_FEATURESET_REFS
        assert featureset_set_ref == info_to_ref(fetched_set["info"])
        for item in fetched_set["data"]["items"]:
            assert "info" not in item
            assert "ref_path" not in item
            assert "ref" in item
            assert "label" in item

        fetched_set_with_info = self.set_api_client.get_feature_set_set_v1(
            self.ctx,
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
            self.set_api_client.get_feature_set_set_v1(self.ctx, {"ref": "not_a_ref"})

    def test_get_feature_set_set_bad_path(self):
        with pytest.raises(
            ServerError, match="JSONRPCError: -32500. Object 2 cannot be accessed:"
        ):
            self.set_api_client.get_feature_set_set_v1(
                self.ctx, {"ref": "1/2/3", "path_to_set": ["foo", "bar"]}
            )

    def test_get_feature_set_set_no_ref(self):
        with pytest.raises(
            ValueError,
            match='"ref" parameter field specifiying the FeatureSet set is required',
        ):
            self.set_api_client.get_feature_set_set_v1(self.ctx, {"ref": None})
