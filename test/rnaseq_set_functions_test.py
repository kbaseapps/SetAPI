"""Tests for requests that get RNASeq<whatever>Sets."""
from test.common_test import (
    check_get_set_output,
    check_save_set_output,
    is_info_object,
    param_wrangle,
)
from test.util import log_this, save_kbase_search_set
from typing import Any

import pytest
from SetAPI.generic.constants import (
    GENOME_SEARCH_SET,
    INC_ITEM_INFO,
    INC_ITEM_REF_PATHS,
    REF_PATH_TO_SET,
)
from SetAPI.SetAPIImpl import SetAPI


@pytest.mark.parametrize("ws_id", ["default_ws_id"], indirect=True)
def test_save_kbasesearch_genome(
    kbase_search_genome_set: dict[str, Any],
    genome_refs: list[str],
    set_api_client: SetAPI,
    context: dict[str, Any],
) -> None:
    import json

    print(json.dumps(kbase_search_genome_set, indent=2, sort_keys=True))
    res = kbase_search_genome_set["obj"]
    check_save_set_output(
        kbase_search_genome_set["obj"],
        set_name=kbase_search_genome_set["set_name"],
        kbase_set_type=GENOME_SEARCH_SET,
    )

    # test get of that object
    d1 = set_api_client.get_genome_set_v1(context, {"ref": res["set_ref"]})[0]
    print("d1:")
    print(json.dumps(d1, indent=2, sort_keys=True))

    assert "data" in d1
    assert "info" in d1
    is_info_object(
        d1["info"],
        kbase_search_genome_set["set_name"],
        kbase_search_genome_set["kbase_set_type"],
    )
    assert d1["data"]["description"] == kbase_search_genome_set["set_description"]
    assert len(d1["data"]["elements"]) == kbase_search_genome_set["n_items"]

    elements = d1["data"]["elements"]
    for ref in genome_refs:
        assert ref in elements

    genome_2 = elements.get(genome_refs[1])
    assert "ref" in genome_2
    assert genome_2.get("ref") == genome_refs[1]
    assert genome_2["metadata"] == {"some": "thing", "or": "other"}


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
    alignment_refs: list[str],
    get_method_args: dict[str, str | int],
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
        n_items=len(alignment_refs),
        second_set_item=None,
        **params,
    )
