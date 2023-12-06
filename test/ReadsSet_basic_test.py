"""Basic ReadsSet tests."""
from test.common_test import check_get_set, check_save_set_output
from typing import Any

import pytest
from SetAPI.generic.constants import INC_ITEM_INFO, INC_ITEM_REF_PATHS, REF_PATH_TO_SET
from SetAPI.reads.ReadsSetInterfaceV1 import (
    ReadsSetInterfaceV1,
)
from SetAPI.SetAPIImpl import SetAPI

API_CLASS = ReadsSetInterfaceV1
SET_TYPE = "reads"


def save_reads_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    set_name: str,
    set_data: dict[str, Any],
) -> dict[str, Any]:
    """Given a set_name and set_data, save a reads set."""
    return set_api_client.save_reads_set_v1(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": set_name,
            "data": set_data,
        },
    )[0]


@pytest.fixture(scope="module")
def reads_set(
    reads_refs: list[str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> dict[str, Any]:
    """A set with name, description, and items populated."""
    set_name = "test_reads_set"
    set_description = "test_reads"
    set_items = [{"label": "some_label", "ref": ref} for ref in reads_refs]
    set_data = {
        "description": set_description,
        "items": set_items,
    }

    result = save_reads_set(set_api_client, context, ws_id, set_name, set_data)

    return {
        "obj": result,
        "set_name": set_name,
        "set_type": API_CLASS.set_type(),
        "set_description": set_description,
        "n_items": len(reads_refs),
        "second_set_item": set_items[1],
    }


@pytest.fixture(scope="module")
def empty_reads_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> dict[str, Any]:
    """A set with no description and an empty items list."""
    set_name = "empty_reads_set"
    # omit the set description and make the set items an empty list
    set_data = {
        "items": [],
    }

    result = save_reads_set(set_api_client, context, ws_id, set_name, set_data)

    return {
        "obj": result,
        "set_name": set_name,
        "set_type": API_CLASS.set_type(),
        # the class fills in the missing description field
        "set_description": "",
        "n_items": 0,
    }


def test_save_reads_set(
    reads_set: dict[str, Any],
) -> None:
    check_save_set_output(**reads_set)


# it's possible to create an empty reads set, so let's test it!
def test_save_reads_set_no_reads(
    empty_reads_set: dict[str, Any],
) -> None:
    check_save_set_output(**empty_reads_set)


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
def test_get_genome_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_name: str,
    ref_args: str,
    get_method_args: dict[str, str | int],
    reads_set: dict[str, Any],
    empty_reads_set: dict[str, Any],
) -> None:
    for saved_set in [reads_set, empty_reads_set]:
        check_get_set(
            set_to_get=saved_set,
            set_type=SET_TYPE,
            set_api_client=set_api_client,
            context=context,
            ws_name=ws_name,
            ref_args=ref_args,
            get_method_args=get_method_args,
        )
