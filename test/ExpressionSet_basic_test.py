"""Basic ExpressionSet tests."""
from test.common_test import check_get_set, check_save_set_output
from test.util import log_this
from typing import Any

import pytest
from SetAPI.expression.ExpressionSetInterfaceV1 import ExpressionSetInterfaceV1
from SetAPI.generic.constants import INC_ITEM_INFO, INC_ITEM_REF_PATHS, REF_PATH_TO_SET
from SetAPI.SetAPIImpl import SetAPI

DEBUG = False

API_CLASS = ExpressionSetInterfaceV1
SET_TYPE = "expression"


def save_expression_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    set_name: str,
    set_data: dict[str, Any],
) -> dict[str, Any]:
    """Given a set_name and set_data, save an expression set."""
    return set_api_client.save_expression_set_v1(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": set_name,
            "data": set_data,
        },
    )[0]


@pytest.fixture(scope="module")
def expression_set(
    expression_refs: list[str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> dict[str, Any]:
    """A set with name, description, and items populated."""
    set_name = "test_expression_set"
    set_description = "test_expressions"
    set_items = [{"label": "some_label", "ref": ref} for ref in expression_refs]
    set_data = {
        "description": set_description,
        "items": set_items,
    }

    result = save_expression_set(set_api_client, context, ws_id, set_name, set_data)

    return {
        "obj": result,
        "set_name": set_name,
        "set_type": API_CLASS.set_type(),
        "set_description": set_description,
        "n_items": len(expression_refs),
        "second_set_item": set_items[1],
    }


def test_save_expression_set(
    expression_set: dict[str, Any],
) -> None:
    check_save_set_output(**expression_set)


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


@pytest.mark.parametrize(
    "ref_args",
    [
        pytest.param("__SET_REF__", id="set_ref"),
        pytest.param("__WS_NAME__SET_NAME__", id="ws_name_set_name"),
    ],
)
@pytest.mark.parametrize(
    "get_method_args",
    [
        pytest.param({}, id="empty"),
        pytest.param({INC_ITEM_INFO: 1}, id="inc_item_info"),
        pytest.param(
            {INC_ITEM_REF_PATHS: 1},
            id="inc_ref_path",
        ),
        pytest.param(
            {
                INC_ITEM_INFO: 1,
                INC_ITEM_REF_PATHS: 1,
            },
            id="inc_item_info_ref_path",
        ),
        pytest.param(
            {INC_ITEM_INFO: 1, INC_ITEM_REF_PATHS: 1, REF_PATH_TO_SET: ["YES"]},
            id="inc_item_info_ref_path_w_ref_path",
        ),
        pytest.param(
            {
                INC_ITEM_INFO: 0,
                INC_ITEM_REF_PATHS: 0,
            },
            id="no_incs",
        ),
    ],
)
def test_get_expression_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_name: str,
    expression_set: dict[str, Any],
    ref_args: str,
    get_method_args: dict[str, str | int],
) -> None:
    check_get_set(
        set_to_get=expression_set,
        set_type=SET_TYPE,
        set_api_client=set_api_client,
        context=context,
        ws_name=ws_name,
        ref_args=ref_args,
        get_method_args=get_method_args,
    )


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
