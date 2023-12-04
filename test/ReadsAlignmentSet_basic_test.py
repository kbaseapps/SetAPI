"""Basic ReadsAlignmentSet tests."""
from test.common_checks import (
    check_get_set_bad_path,
    check_get_set_bad_ref,
    check_get_set_no_ref,
    check_get_set_output,
    check_save_set_mismatched_genomes,
    check_save_set_no_data,
    check_save_set_no_items_list,
    check_save_set_no_objects,
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


@pytest.fixture(scope="module")
def alignment_set(
    alignment_refs: list[str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> dict[str, int | str | dict[str, Any]]:
    set_name = "test_alignment_set"
    set_description = "test_alignments"
    set_items = [{"label": "some_label", "ref": ref} for ref in alignment_refs]
    set_data = {
        "description": set_description,
        "items": set_items,
    }

    result = set_api_client.save_reads_alignment_set_v1(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": set_name,
            "data": set_data,
        },
    )[0]
    return {
        "obj": result,
        "set_name": set_name,
        "set_type": API_CLASS.set_type(),
        "set_description": set_description,
        "n_items": len(alignment_refs),
        "second_set_item": set_items[1],
    }


def test_save_reads_alignment_set(
    alignment_set,
) -> None:
    check_save_set_output(**alignment_set)


def test_save_reads_alignment_set_mismatched_genomes(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    alignment_mismatched_genome_refs: list[str],
) -> None:
    alignment_set_items = [
        {"label": "some_label", "ref": ref} for ref in alignment_mismatched_genome_refs
    ]
    check_save_set_mismatched_genomes(
        context=context,
        save_method=set_api_client.save_reads_alignment_set_v1,
        set_items=alignment_set_items,
        set_items_type=API_CLASS.set_items_type(),
    )


def test_save_reads_alignment_set_no_data(
    set_api_client: SetAPI, context: dict[str, str | list], ws_id: int
) -> None:
    check_save_set_no_data(
        context,
        set_api_client.save_reads_alignment_set_v1,
        API_CLASS.set_items_type(),
    )


def test_save_reads_alignment_set_no_items_list(
    set_api_client: SetAPI, context: dict[str, str | list], ws_id: int
) -> None:
    check_save_set_no_items_list(
        context,
        set_api_client.save_reads_alignment_set_v1,
        API_CLASS.set_items_type(),
    )


def test_save_reads_alignment_set_no_alignments(
    set_api_client: SetAPI, context: dict[str, str | list], ws_id: int
) -> None:
    check_save_set_no_objects(
        context,
        set_api_client.save_reads_alignment_set_v1,
        API_CLASS.set_items_type(),
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
    alignment_set: dict[str, Any],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_name: str,
    ref_args: str,
    get_method_args: dict[str, str | int],
) -> None:
    alignment_set_ref = alignment_set["obj"]["set_ref"]
    params = {}
    if ref_args == "__SET_REF__":
        params["ref"] = alignment_set_ref
    else:
        params["ref"] = f"{ws_name}/{alignment_set['set_name']}"

    for param in [INC_ITEM_INFO, INC_ITEM_REF_PATHS, REF_PATH_TO_SET]:
        if param in get_method_args:
            params[param] = get_method_args[param]

    if params.get(REF_PATH_TO_SET, []) != []:
        # add in a value to check REF_PATH_TO_SET
        params[REF_PATH_TO_SET] = [alignment_set["obj"]["set_ref"]]

    fetched_set = set_api_client.get_reads_alignment_set_v1(context, params)[0]

    args_to_check_get_set_output = {
        **{arg: alignment_set[arg] for arg in alignment_set if arg != "obj"},
        **params,
        "obj": fetched_set,
    }
    check_get_set_output(**args_to_check_get_set_output)


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


def test_get_reads_alignment_set_bad_ref(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    check_get_set_bad_ref(context, set_api_client.get_reads_alignment_set_v1)


def test_get_reads_alignment_set_bad_path(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    check_get_set_bad_path(context, set_api_client.get_reads_alignment_set_v1)


def test_get_reads_alignment_set_no_ref(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    check_get_set_no_ref(
        context, set_api_client.get_reads_alignment_set_v1, API_CLASS.set_items_type()
    )
