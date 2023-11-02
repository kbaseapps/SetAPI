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
)

import pytest
from installed_clients.baseclient import ServerError


class ReadsAlignmentSetAPITest(BaseTestClass):
    DEBUG = False

    @classmethod
    def prepare_data(cls: BaseTestClass) -> None:
        """Set up fixtures for the class.

        :param cls: class object
        :type cls: BaseTestClass
        """
        # Make a fake genome
        [fake_genome, fake_genome2] = cls.foft.create_fake_genomes(
            {"ws_name": cls.wsName, "obj_names": ["fake_genome", "fake_genome2"]}
        )
        cls.genome_refs = [info_to_ref(fake_genome), info_to_ref(fake_genome2)]

        # Make some fake reads objects
        fake_reads_list = cls.foft.create_fake_reads(
            {"ws_name": cls.wsName, "obj_names": ["reads1", "reads2", "reads3"]}
        )
        cls.alignment_refs = []
        cls.reads_refs = []

        dummy_filename = "dummy.txt"
        cls.dummy_path = os.path.join(cls.cfg["scratch"], dummy_filename)
        shutil.copy(os.path.join(TEST_BASE_DIR, "data", dummy_filename), cls.dummy_path)

        # Make some fake alignments referencing those reads and genome
        for idx, reads_info in enumerate(fake_reads_list):
            reads_ref = info_to_ref(reads_info)
            cls.reads_refs.append(reads_ref)
            cls.alignment_refs.append(
                make_fake_alignment(
                    os.environ["SDK_CALLBACK_URL"],
                    cls.dummy_path,
                    f"fake_alignment_{idx}",
                    reads_ref,
                    cls.genome_refs[0],
                    cls.wsName,
                    cls.wsClient,
                )
            )

        # Make a fake RNASeqSampleSet
        cls.sampleset_ref = make_fake_sampleset(
            "fake_sampleset", [], [], cls.wsName, cls.wsClient
        )

        # Finally, make a couple fake RNASeqAlignmentSts objects from those alignments
        cls.fake_rnaseq_alignment_set1 = make_fake_old_alignment_set(
            "fake_rnaseq_alignment_set1",
            cls.reads_refs,
            cls.genome_refs[0],
            cls.sampleset_ref,
            cls.alignment_refs,
            cls.wsName,
            cls.wsClient,
        )
        cls.fake_rnaseq_alignment_set2 = make_fake_old_alignment_set(
            "fake_rnaseq_alignment_set2",
            cls.reads_refs,
            cls.genome_refs[0],
            cls.sampleset_ref,
            cls.alignment_refs,
            cls.wsName,
            cls.wsClient,
            include_sample_alignments=True,
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
        cls.expression_refs = [
            make_fake_expression(
                os.environ["SDK_CALLBACK_URL"],
                cls.dummy_path,
                f"fake_expression_{idx}",
                cls.genome_refs[0],
                cls.annotation_ref,
                alignment_ref,
                cls.wsName,
                cls.wsClient,
            )
            for idx, alignment_ref in enumerate(cls.alignment_refs)
        ]

        # Make a fake RNASeq Expression Set object
        cls.fake_rnaseq_expression_set = make_fake_old_expression_set(
            "fake_rnaseq_expression_set",
            cls.genome_refs[0],
            cls.sampleset_ref,
            cls.alignment_refs,
            cls.fake_rnaseq_alignment_set1,
            cls.expression_refs,
            cls.wsName,
            cls.wsClient,
            True,
        )

    def test_save_alignment_set(self):
        alignment_set_name = "test_alignment_set"
        alignment_items = [{"label": "wt", "ref": ref} for ref in self.alignment_refs]
        alignment_set = {"description": "test_alignments", "items": alignment_items}
        result = self.serviceImpl.save_reads_alignment_set_v1(
            self.ctx,
            {
                "workspace": self.wsName,
                "output_object_name": alignment_set_name,
                "data": alignment_set,
            },
        )[0]
        assert result is not None
        assert "set_ref" in result
        assert "set_info" in result
        assert result["set_ref"] == info_to_ref(result["set_info"])
        assert result["set_info"][1] == alignment_set_name
        assert "KBaseSets.ReadsAlignmentSet" in result["set_info"][2]

    def test_save_alignment_set_mismatched_genomes(self):
        alignment_set_name = "alignment_set_bad_genomes"
        alignment_set = {
            "description": "this_better_fail",
            "items": [
                {
                    "ref": make_fake_alignment(
                        os.environ["SDK_CALLBACK_URL"],
                        self.dummy_path,
                        "odd_alignment",
                        self.reads_refs[0],
                        self.genome_refs[1],
                        self.wsName,
                        self.wsClient,
                    ),
                    "label": "odd_alignment",
                },
                {"ref": self.alignment_refs[1], "label": "wt"},
            ],
        }
        with pytest.raises(
            ValueError,
            match="All ReadsAlignments in the set must be aligned against "
            "the same genome reference",
        ):
            self.serviceImpl.save_reads_alignment_set_v1(
                self.ctx,
                {
                    "workspace": self.wsName,
                    "output_object_name": alignment_set_name,
                    "data": alignment_set,
                },
            )

    def test_save_alignment_set_no_data(self):
        with pytest.raises(
            ValueError,
            match='"data" parameter field required to save a ReadsAlignmentSet',
        ):
            self.serviceImpl.save_reads_alignment_set_v1(
                self.ctx,
                {
                    "workspace": self.wsName,
                    "output_object_name": "foo",
                    "data": None,
                },
            )

    def test_save_alignment_set_no_alignments(self):
        with pytest.raises(
            ValueError,
            match="A ReadsAlignmentSet must contain at least one ReadsAlignment reference.",
        ):
            self.serviceImpl.save_reads_alignment_set_v1(
                self.ctx,
                {
                    "workspace": self.wsName,
                    "output_object_name": "foo",
                    "data": {"items": []},
                },
            )

    def test_get_old_alignment_set(self):
        for ref in [self.fake_rnaseq_alignment_set1, self.fake_rnaseq_alignment_set2]:
            fetched_set = self.serviceImpl.get_reads_alignment_set_v1(
                self.ctx, {"ref": ref, "include_item_info": 0}
            )[0]
            assert fetched_set is not None
            assert "data" in fetched_set
            assert "info" in fetched_set
            assert len(fetched_set["data"]["items"]) == 3
            assert ref == info_to_ref(fetched_set["info"])
            for item in fetched_set["data"]["items"]:
                assert "info" not in item
                assert "ref" in item
                assert "label" in item

            fetched_set_with_info = self.serviceImpl.get_reads_alignment_set_v1(
                self.ctx,
                {"ref": ref, "include_item_info": 1, "include_set_item_ref_paths": 1},
            )[0]
            assert fetched_set_with_info is not None
            assert "data" in fetched_set_with_info
            for item in fetched_set_with_info["data"]["items"]:
                assert "info" in item
                assert "ref" in item
                assert "label" in item
                assert "ref_path" in item
                assert item["ref_path"] == ref + ";" + item["ref"]

    def test_get_old_alignment_set_ref_path_to_set(self):
        alignment_ref = self.fake_rnaseq_alignment_set1
        ref_path_to_set = [self.fake_rnaseq_expression_set, alignment_ref]

        fetched_set = self.serviceImpl.get_reads_alignment_set_v1(
            self.ctx,
            {
                "ref": alignment_ref,
                "ref_path_to_set": ref_path_to_set,
                "include_item_info": 0,
                "include_set_item_ref_paths": 1,
            },
        )[0]
        assert fetched_set is not None
        assert "data" in fetched_set
        assert "info" in fetched_set
        assert len(fetched_set["data"]["items"]) == 3
        assert alignment_ref == info_to_ref(fetched_set["info"])
        for item in fetched_set["data"]["items"]:
            assert "info" not in item
            assert "ref" in item
            assert "label" in item
            assert "ref_path" in item
            assert item["ref_path"] == ";".join(ref_path_to_set) + ";" + item["ref"]

        if self.DEBUG:
            print("======  RNASeq Alignment with ref_path_to_set ========")
            pprint(fetched_set)
            print("======================================================")

    def test_get_alignment_set(self):
        alignment_set_name = "test_alignment_set"
        alignment_items = [{"label": "wt", "ref": ref} for ref in self.alignment_refs]
        alignment_set = {"description": "test_alignments", "items": alignment_items}
        alignment_set_ref = self.serviceImpl.save_reads_alignment_set_v1(
            self.ctx,
            {
                "workspace": self.wsName,
                "output_object_name": alignment_set_name,
                "data": alignment_set,
            },
        )[0]["set_ref"]

        fetched_set = self.serviceImpl.get_reads_alignment_set_v1(
            self.ctx, {"ref": alignment_set_ref, "include_item_info": 0}
        )[0]
        assert fetched_set is not None
        assert "data" in fetched_set
        assert "info" in fetched_set
        assert len(fetched_set["data"]["items"]) == 3
        assert alignment_set_ref == info_to_ref(fetched_set["info"])
        for item in fetched_set["data"]["items"]:
            assert "info" not in item
            assert "ref" in item
            assert "label" in item

        fetched_set_with_info = self.serviceImpl.get_reads_alignment_set_v1(
            self.ctx, {"ref": alignment_set_ref, "include_item_info": 1}
        )[0]
        assert fetched_set_with_info is not None
        assert "data" in fetched_set_with_info
        for item in fetched_set_with_info["data"]["items"]:
            assert "info" in item
            assert "ref" in item
            assert "label" in item

    def test_get_alignment_set_ref_path(self):
        alignment_set_name = "test_alignment_set_ref_path"
        alignment_items = [{"label": "wt", "ref": ref} for ref in self.alignment_refs]
        alignment_set = {"description": "test_alignments", "items": alignment_items}
        alignment_set_ref = self.serviceImpl.save_reads_alignment_set_v1(
            self.ctx,
            {
                "workspace": self.wsName,
                "output_object_name": alignment_set_name,
                "data": alignment_set,
            },
        )[0]["set_ref"]

        fetched_set = self.serviceImpl.get_reads_alignment_set_v1(
            self.ctx,
            {
                "ref": alignment_set_ref,
                "include_item_info": 0,
                "include_set_item_ref_paths": 1,
            },
        )[0]
        assert fetched_set is not None
        assert "data" in fetched_set
        assert "info" in fetched_set
        assert len(fetched_set["data"]["items"]) == 3
        assert alignment_set_ref == info_to_ref(fetched_set["info"])
        for item in fetched_set["data"]["items"]:
            assert "info" not in item
            assert "ref" in item
            assert "label" in item
            assert "ref_path" in item
            assert item["ref_path"] == alignment_set_ref + ";" + item["ref"]

    def test_get_alignment_set_bad_ref(self):
        with pytest.raises(
            ValueError, match='"ref" parameter must be a valid workspace reference'
        ):
            self.serviceImpl.get_reads_alignment_set_v1(self.ctx, {"ref": "not_a_ref"})

    def test_get_alignment_set_bad_path(self):
        with pytest.raises(
            ServerError, match="JSONRPCError: -32500. Object 2 cannot be accessed:"
        ):
            self.serviceImpl.get_reads_alignment_set_v1(
                self.ctx, {"ref": "1/2/3", "path_to_set": ["foo", "bar"]}
            )

    def test_get_alignment_set_no_ref(self):
        with pytest.raises(
            ValueError,
            match='"ref" parameter field specifiying the reads alignment set is required',
        ):
            self.serviceImpl.get_reads_alignment_set_v1(self.ctx, {"ref": None})
