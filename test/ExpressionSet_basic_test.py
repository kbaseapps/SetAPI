"""Basic ExpressionSet tests."""
from test.util import log_this

import pytest
from SetAPI.generic.constants import INC_ITEM_INFO, INC_ITEM_REF_PATHS
from SetAPI.SetAPIImpl import SetAPI
from SetAPI.util import info_to_ref

DEBUG = False


def test_save_expression_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    expression_refs: list[str],
) -> None:
    expression_set_name = "test_expression_set"
    expression_items = [{"label": "foo", "ref": ref} for ref in expression_refs]
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
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    expression_mismatched_genome_refs: list[str],
) -> None:
    set_name = "expression_set_mismatched_genomes"
    set_description = "this_better_fail"
    set_items = [
        {"label": "foo", "ref": ref} for ref in expression_mismatched_genome_refs
    ]
    expression_set = {
        "description": set_description,
        "items": set_items,
    }

    with pytest.raises(
        ValueError,
        match="All Expression objects in the set must use the same genome reference.",
    ):
        set_api_client.save_expression_set_v1(
            context,
            {
                "workspace_id": ws_id,
                "output_object_name": set_name,
                "data": expression_set,
            },
        )


def test_get_expression_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    expression_refs: list[str],
) -> None:
    expression_set_name = "test_expression_set"
    expression_items = [{"label": "wt", "ref": ref} for ref in expression_refs]
    expression_set = {"description": "test_alignments", "items": expression_items}
    n_items = len(expression_refs)
    expression_set_ref = set_api_client.save_expression_set_v1(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": expression_set_name,
            "data": expression_set,
        },
    )[0]["set_ref"]

    fetched_set = set_api_client.get_expression_set_v1(
        context, {"ref": expression_set_ref, INC_ITEM_INFO: 0}
    )[0]
    assert fetched_set is not None
    assert "data" in fetched_set
    assert "info" in fetched_set
    assert len(fetched_set["data"]["items"]) == n_items
    assert expression_set_ref == info_to_ref(fetched_set["info"])
    for item in fetched_set["data"]["items"]:
        assert "info" not in item
        assert "ref_path" not in item
        assert "ref" in item
        assert "label" in item

    fetched_set_with_info = set_api_client.get_expression_set_v1(
        context, {"ref": expression_set_ref, INC_ITEM_INFO: 1}
    )[0]
    assert fetched_set_with_info is not None
    assert "data" in fetched_set_with_info
    for item in fetched_set_with_info["data"]["items"]:
        assert "info" in item
        assert "ref" in item
        assert "label" in item
        assert "ref_path" not in item


def test_get_expression_set_ref_path(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    expression_refs: list[str],
) -> None:
    expression_set_name = "test_expression_set_ref_path"
    expression_items = [{"label": "wt", "ref": ref} for ref in expression_refs]
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
            INC_ITEM_INFO: 1,
            INC_ITEM_REF_PATHS: 1,
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
    set_api_client: SetAPI,
    context: dict[str, str | list],
    config: dict[str, str],
    rnaseq_expression_set: str,
) -> None:
    fetched_set_with_ref_path = set_api_client.get_expression_set_v1(
        context,
        {
            "ref": rnaseq_expression_set,
            INC_ITEM_INFO: 0,
            INC_ITEM_REF_PATHS: 1,
        },
    )[0]

    for item in fetched_set_with_ref_path["data"]["items"]:
        assert "ref" in item
        assert "label" in item
        assert "ref_path" in item
        assert item["ref_path"] == f"{rnaseq_expression_set};{item['ref']}"
    if DEBUG:
        log_this(
            config,
            "get_created_rnaseq_expression_set_ref_path",
            fetched_set_with_ref_path,
        )
