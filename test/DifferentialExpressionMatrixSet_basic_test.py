"""Basic DifferentialExpressionMatrixSet tests."""
from test.common_test import (
    check_get_set,
    check_save_set_mismatched_genomes,
    check_save_set_output,
)
from typing import Any

import pytest
from SetAPI.differentialexpressionmatrix.DifferentialExpressionMatrixSetInterfaceV1 import (
    DifferentialExpressionMatrixSetInterfaceV1,
)
from SetAPI.generic.constants import INC_ITEM_INFO, INC_ITEM_REF_PATHS, REF_PATH_TO_SET
from SetAPI.SetAPIImpl import SetAPI
from SetAPI.util import info_to_ref

API_CLASS = DifferentialExpressionMatrixSetInterfaceV1
SET_TYPE = "differential_expression_matrix"


def save_diff_expr_matrix_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    set_name: str,
    set_data: dict[str, Any],
) -> dict[str, Any]:
    """Given a set_name and set_data, save an assembly set."""
    return set_api_client.save_differential_expression_matrix_set_v1(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": set_name,
            "data": set_data,
        },
    )[0]


@pytest.fixture(scope="module")
def differential_expression_matrix_with_genome_set(
    diff_exp_matrix_genome_refs: list[str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> dict[str, Any]:
    """A set with name, description, and items populated."""
    set_name = "test_diff_expr_matrix_with_genome_set"
    set_description = "test_diff_expr_matrices"
    set_items = [
        {"label": "some_label", "ref": ref} for ref in diff_exp_matrix_genome_refs
    ]
    set_data = {
        "description": set_description,
        "items": set_items,
    }

    result = save_diff_expr_matrix_set(
        set_api_client, context, ws_id, set_name, set_data
    )

    return {
        "obj": result,
        "set_name": set_name,
        "set_type": API_CLASS.set_type(),
        "set_description": set_description,
        "n_items": len(diff_exp_matrix_genome_refs),
        "second_set_item": set_items[1],
    }


@pytest.fixture(scope="module")
def differential_expression_matrix_no_genome_set(
    diff_exp_matrix_no_genome_refs: list[str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> dict[str, Any]:
    """A set with name, description, and items populated."""
    set_name = "test_diff_expr_matrix_no_genome_set"
    set_description = "test_diff_expr_matrices"
    set_items = [
        {"label": "some_label", "ref": ref} for ref in diff_exp_matrix_no_genome_refs
    ]
    set_data = {
        "description": set_description,
        "items": set_items,
    }

    result = save_diff_expr_matrix_set(
        set_api_client, context, ws_id, set_name, set_data
    )

    return {
        "obj": result,
        "set_name": set_name,
        "set_type": API_CLASS.set_type(),
        "set_description": set_description,
        "n_items": len(diff_exp_matrix_no_genome_refs),
        "second_set_item": set_items[1],
    }


def test_save_diff_exp_matrix_set(
    differential_expression_matrix_with_genome_set,
    differential_expression_matrix_no_genome_set,
) -> None:
    for saved_set in [
        differential_expression_matrix_with_genome_set,
        differential_expression_matrix_no_genome_set,
    ]:
        check_save_set_output(**saved_set)


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
def test_get_diff_exp_matrix_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_name: str,
    ref_args: str,
    get_method_args: dict[str, str | int],
    differential_expression_matrix_with_genome_set,
    differential_expression_matrix_no_genome_set,
) -> None:
    for saved_set in [
        differential_expression_matrix_with_genome_set,
        differential_expression_matrix_no_genome_set,
    ]:
        check_get_set(
            set_to_get=saved_set,
            set_type=SET_TYPE,
            set_api_client=set_api_client,
            context=context,
            ws_name=ws_name,
            ref_args=ref_args,
            get_method_args=get_method_args,
        )


def test_save_diff_exp_matrix_set_mismatched_genomes(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    diff_exp_matrix_mismatched_genome_refs: list[str],
) -> None:
    check_save_set_mismatched_genomes(
        context=context,
        set_api_client=set_api_client,
        set_type=SET_TYPE,
        set_item_refs=diff_exp_matrix_mismatched_genome_refs,
        set_items_type=API_CLASS.set_items_type(),
    )
