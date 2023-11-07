# -*- coding: utf-8 -*-
import os
import shutil
from pprint import pprint
from test import TEST_BASE_DIR
from test.base_class import BaseTestClass
from test.util import (
    info_to_ref,
    make_fake_alignment,
    make_fake_annotation,
    make_fake_expression,
    make_fake_old_alignment_set,
    make_fake_old_expression_set,
    make_fake_sampleset,
    make_genome_refs,
    make_reads_refs,
)

import pytest
from installed_clients.baseclient import ServerError

N_READS_ALIGNMENTS_EXPRESSIONS = 3

class ExpressionSetAPITest(BaseTestClass):
DEBUG = False

@classmethod
def prepare_data(cls: BaseTestClass) -> None:
    """Set up fixtures for the class.

    :param cls: class object
    :type cls: BaseTestClass
    """
    # Make a fake genome
    cls.genome_refs = make_genome_refs(
        cls.foft,
        cls.ws_name
    )

    # Make some fake reads objects
    reads_refs = make_reads_refs(cls.foft, cls.ws_name)

    # Make some fake alignments referencing those reads and genome
    dummy_filename = "dummy.txt"
    cls.dummy_path = os.path.join(cls.config["scratch"], dummy_filename)
    shutil.copy(os.path.join(TEST_BASE_DIR, "data", dummy_filename), cls.dummy_path)

    cls.alignment_refs = [
        make_fake_alignment(
            os.environ["SDK_CALLBACK_URL"],
            cls.dummy_path,
            f"fake_alignment_{idx}",
            reads_ref,
            cls.genome_refs[0],
            cls.ws_name,
            cls.ws_client,
        ) for idx, reads_ref in enumerate(reads_refs)]

    # Need a fake annotation to get the expression objects
    cls.annotation_ref = make_fake_annotation(
        os.environ["SDK_CALLBACK_URL"],
        cls.dummy_path,
        "fake_annotation",
        cls.ws_name,
        cls.ws_client,
    )

    # Now we can phony up some expression objects to build sets out of.
    # name, genome_ref, annotation_ref, alignment_ref, ws_name, ws_client
    cls.expression_refs = [
        make_fake_expression(
            os.environ["SDK_CALLBACK_URL"],
            cls.dummy_path,
            f"fake_expression_{idx}",
            cls.genome_refs[0],
            cls.annotation_ref,
            alignment_ref,
            cls.ws_name,
            cls.ws_client,
        )
        for idx, alignment_ref in enumerate(cls.alignment_refs)
    ]

    # Make a fake RNASeq Alignment Set object
    # Make a fake RNASeqSampleSet
    cls.sampleset_ref = make_fake_sampleset(
        "fake_sampleset", [], [], cls.ws_name, cls.ws_client
    )

    # Finally, make a couple fake RNASeqAlignmentSts objects from those alignments
    cls.fake_rnaseq_alignment_set = make_fake_old_alignment_set(
        "fake_rnaseq_alignment_set",
        reads_refs,
        cls.genome_refs[0],
        cls.sampleset_ref,
        cls.alignment_refs,
        cls.ws_name,
        cls.ws_client,
    )

    # Make a fake RNASeq Expression Set object
    cls.fake_rnaseq_expression_set = make_fake_old_expression_set(
        "fake_rnaseq_expression_set",
        cls.genome_refs[0],
        cls.sampleset_ref,
        cls.alignment_refs,
        cls.fake_rnaseq_alignment_set,
        cls.expression_refs,
        cls.ws_name,
        cls.ws_client,
        True,
    )

def test_save_expression_set(self):
    expression_set_name = "test_expression_set"
    expression_items = [
        {"label": "foo", "ref": ref} for ref in self.expression_refs
    ]
    expression_set = {"description": "test_expressions", "items": expression_items}
    result = self.set_api_client.save_expression_set_v1(
        self.ctx,
        {
            "workspace": self.ws_name,
            "output_object_name": expression_set_name,
            "data": expression_set,
        },
    )[0]
    assert result is not None
    assert "set_ref" in result
    assert "set_info" in result
    assert result["set_ref"] == info_to_ref(result["set_info"])
    assert result["set_info"][1] == expression_set_name
    assert "KBaseSets.ExpressionSet" in result["set_info"][2]

def test_save_expression_set_mismatched_genomes(self):
    expression_set_name = "expression_set_bad_genomes"
    expression_set = {
        "description": "this_better_fail",
        "items": [
            {
                "ref": make_fake_expression(
                    os.environ["SDK_CALLBACK_URL"],
                    self.dummy_path,
                    "odd_expression",
                    self.genome_refs[1],
                    self.annotation_ref,
                    self.alignment_refs[0],
                    self.ws_name,
                    self.ws_client,
                ),
                "label": "odd_alignment",
            },
            {"ref": self.alignment_refs[1], "label": "not_so_odd"},
        ],
    }
    with pytest.raises(
        ValueError,
        match="All Expression objects in the set must use the same genome reference.",
    ):
        self.set_api_client.save_expression_set_v1(
            self.ctx,
            {
                "workspace": self.ws_name,
                "output_object_name": expression_set_name,
                "data": expression_set,
            },
        )

def test_save_expression_set_no_data(self):
    with pytest.raises(
        ValueError, match='"data" parameter field required to save an ExpressionSet'
    ):
        self.set_api_client.save_expression_set_v1(
            self.ctx,
            {
                "workspace": self.ws_name,
                "output_object_name": "foo",
                "data": None,
            },
        )

def test_save_expression_set_no_expressions(self):
    with pytest.raises(
        ValueError,
        match="An ExpressionSet must contain at least one Expression object reference.",
    ):
        self.set_api_client.save_expression_set_v1(
            self.ctx,
            {
                "workspace": self.ws_name,
                "output_object_name": "foo",
                "data": {"items": []},
            },
        )

def test_get_expression_set(self):
    expression_set_name = "test_expression_set"
    expression_items = [{"label": "wt", "ref": ref} for ref in self.expression_refs]
    expression_set = {"description": "test_alignments", "items": expression_items}
    expression_set_ref = self.set_api_client.save_expression_set_v1(
        self.ctx,
        {
            "workspace": self.ws_name,
            "output_object_name": expression_set_name,
            "data": expression_set,
        },
    )[0]["set_ref"]

    fetched_set = self.set_api_client.get_expression_set_v1(
        self.ctx, {"ref": expression_set_ref, "include_item_info": 0}
    )[0]
    assert fetched_set is not None
    assert "data" in fetched_set
    assert "info" in fetched_set
    assert len(fetched_set["data"]["items"]) == N_READS_ALIGNMENTS_EXPRESSIONS
    assert expression_set_ref == info_to_ref(fetched_set["info"])
    for item in fetched_set["data"]["items"]:
        assert "info" not in item
        assert "ref_path" not in item
        assert "ref" in item
        assert "label" in item

    fetched_set_with_info = self.set_api_client.get_expression_set_v1(
        self.ctx, {"ref": expression_set_ref, "include_item_info": 1}
    )[0]
    assert fetched_set_with_info is not None
    assert "data" in fetched_set_with_info
    for item in fetched_set_with_info["data"]["items"]:
        assert "info" in item
        assert "ref" in item
        assert "label" in item
        assert "ref_path" not in item

def test_get_expression_set_ref_path(self):
    expression_set_name = "test_expression_set_ref_path"
    expression_items = [{"label": "wt", "ref": ref} for ref in self.expression_refs]
    expression_set = {"description": "test_alignments", "items": expression_items}
    expression_set_ref = self.set_api_client.save_expression_set_v1(
        self.ctx,
        {
            "workspace": self.ws_name,
            "output_object_name": expression_set_name,
            "data": expression_set,
        },
    )[0]["set_ref"]

    fetched_set_with_info = self.set_api_client.get_expression_set_v1(
        self.ctx,
        {
            "ref": expression_set_ref,
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
        assert item["ref_path"] == expression_set_ref + ";" + item["ref"]

def test_get_created_rnaseq_expression_set_ref_path(self):
    fetched_set_with_ref_path = self.set_api_client.get_expression_set_v1(
        self.ctx,
        {
            "ref": self.fake_rnaseq_expression_set,
            "include_item_info": 0,
            "include_set_item_ref_paths": 1,
        },
    )[0]

    for item in fetched_set_with_ref_path["data"]["items"]:
        assert "ref" in item
        assert "label" in item
        assert "ref_path" in item
        assert item["ref_path"] == f"{self.fake_rnaseq_expression_set};{item['ref']}"
    if self.DEBUG:
        print(
            "INPUT: CREATED KBasesets.ExpressionSet: " + self.fake_rnaseq_expression_set
        )
        pprint(fetched_set_with_ref_path)
        print("==========================")

def test_get_expression_set_bad_ref(self):
    with pytest.raises(
        ValueError, match='"ref" parameter must be a valid workspace reference'
    ):
        self.set_api_client.get_expression_set_v1(self.ctx, {"ref": "not_a_ref"})

def test_get_expression_set_bad_path(self):
    with pytest.raises(
        ServerError, match="JSONRPCError: -32500. Object 2 cannot be accessed: "
    ):
        self.set_api_client.get_expression_set_v1(
            self.ctx, {"ref": "1/2/3", "path_to_set": ["foo", "bar"]}
        )

def test_get_expression_set_no_ref(self):
    with pytest.raises(
        ValueError,
        match='"ref" parameter field specifiying the expression set is required',
    ):
        self.set_api_client.get_expression_set_v1(self.ctx, {"ref": None})
