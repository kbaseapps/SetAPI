"""Tests for requests that get RNASeq<whatever>Sets."""
from test.common_test import (
    check_get_set_output,
    param_wrangle,
)
from typing import Any

import pytest
from SetAPI.generic.constants import (
    INC_ITEM_INFO,
    INC_ITEM_REF_PATHS,
    REF_PATH_TO_SET,
)
from SetAPI.SetAPIImpl import SetAPI


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
            {INC_ITEM_INFO: 1, INC_ITEM_REF_PATHS: 1, REF_PATH_TO_SET: []},
            id="inc_item_info_ref_path_empty_ref_path",
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
def test_get_rnaseq_alignment_set(
    rnaseq_alignment_sets: list[str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    default_ws_name: str,
    reads_refs: list[str],
    ref_args: str,
    get_method_args: dict[str, str | int],
    ws_id: int,
) -> None:
    n_items = len(reads_refs)
    idx = -1
    for ref in rnaseq_alignment_sets:
        idx += 1
        set_name = f"fake_rnaseq_alignment_set_{idx}"  # from the fixture
        params = param_wrangle(
            ref_args, get_method_args, ref, set_name, default_ws_name
        )
        fetched_set = set_api_client.get_reads_alignment_set_v1(context, params)[0]

        # set items are not returned in order so can't check the second set item
        check_get_set_output(
            fetched_set,
            set_name=set_name,
            kbase_set_type="KBaseRNASeq.RNASeqAlignmentSet",
            set_description="",
            n_items=n_items,
            **params,
        )


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
            {INC_ITEM_INFO: 1, INC_ITEM_REF_PATHS: 1, REF_PATH_TO_SET: []},
            id="inc_item_info_ref_path_empty_ref_path",
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
def test_get_rnaseq_expression_set_ref_path(
    rnaseq_expression_set: str,
    set_api_client: SetAPI,
    context: dict[str, str | list],
    default_ws_name: str,
    ref_args: str,
    reads_alignment_refs: list[str],
    get_method_args: dict[str, str | int],
    ws_id: int,
) -> None:
    params = {}
    set_name = "fake_rnaseq_expression_set"  # from the fixture
    params = param_wrangle(
        ref_args, get_method_args, rnaseq_expression_set, set_name, default_ws_name
    )

    fetched_set = set_api_client.get_expression_set_v1(
        context,
        params,
    )[0]

    check_get_set_output(
        fetched_set,
        set_name=set_name,
        kbase_set_type="KBaseRNASeq.RNASeqExpressionSet",
        set_description="",
        n_items=len(reads_alignment_refs),
        second_set_item=None,
        **params,
    )
