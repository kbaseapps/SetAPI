# -*- coding: utf-8 -*-
from test.base_class import BaseTestClass
from test.util import info_to_ref, make_fake_diff_exp_matrix, make_genome_refs

import pytest
from installed_clients.baseclient import ServerError


N_MATRICES = 3

class DifferentialExpressionMatrixSetAPITest(BaseTestClass):
    @classmethod
    def prepare_data(cls: BaseTestClass) -> None:
        """Set up fixtures for the class.

        :param cls: class object
        :type cls: BaseTestClass
        """
        # Make fake genomes
        cls.genome_refs = make_genome_refs(cls.foft, cls.ws_name)

        # Make fake diff exp matrices
        cls.diff_exps_no_genome = [
            make_fake_diff_exp_matrix(
                f"fake_mat_no_genome_{i}",
                cls.ws_name,
                cls.ws_client
            )
            for i in range(N_MATRICES)
        ]

        cls.diff_exps_genome = [
            make_fake_diff_exp_matrix(
                f"fake_mat_genome_{i}",
                cls.ws_name,
                cls.ws_client,
                genome_ref=cls.genome_refs[0],
            )
            for i in range(N_MATRICES)
        ]

    def test_save_diff_exp_matrix_set(self):
        set_name = "test_diff_exp_matrix_set"
        set_items = [{"label": "foo", "ref": ref} for ref in self.diff_exps_genome]
        matrix_set = {"description": "test_matrix_set", "items": set_items}
        result = self.set_api_client.save_differential_expression_matrix_set_v1(
            self.ctx,
            {
                "workspace": self.ws_name,
                "output_object_name": set_name,
                "data": matrix_set,
            },
        )[0]
        assert result is not None
        assert "set_ref" in result
        assert "set_info" in result
        assert result["set_ref"] == info_to_ref(result["set_info"])
        assert result["set_info"][1] == set_name
        assert "KBaseSets.DifferentialExpressionMatrixSet" in result["set_info"][2]

    def test_save_diff_exp_matrix_set_no_genome(self):
        set_name = "test_de_matrix_set_no_genome"
        set_items = [{"label": "foo", "ref": ref} for ref in self.diff_exps_no_genome]
        matrix_set = {"description": "test_matrix_set", "items": set_items}
        result = self.set_api_client.save_differential_expression_matrix_set_v1(
            self.ctx,
            {
                "workspace": self.ws_name,
                "output_object_name": set_name,
                "data": matrix_set,
            },
        )[0]
        assert result is not None
        assert "set_ref" in result
        assert "set_info" in result
        assert result["set_ref"] == info_to_ref(result["set_info"])
        assert result["set_info"][1] == set_name
        assert "KBaseSets.DifferentialExpressionMatrixSet" in result["set_info"][2]

    def test_save_dem_set_mismatched_genomes(self):
        set_name = "dem_set_bad_genomes"
        dem_set = {
            "description": "this_better_fail",
            "items": [
                {
                    "ref": make_fake_diff_exp_matrix(
                        "odd_dem",
                        self.ws_name,
                        self.ws_client,
                        genome_ref=self.genome_refs[1],
                    ),
                    "label": "odd_alignment",
                },
                {"ref": self.diff_exps_genome[0], "label": "not_so_odd"},
            ],
        }
        with pytest.raises(
            ValueError,
            match="All Differential Expression Matrix objects in the set must use the same genome reference.",
        ):
            self.set_api_client.save_differential_expression_matrix_set_v1(
                self.ctx,
                {
                    "workspace": self.ws_name,
                    "output_object_name": set_name,
                    "data": dem_set,
                },
            )

    def test_save_dem_set_no_data(self):
        with pytest.raises(
            ValueError,
            match='"data" parameter field required to save a DifferentialExpressionMatrixSet',
        ):
            self.set_api_client.save_differential_expression_matrix_set_v1(
                self.ctx,
                {
                    "workspace": self.ws_name,
                    "output_object_name": "foo",
                    "data": None,
                },
            )

    def test_save_dem_set_no_dem(self):
        with pytest.raises(
            ValueError,
            match="A DifferentialExpressionMatrixSet must contain at least one DifferentialExpressionMatrix object reference.",
        ):
            self.set_api_client.save_differential_expression_matrix_set_v1(
                self.ctx,
                {
                    "workspace": self.ws_name,
                    "output_object_name": "foo",
                    "data": {"items": []},
                },
            )

    def test_get_dem_set(self):
        set_name = "test_expression_set"
        set_items = [{"label": "wt", "ref": ref} for ref in self.diff_exps_no_genome]
        dem_set = {"description": "test_test_diffExprMatrixSet", "items": set_items}
        dem_set_ref = self.set_api_client.save_differential_expression_matrix_set_v1(
            self.ctx,
            {
                "workspace": self.ws_name,
                "output_object_name": set_name,
                "data": dem_set,
            },
        )[0]["set_ref"]

        fetched_set = self.set_api_client.get_differential_expression_matrix_set_v1(
            self.ctx, {"ref": dem_set_ref, "include_item_info": 0}
        )[0]
        assert fetched_set is not None
        assert "data" in fetched_set
        assert "info" in fetched_set
        assert len(fetched_set["data"]["items"]) == N_MATRICES
        assert dem_set_ref == info_to_ref(fetched_set["info"])
        for item in fetched_set["data"]["items"]:
            assert "info" not in item
            assert "ref" in item
            assert "ref_path" not in item
            assert "label" in item

        fetched_set_with_info = (
            self.set_api_client.get_differential_expression_matrix_set_v1(
                self.ctx, {"ref": dem_set_ref, "include_item_info": 1}
            )[0]
        )
        assert fetched_set_with_info is not None
        assert "data" in fetched_set_with_info
        for item in fetched_set_with_info["data"]["items"]:
            assert "info" in item
            assert "ref" in item
            assert "label" in item

    def test_get_dem_set_ref_path(self):
        set_name = "test_diff_expression_set_ref_path"
        set_items = [{"label": "wt", "ref": ref} for ref in self.diff_exps_no_genome]
        dem_set = {"description": "test_diffExprMatrixSet_ref_path", "items": set_items}
        dem_set_ref = self.set_api_client.save_differential_expression_matrix_set_v1(
            self.ctx,
            {
                "workspace": self.ws_name,
                "output_object_name": set_name,
                "data": dem_set,
            },
        )[0]["set_ref"]

        fetched_set_with_ref_path = (
            self.set_api_client.get_differential_expression_matrix_set_v1(
                self.ctx,
                {
                    "ref": dem_set_ref,
                    "include_item_info": 0,
                    "include_set_item_ref_paths": 1,
                },
            )[0]
        )
        assert fetched_set_with_ref_path is not None
        assert "data" in fetched_set_with_ref_path
        assert "info" in fetched_set_with_ref_path
        assert len(fetched_set_with_ref_path["data"]["items"]) == N_MATRICES
        assert dem_set_ref == info_to_ref(fetched_set_with_ref_path["info"])
        for item in fetched_set_with_ref_path["data"]["items"]:
            assert "info" not in item
            assert "ref" in item
            assert "label" in item
            assert "ref_path" in item
            assert item["ref_path"] == dem_set_ref + ";" + item["ref"]
        # pprint(fetched_set_with_ref_path)

    def test_get_dem_set_bad_ref(self):
        with pytest.raises(
            ValueError, match='"ref" parameter must be a valid workspace reference'
        ):
            self.set_api_client.get_differential_expression_matrix_set_v1(
                self.ctx, {"ref": "not_a_ref"}
            )

    def test_get_dem_set_bad_path(self):
        with pytest.raises(
            ServerError, match="JSONRPCError: -32500. Object 2 cannot be accessed: "
        ):
            self.set_api_client.get_differential_expression_matrix_set_v1(
                self.ctx, {"ref": "1/2/3", "path_to_set": ["foo", "bar"]}
            )

    def test_get_dem_set_no_ref(self):
        with pytest.raises(
            ValueError,
            match='"ref" parameter field specifiying the DifferentialExpressionMatrix set is required',
        ):
            self.set_api_client.get_differential_expression_matrix_set_v1(
                self.ctx, {"ref": None}
            )
