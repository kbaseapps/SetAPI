"""Basic ReadsAlignmentSet tests."""
from test.common_test import (
    check_get_set,
    check_get_set_output,
    check_save_set_mismatched_genomes,
    check_save_set_output,
)
from typing import Any

import pytest
from SetAPI.generic.constants import INC_ITEM_INFO, INC_ITEM_REF_PATHS, REF_PATH_TO_SET
from SetAPI.readsalignment.ReadsAlignmentSetInterfaceV1 import (
    ReadsAlignmentSetInterfaceV1,
)
from SetAPI.SetAPIImpl import SetAPI

API_CLASS = ReadsAlignmentSetInterfaceV1
SET_TYPE = "reads_alignment"


def save_reads_alignment_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    set_name: str,
    set_data: dict[str, Any],
) -> dict[str, Any]:
    """Given a set name and set data, save a reads alignment set."""
    return set_api_client.save_reads_alignment_set_v1(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": set_name,
            "data": set_data,
        },
    )[0]


@pytest.fixture(scope="module")
def reads_alignment_set(
    alignment_refs: list[str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> dict[str, int | str | dict[str, Any]]:
    set_name = "test_reads_alignment_set"
    set_description = "test_reads_alignments"
    set_items = [{"label": "some_label", "ref": ref} for ref in alignment_refs]
    set_data = {
        "description": set_description,
        "items": set_items,
    }

    result = save_reads_alignment_set(
        set_api_client, context, ws_id, set_name, set_data
    )

    return {
        "obj": result,
        "set_name": set_name,
        "set_type": API_CLASS.set_type(),
        "set_description": set_description,
        "n_items": len(alignment_refs),
        "second_set_item": set_items[1],
    }


def test_save_reads_alignment_set(
    reads_alignment_set: dict[str, Any],
) -> None:
    check_save_set_output(**reads_alignment_set)


def test_save_reads_alignment_set_mismatched_genomes(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    alignment_mismatched_genome_refs: list[str],
) -> None:
    check_save_set_mismatched_genomes(
        context=context,
        set_api_client=set_api_client,
        set_type=SET_TYPE,
        set_item_refs=alignment_mismatched_genome_refs,
        set_items_type=API_CLASS.set_items_type(),
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
            {INC_ITEM_INFO: 1, INC_ITEM_REF_PATHS: 1, REF_PATH_TO_SET: []},
            id="inc_item_info_ref_path_empty_ref_path",
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
def test_get_reads_alignment_set(
    reads_alignment_set: dict[str, Any],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_name: str,
    ref_args: str,
    get_method_args: dict[str, str | int],
) -> None:
    check_get_set(
        set_to_get=reads_alignment_set,
        set_type=SET_TYPE,
        set_api_client=set_api_client,
        context=context,
        ws_name=ws_name,
        ref_args=ref_args,
        get_method_args=get_method_args,
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
    ws_name: str,
    reads_refs: list[str],
    ref_args: str,
    get_method_args: dict[str, str | int],
) -> None:
    params = {}
    for param in [INC_ITEM_INFO, INC_ITEM_REF_PATHS, REF_PATH_TO_SET]:
        if param in get_method_args:
            params[param] = get_method_args[param]

    n_items = len(reads_refs)
    idx = -1
    for ref in rnaseq_alignment_sets:
        idx += 1
        set_name = f"fake_rnaseq_alignment_set_{idx}"
        if ref_args == "__SET_REF__":
            params["ref"] = ref
        else:
            params["ref"] = f"{ws_name}/{set_name}"

        if params.get(REF_PATH_TO_SET, []) != []:
            # add in some values for the REF_PATH_TO_SET
            params[REF_PATH_TO_SET] = [
                rnaseq_alignment_sets[idx],
            ]

        fetched_set = set_api_client.get_reads_alignment_set_v1(context, params)[0]

        # set items are not returned in order so can't check the second set item
        check_get_set_output(
            fetched_set,
            set_name=set_name,
            set_type="KBaseRNASeq.RNASeqAlignmentSet",
            set_description="",
            n_items=n_items,
            **params,
            is_fake_set=True,
        )
