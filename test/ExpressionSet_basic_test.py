"""Basic ExpressionSet tests."""
import os
from test.util import (
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
from SetAPI.util import info_to_ref

N_READS_ALIGNMENTS_EXPRESSIONS = 3
DEBUG = False


@pytest.fixture(scope="module")
def test_data(
    genome_refs: list[str],
    reads_refs: list[str],
    ws_id: int,
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
            ws_id,
            clients["ws"],
        )
        for idx, reads_ref in enumerate(reads_refs)
    ]

    # Need a fake annotation to get the expression objects
    annotation_ref = make_fake_annotation(
        os.environ["SDK_CALLBACK_URL"],
        dummy_path,
        "fake_annotation",
        ws_id,
        clients["ws"],
    )

    # Now we can phony up some expression objects to build sets out of.
    expression_refs = [
        make_fake_expression(
            os.environ["SDK_CALLBACK_URL"],
            dummy_path,
            f"fake_expression_{idx}",
            genome_refs[0],
            annotation_ref,
            alignment_ref,
            ws_id,
            clients["ws"],
        )
        for idx, alignment_ref in enumerate(alignment_refs)
    ]

    # Make a fake RNASeq Alignment Set object
    # Make a fake RNASeqSampleSet
    sampleset_ref = make_fake_sampleset("fake_sampleset", [], [], ws_id, clients["ws"])

    # Finally, make a couple fake RNASeqAlignmentSts objects from those alignments
    fake_rnaseq_alignment_set = make_fake_old_alignment_set(
        "fake_rnaseq_alignment_set",
        reads_refs,
        genome_refs[0],
        sampleset_ref,
        alignment_refs,
        ws_id,
        clients["ws"],
    )

    # Make a fake RNASeq Expression Set object
    fake_rnaseq_expression_set = make_fake_old_expression_set(
        "fake_rnaseq_expression_set",
        genome_refs[0],
        sampleset_ref,
        alignment_refs,
        fake_rnaseq_alignment_set,
        expression_refs,
        ws_id,
        clients["ws"],
        True,
    )

    return {
        "fake_rnaseq_expression_set": fake_rnaseq_expression_set,
        "expression_refs": expression_refs,
        "genome_refs": genome_refs,
        "annotation_ref": annotation_ref,
        "alignment_refs": alignment_refs,
        "dummy_path": dummy_path,
    }


def test_save_expression_set(
    test_data: dict, set_api_client: SetAPI, context: dict[str, str | list], ws_id: int
) -> None:
    expression_set_name = "test_expression_set"
    expression_items = [
        {"label": "foo", "ref": ref} for ref in test_data["expression_refs"]
    ]
    expression_set = {"description": "test_expressions", "items": expression_items}
    result = set_api_client.save_expression_set_v1(
        context,
        {
            "workspace_id": ws_id,
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


def test_save_expression_set_mismatched_genomes(
    test_data: dict,
    ws_id: int,
    clients: dict[str, Any],
    set_api_client: SetAPI,
    context: dict[str, str | list],
) -> None:
    expression_set_name = "expression_set_bad_genomes"
    expression_set = {
        "description": "this_better_fail",
        "items": [
            {
                "ref": make_fake_expression(
                    os.environ["SDK_CALLBACK_URL"],
                    test_data["dummy_path"],
                    "odd_expression",
                    test_data["genome_refs"][1],
                    test_data["annotation_ref"],
                    test_data["alignment_refs"][0],
                    ws_id,
                    clients["ws"],
                ),
                "label": "odd_alignment",
            },
            {"ref": test_data["alignment_refs"][1], "label": "not_so_odd"},
        ],
    }
    with pytest.raises(
        ValueError,
        match="All Expression objects in the set must use the same genome reference.",
    ):
        set_api_client.save_expression_set_v1(
            context,
            {
                "workspace_id": ws_id,
                "output_object_name": expression_set_name,
                "data": expression_set,
            },
        )


def test_save_expression_set_no_data(
    set_api_client: SetAPI, context: dict[str, str | list], ws_id: int
) -> None:
    with pytest.raises(
        ValueError, match='"data" parameter field required to save an ExpressionSet'
    ):
        set_api_client.save_expression_set_v1(
            context,
            {
                "workspace_id": ws_id,
                "output_object_name": "foo",
                "data": None,
            },
        )


def test_save_expression_set_no_expressions(
    set_api_client: SetAPI, context: dict[str, str | list], ws_id: int
) -> None:
    with pytest.raises(
        ValueError,
        match="An ExpressionSet must contain at least one Expression object reference.",
    ):
        set_api_client.save_expression_set_v1(
            context,
            {
                "workspace_id": ws_id,
                "output_object_name": "foo",
                "data": {"items": []},
            },
        )


def test_get_expression_set(
    test_data: dict, set_api_client: SetAPI, context: dict[str, str | list], ws_id: int
) -> None:
    expression_set_name = "test_expression_set"
    expression_items = [
        {"label": "wt", "ref": ref} for ref in test_data["expression_refs"]
    ]
    expression_set = {"description": "test_alignments", "items": expression_items}
    expression_set_ref = set_api_client.save_expression_set_v1(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": expression_set_name,
            "data": expression_set,
        },
    )[0]["set_ref"]

    fetched_set = set_api_client.get_expression_set_v1(
        context, {"ref": expression_set_ref, "include_item_info": 0}
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

    fetched_set_with_info = set_api_client.get_expression_set_v1(
        context, {"ref": expression_set_ref, "include_item_info": 1}
    )[0]
    assert fetched_set_with_info is not None
    assert "data" in fetched_set_with_info
    for item in fetched_set_with_info["data"]["items"]:
        assert "info" in item
        assert "ref" in item
        assert "label" in item
        assert "ref_path" not in item


def test_get_expression_set_ref_path(
    test_data: dict, set_api_client: SetAPI, context: dict[str, str | list], ws_id: int
) -> None:
    expression_set_name = "test_expression_set_ref_path"
    expression_items = [
        {"label": "wt", "ref": ref} for ref in test_data["expression_refs"]
    ]
    expression_set = {"description": "test_alignments", "items": expression_items}
    expression_set_ref = set_api_client.save_expression_set_v1(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": expression_set_name,
            "data": expression_set,
        },
    )[0]["set_ref"]

    fetched_set_with_info = set_api_client.get_expression_set_v1(
        context,
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


def test_get_created_rnaseq_expression_set_ref_path(
    test_data: dict,
    config: dict[str, str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
) -> None:
    fetched_set_with_ref_path = set_api_client.get_expression_set_v1(
        context,
        {
            "ref": test_data["fake_rnaseq_expression_set"],
            "include_item_info": 0,
            "include_set_item_ref_paths": 1,
        },
    )[0]

    for item in fetched_set_with_ref_path["data"]["items"]:
        assert "ref" in item
        assert "label" in item
        assert "ref_path" in item
        assert (
            item["ref_path"]
            == f"{test_data['fake_rnaseq_expression_set']};{item['ref']}"
        )
    if DEBUG:
        log_this(
            config,
            "get_created_rnaseq_expression_set_ref_path",
            fetched_set_with_ref_path,
        )


def test_get_expression_set_bad_ref(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    with pytest.raises(
        ValueError, match='"ref" parameter must be a valid workspace reference'
    ):
        set_api_client.get_expression_set_v1(context, {"ref": "not_a_ref"})


def test_get_expression_set_bad_path(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    with pytest.raises(
        ServerError, match="JSONRPCError: -32500. Object 2 cannot be accessed: "
    ):
        set_api_client.get_expression_set_v1(
            context, {"ref": "1/2/3", "path_to_set": ["foo", "bar"]}
        )


def test_get_expression_set_no_ref(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    with pytest.raises(
        ValueError,
        match='"ref" parameter field specifiying the expression set is required',
    ):
        set_api_client.get_expression_set_v1(context, {"ref": None})
