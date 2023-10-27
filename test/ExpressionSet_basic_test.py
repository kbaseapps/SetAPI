# -*- coding: utf-8 -*-
import os
import shutil
import unittest
from pprint import pprint
import pytest
from test import TEST_BASE_DIR
from test.test_config import get_test_config
from installed_clients.FakeObjectsForTestsClient import FakeObjectsForTests
from test.util import (
    info_to_ref,
    make_fake_alignment,
    make_fake_annotation,
    make_fake_expression,
    make_fake_sampleset,
    make_fake_old_alignment_set,
    make_fake_old_expression_set,
)


class ExpressionSetAPITest(unittest.TestCase):
    DEBUG = False

    @classmethod
    def setUpClass(cls):
        props = get_test_config()
        for prop in ["cfg", "ctx", "serviceImpl", "wsClient", "wsName", "wsURL"]:
            setattr(cls, prop, props[prop])

        foft = FakeObjectsForTests(os.environ["SDK_CALLBACK_URL"])

        # Make a fake genome
        [fake_genome, fake_genome2] = foft.create_fake_genomes(
            {"ws_name": cls.wsName, "obj_names": ["fake_genome", "fake_genome2"]}
        )
        cls.genome_refs = [info_to_ref(fake_genome), info_to_ref(fake_genome2)]

        # Make some fake reads objects
        fake_reads_list = foft.create_fake_reads(
            {"ws_name": cls.wsName, "obj_names": ["reads1", "reads2", "reads3"]}
        )
        cls.alignment_refs = list()
        cls.reads_refs = list()

        # Make some fake alignments referencing those reads and genome
        dummy_filename = "dummy.txt"
        cls.dummy_path = os.path.join(cls.cfg["scratch"], dummy_filename)
        shutil.copy(os.path.join(TEST_BASE_DIR, "data", dummy_filename), cls.dummy_path)

        for idx, reads_info in enumerate(fake_reads_list):
            reads_ref = info_to_ref(reads_info)
            cls.reads_refs.append(reads_ref)
            cls.alignment_refs.append(
                make_fake_alignment(
                    os.environ["SDK_CALLBACK_URL"],
                    cls.dummy_path,
                    "fake_alignment_{}".format(idx),
                    reads_ref,
                    cls.genome_refs[0],
                    cls.wsName,
                    cls.wsClient,
                )
            )

        # Need a fake annotation to get the expression objects
        cls.annotation_ref = make_fake_annotation(
            os.environ["SDK_CALLBACK_URL"],
            cls.dummy_path,
            "fake_annotation",
            cls.wsName,
            cls.wsClient,
        )

        # Now we can phony up some expression objects to build sets out of.
        # name, genome_ref, annotation_ref, alignment_ref, ws_name, ws_client
        cls.expression_refs = list()
        for idx, alignment_ref in enumerate(cls.alignment_refs):
            cls.expression_refs.append(
                make_fake_expression(
                    os.environ["SDK_CALLBACK_URL"],
                    cls.dummy_path,
                    "fake_expression_{}".format(idx),
                    cls.genome_refs[0],
                    cls.annotation_ref,
                    alignment_ref,
                    cls.wsName,
                    cls.wsClient,
                )
            )

        # Make a fake RNASeq Alignment Set object
        # Make a fake RNASeqSampleSet
        cls.sampleset_ref = make_fake_sampleset(
            "fake_sampleset", [], [], cls.wsName, cls.wsClient
        )

        # Finally, make a couple fake RNASeqAlignmentSts objects from those alignments
        cls.fake_rnaseq_alignment_set = make_fake_old_alignment_set(
            "fake_rnaseq_alignment_set",
            cls.reads_refs,
            cls.genome_refs[0],
            cls.sampleset_ref,
            cls.alignment_refs,
            cls.wsName,
            cls.wsClient,
        )

        # Make a fake RNASeq Expression Set object
        cls.fake_rnaseq_expression_set = make_fake_old_expression_set(
            "fake_rnaseq_expression_set",
            cls.genome_refs[0],
            cls.sampleset_ref,
            cls.alignment_refs,
            cls.fake_rnaseq_alignment_set,
            cls.expression_refs,
            cls.wsName,
            cls.wsClient,
            True,
        )

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

    def test_save_expression_set(self):
        expression_set_name = "test_expression_set"
        expression_items = list()
        for ref in self.expression_refs:
            expression_items.append({"label": "foo", "ref": ref})
        expression_set = {"description": "test_expressions", "items": expression_items}
        result = self.getImpl().save_expression_set_v1(
            self.getContext(),
            {
                "workspace": self.getWsName(),
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
                        self.getWsName(),
                        self.getWsClient(),
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
            self.getImpl().save_expression_set_v1(
                self.getContext(),
                {
                    "workspace": self.getWsName(),
                    "output_object_name": expression_set_name,
                    "data": expression_set,
                },
            )

    def test_save_expression_set_no_data(self):
        with pytest.raises(
            ValueError, match='"data" parameter field required to save an ExpressionSet'
        ):
            self.getImpl().save_expression_set_v1(
                self.getContext(),
                {
                    "workspace": self.getWsName(),
                    "output_object_name": "foo",
                    "data": None,
                },
            )

    def test_save_expression_set_no_expressions(self):
        with pytest.raises(
            ValueError,
            match="An ExpressionSet must contain at least one Expression object reference.",
        ):
            self.getImpl().save_expression_set_v1(
                self.getContext(),
                {
                    "workspace": self.getWsName(),
                    "output_object_name": "foo",
                    "data": {"items": []},
                },
            )

    def test_get_expression_set(self):
        expression_set_name = "test_expression_set"
        expression_items = list()
        for ref in self.expression_refs:
            expression_items.append({"label": "wt", "ref": ref})
        expression_set = {"description": "test_alignments", "items": expression_items}
        expression_set_ref = self.getImpl().save_expression_set_v1(
            self.getContext(),
            {
                "workspace": self.getWsName(),
                "output_object_name": expression_set_name,
                "data": expression_set,
            },
        )[0]["set_ref"]

        fetched_set = self.getImpl().get_expression_set_v1(
            self.getContext(), {"ref": expression_set_ref, "include_item_info": 0}
        )[0]
        assert fetched_set is not None
        assert "data" in fetched_set
        assert "info" in fetched_set
        assert len(fetched_set["data"]["items"]) == 3
        assert expression_set_ref == info_to_ref(fetched_set["info"])
        for item in fetched_set["data"]["items"]:
            assert "info" not in item
            assert "ref_path" not in item
            assert "ref" in item
            assert "label" in item

        fetched_set_with_info = self.getImpl().get_expression_set_v1(
            self.getContext(), {"ref": expression_set_ref, "include_item_info": 1}
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
        expression_items = list()
        for ref in self.expression_refs:
            expression_items.append({"label": "wt", "ref": ref})
        expression_set = {"description": "test_alignments", "items": expression_items}
        expression_set_ref = self.getImpl().save_expression_set_v1(
            self.getContext(),
            {
                "workspace": self.getWsName(),
                "output_object_name": expression_set_name,
                "data": expression_set,
            },
        )[0]["set_ref"]

        fetched_set_with_info = self.getImpl().get_expression_set_v1(
            self.getContext(),
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
        created_expression_set_ref = self.fake_rnaseq_expression_set

        fetched_set_with_ref_path = self.getImpl().get_expression_set_v1(
            self.getContext(),
            {
                "ref": created_expression_set_ref,
                "include_item_info": 0,
                "include_set_item_ref_paths": 1,
            },
        )[0]

        for item in fetched_set_with_ref_path["data"]["items"]:
            assert "ref" in item
            assert "label" in item
            assert "ref_path" in item
            assert item["ref_path"] == f"{created_expression_set_ref};{item['ref']}"
        if self.DEBUG:
            print(
                (
                    "INPUT: CREATED KBasesets.ExpressionSet: "
                    + created_expression_set_ref
                )
            )
            pprint(fetched_set_with_ref_path)
            print("==========================")

    def test_get_expression_set_bad_ref(self):
        with pytest.raises(
            ValueError, match='"ref" parameter must be a valid workspace reference'
        ):
            self.getImpl().get_expression_set_v1(
                self.getContext(), {"ref": "not_a_ref"}
            )

    def test_get_expression_set_bad_path(self):
        with pytest.raises(Exception):
            self.getImpl().get_expression_set_v1(
                self.getContext(), {"ref": "1/2/3", "path_to_set": ["foo", "bar"]}
            )

    def test_get_expression_set_no_ref(self):
        with pytest.raises(
            ValueError,
            match='"ref" parameter field specifiying the expression set is required',
        ):
            self.getImpl().get_expression_set_v1(self.getContext(), {"ref": None})
