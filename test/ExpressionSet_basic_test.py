"""Basic ExpressionSet tests."""
from test.util import log_this

import pytest
from installed_clients.baseclient import ServerError
from SetAPI.SetAPIImpl import SetAPI
from SetAPI.util import info_to_ref

DEBUG = False


def test_save_expression_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    expression_refs,
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
    mismatched_expression_refs: list[str],
) -> None:
    set_name = "expression_set_mismatched_genomes"
    set_description = "this_better_fail"
    set_items = [
        {"ref": expression_ref, "label": "label_for_expression_ref"}
        for expression_ref in mismatched_expression_refs
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
        context, {"ref": expression_set_ref, "include_item_info": 0}
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
    set_api_client: SetAPI,
    context: dict[str, str | list],
    config: dict[str, str],
    rnaseq_expression_set: str,
) -> None:
    fetched_set_with_ref_path = set_api_client.get_expression_set_v1(
        context,
        {
            "ref": rnaseq_expression_set,
            "include_item_info": 0,
            "include_set_item_ref_paths": 1,
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
