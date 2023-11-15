"""Basic ReadsAlignmentSet tests."""
import os
from test.util import (
    info_to_ref,
    log_this,
    make_fake_alignment,
    make_fake_annotation,
    make_fake_expression,
    make_fake_old_alignment_set,
    make_fake_old_expression_set,
    make_fake_sampleset,
)
from typing import Any

import pytest
from installed_clients.baseclient import ServerError
from SetAPI.SetAPIImpl import SetAPI

N_READS = 3
DEBUG = False


@pytest.fixture(scope="module")
def test_data(
    genome_refs: list[str],
    reads_refs: list[str],
    ws_name: str,
    clients: dict[str, Any],
    scratch_dir: str,
) -> dict[str, Any]:
    dummy_filename = "dummy.txt"
    dummy_path = os.path.join(scratch_dir, dummy_filename)

    # Make some fake alignments referencing those reads and genome
    alignment_refs = [
        make_fake_alignment(
            os.environ["SDK_CALLBACK_URL"],
            dummy_path,
            f"fake_alignment_{idx}",
            reads_ref,
            genome_refs[0],
            ws_name,
            clients["ws"],
        )
        for idx, reads_ref in enumerate(reads_refs)
    ]

    # Make a fake RNASeqSampleSet
    sampleset_ref = make_fake_sampleset(
        "fake_sampleset", [], [], ws_name, clients["ws"]
    )

    # Finally, make a couple fake RNASeqAlignmentSts objects from those alignments
    fake_rnaseq_alignment_set1 = make_fake_old_alignment_set(
        "fake_rnaseq_alignment_set1",
        reads_refs,
        genome_refs[0],
        sampleset_ref,
        alignment_refs,
        ws_name,
        clients["ws"],
    )
    fake_rnaseq_alignment_set2 = make_fake_old_alignment_set(
        "fake_rnaseq_alignment_set2",
        reads_refs,
        genome_refs[0],
        sampleset_ref,
        alignment_refs,
        ws_name,
        clients["ws"],
        include_sample_alignments=True,
    )

    # Need a fake annotation to get the expression objects
    annotation_ref = make_fake_annotation(
        os.environ["SDK_CALLBACK_URL"],
        dummy_path,
        "fake_annotation",
        ws_name,
        clients["ws"],
    )

    # Now we can phony up some expression objects to build sets out of.
    # name, genome_ref, annotation_ref, alignment_ref, ws_name: str, clients["ws"]
    expression_refs = [
        make_fake_expression(
            os.environ["SDK_CALLBACK_URL"],
            dummy_path,
            f"fake_expression_{idx}",
            genome_refs[0],
            annotation_ref,
            alignment_ref,
            ws_name,
            clients["ws"],
        )
        for idx, alignment_ref in enumerate(alignment_refs)
    ]

    # Make a fake RNASeq Expression Set object
    fake_rnaseq_expression_set = make_fake_old_expression_set(
        "fake_rnaseq_expression_set",
        genome_refs[0],
        sampleset_ref,
        alignment_refs,
        fake_rnaseq_alignment_set1,
        expression_refs,
        ws_name,
        clients["ws"],
        True,
    )

    return {
        "alignment_refs": alignment_refs,
        "dummy_path": dummy_path,
        "genome_refs": genome_refs,
        "reads_refs": reads_refs,
        "fake_rnaseq_expression_set": fake_rnaseq_expression_set,
        "fake_rnaseq_alignment_set1": fake_rnaseq_alignment_set1,
        "fake_rnaseq_alignment_set2": fake_rnaseq_alignment_set2,
    }


def test_save_alignment_set(
    test_data: dict[str, Any],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_name: str,
) -> None:
    alignment_set_name = "test_alignment_set"
    alignment_items = [
        {"label": "wt", "ref": ref} for ref in test_data["alignment_refs"]
    ]
    alignment_set = {"description": "test_alignments", "items": alignment_items}
    result = set_api_client.save_reads_alignment_set_v1(
        context,
        {
            "workspace": ws_name,
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


def test_save_alignment_set_mismatched_genomes(
    test_data: dict[str, Any],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_name: str,
    clients: dict[str, Any],
) -> None:
    alignment_set_name = "alignment_set_bad_genomes"
    alignment_set = {
        "description": "this_better_fail",
        "items": [
            {
                "ref": make_fake_alignment(
                    os.environ["SDK_CALLBACK_URL"],
                    test_data["dummy_path"],
                    "odd_alignment",
                    test_data["reads_refs"][0],
                    test_data["genome_refs"][1],
                    ws_name,
                    clients["ws"],
                ),
                "label": "odd_alignment",
            },
            {"ref": test_data["alignment_refs"][1], "label": "wt"},
        ],
    }
    with pytest.raises(
        ValueError,
        match="All ReadsAlignments in the set must be aligned against "
        "the same genome reference",
    ):
        set_api_client.save_reads_alignment_set_v1(
            context,
            {
                "workspace": ws_name,
                "output_object_name": alignment_set_name,
                "data": alignment_set,
            },
        )


def test_save_alignment_set_no_data(
    set_api_client: SetAPI, context: dict[str, str | list], ws_name: str
) -> None:
    with pytest.raises(
        ValueError,
        match='"data" parameter field required to save a ReadsAlignmentSet',
    ):
        set_api_client.save_reads_alignment_set_v1(
            context,
            {
                "workspace": ws_name,
                "output_object_name": "foo",
                "data": None,
            },
        )


def test_save_alignment_set_no_alignments(
    set_api_client: SetAPI, context: dict[str, str | list], ws_name: str
) -> None:
    with pytest.raises(
        ValueError,
        match="A ReadsAlignmentSet must contain at least one ReadsAlignment reference.",
    ):
        set_api_client.save_reads_alignment_set_v1(
            context,
            {
                "workspace": ws_name,
                "output_object_name": "foo",
                "data": {"items": []},
            },
        )


def test_get_old_alignment_set(
    test_data: dict[str, Any], set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    for ref in [
        test_data["fake_rnaseq_alignment_set1"],
        test_data["fake_rnaseq_alignment_set2"],
    ]:
        fetched_set = set_api_client.get_reads_alignment_set_v1(
            context, {"ref": ref, "include_item_info": 0}
        )[0]
        assert fetched_set is not None
        assert "data" in fetched_set
        assert "info" in fetched_set
        assert len(fetched_set["data"]["items"]) == N_READS
        assert ref == info_to_ref(fetched_set["info"])
        for item in fetched_set["data"]["items"]:
            assert "info" not in item
            assert "ref" in item
            assert "label" in item

        fetched_set_with_info = set_api_client.get_reads_alignment_set_v1(
            context,
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


def test_get_old_alignment_set_ref_path_to_set(
    test_data: dict[str, Any], config: dict[str, str], set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    alignment_ref = test_data["fake_rnaseq_alignment_set1"]
    ref_path_to_set = [test_data["fake_rnaseq_expression_set"], alignment_ref]

    fetched_set = set_api_client.get_reads_alignment_set_v1(
        context,
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
    assert len(fetched_set["data"]["items"]) == N_READS
    assert alignment_ref == info_to_ref(fetched_set["info"])
    for item in fetched_set["data"]["items"]:
        assert "info" not in item
        assert "ref" in item
        assert "label" in item
        assert "ref_path" in item
        assert item["ref_path"] == ";".join(ref_path_to_set) + ";" + item["ref"]

    if DEBUG:
        log_this(config, "RNASeq_Alignment_with_ref_path_to_set", fetched_set)


def test_get_alignment_set(
    test_data: dict[str, Any],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_name: str,
) -> None:
    alignment_set_name = "test_alignment_set"
    alignment_items = [
        {"label": "wt", "ref": ref} for ref in test_data["alignment_refs"]
    ]
    alignment_set = {"description": "test_alignments", "items": alignment_items}
    alignment_set_ref = set_api_client.save_reads_alignment_set_v1(
        context,
        {
            "workspace": ws_name,
            "output_object_name": alignment_set_name,
            "data": alignment_set,
        },
    )[0]["set_ref"]

    fetched_set = set_api_client.get_reads_alignment_set_v1(
        context, {"ref": alignment_set_ref, "include_item_info": 0}
    )[0]
    assert fetched_set is not None
    assert "data" in fetched_set
    assert "info" in fetched_set
    assert len(fetched_set["data"]["items"]) == N_READS
    assert alignment_set_ref == info_to_ref(fetched_set["info"])
    for item in fetched_set["data"]["items"]:
        assert "info" not in item
        assert "ref" in item
        assert "label" in item

    fetched_set_with_info = set_api_client.get_reads_alignment_set_v1(
        context, {"ref": alignment_set_ref, "include_item_info": 1}
    )[0]
    assert fetched_set_with_info is not None
    assert "data" in fetched_set_with_info
    for item in fetched_set_with_info["data"]["items"]:
        assert "info" in item
        assert "ref" in item
        assert "label" in item


def test_get_alignment_set_ref_path(
    test_data: dict[str, Any],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_name: str,
) -> None:
    alignment_set_name = "test_alignment_set_ref_path"
    alignment_items = [
        {"label": "wt", "ref": ref} for ref in test_data["alignment_refs"]
    ]
    alignment_set = {"description": "test_alignments", "items": alignment_items}
    alignment_set_ref = set_api_client.save_reads_alignment_set_v1(
        context,
        {
            "workspace": ws_name,
            "output_object_name": alignment_set_name,
            "data": alignment_set,
        },
    )[0]["set_ref"]

    fetched_set = set_api_client.get_reads_alignment_set_v1(
        context,
        {
            "ref": alignment_set_ref,
            "include_item_info": 0,
            "include_set_item_ref_paths": 1,
        },
    )[0]
    assert fetched_set is not None
    assert "data" in fetched_set
    assert "info" in fetched_set
    assert len(fetched_set["data"]["items"]) == N_READS
    assert alignment_set_ref == info_to_ref(fetched_set["info"])
    for item in fetched_set["data"]["items"]:
        assert "info" not in item
        assert "ref" in item
        assert "label" in item
        assert "ref_path" in item
        assert item["ref_path"] == alignment_set_ref + ";" + item["ref"]


def test_get_alignment_set_bad_ref(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    with pytest.raises(
        ValueError, match='"ref" parameter must be a valid workspace reference'
    ):
        set_api_client.get_reads_alignment_set_v1(context, {"ref": "not_a_ref"})


def test_get_alignment_set_bad_path(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    with pytest.raises(
        ServerError, match="JSONRPCError: -32500. Object 2 cannot be accessed:"
    ):
        set_api_client.get_reads_alignment_set_v1(
            context, {"ref": "1/2/3", "path_to_set": ["foo", "bar"]}
        )


def test_get_alignment_set_no_ref(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    with pytest.raises(
        ValueError,
        match='"ref" parameter field specifiying the reads alignment set is required',
    ):
        set_api_client.get_reads_alignment_set_v1(context, {"ref": None})
