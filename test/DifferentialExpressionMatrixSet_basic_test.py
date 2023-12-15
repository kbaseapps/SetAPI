"""Basic DifferentialExpressionMatrixSet tests."""
from test.common_test import (
    check_get_set,
    check_save_set_output,
)
from typing import Any

import pytest
from SetAPI.generic.constants import (
    DIFFERENTIAL_EXPRESSION_MATRIX,
    DIFFERENTIAL_EXPRESSION_MATRIX_SET,
    INC_ITEM_INFO,
    INC_ITEM_REF_PATHS,
    REF_PATH_TO_SET,
)
from SetAPI.SetAPIImpl import SetAPI

SET_TYPE = DIFFERENTIAL_EXPRESSION_MATRIX_SET
SET_ITEM_NAME = DIFFERENTIAL_EXPRESSION_MATRIX


@pytest.mark.parametrize("ws_id", ["default_ws_id"], indirect=True)
def test_save_diff_exp_matrix_set(
    differential_expression_matrix_with_genome_set: dict[str, Any],
    differential_expression_matrix_no_genome_set: dict[str, Any],
) -> None:
    for saved_set in [
        differential_expression_matrix_with_genome_set,
        differential_expression_matrix_no_genome_set,
    ]:
        check_save_set_output(**saved_set)


@pytest.mark.parametrize("ws_id", ["default_ws_id"], indirect=True)
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
    default_ws_name: str,
    ref_args: str,
    get_method_args: dict[str, str | int],
    differential_expression_matrix_with_genome_set: dict[str, Any],
    differential_expression_matrix_no_genome_set: dict[str, Any],
) -> None:
    for saved_set in [
        differential_expression_matrix_with_genome_set,
        differential_expression_matrix_no_genome_set,
    ]:
        check_get_set(
            set_to_get=saved_set,
            set_item_name=SET_ITEM_NAME,
            set_api_client=set_api_client,
            context=context,
            ws_name=default_ws_name,
            ref_args=ref_args,
            get_method_args=get_method_args,
        )
