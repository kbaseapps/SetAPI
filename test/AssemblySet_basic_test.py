"""Basic tests for the AssemblySet class."""
from test.common_test import (
    check_get_set_output,
    check_save_set_output,
)
from typing import Any

import pytest
from SetAPI.assembly.AssemblySetInterfaceV1 import AssemblySetInterfaceV1
from SetAPI.generic.constants import INC_ITEM_INFO, INC_ITEM_REF_PATHS, REF_PATH_TO_SET
from SetAPI.SetAPIImpl import SetAPI

API_CLASS = AssemblySetInterfaceV1
SET_TYPE = "assembly"


def save_assembly_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    set_name: str,
    set_data: dict[str, Any],
) -> dict[str, Any]:
    """Given a set_name and set_data, save an assembly set."""
    return set_api_client.save_assembly_set_v1(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": set_name,
            "data": set_data,
        },
    )[0]


@pytest.fixture(scope="module")
def assembly_set(
    assembly_refs: list[str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> dict[str, int | str | dict[str, Any]]:
    """A set with name, description, and items populated."""
    set_name = "test_assembly_set"
    set_description = "test_assemblies"
    set_items = [{"label": "some_label", "ref": ref} for ref in assembly_refs]
    set_data = {
        "description": set_description,
        "items": set_items,
    }

    result = save_assembly_set(set_api_client, context, ws_id, set_name, set_data)

    return {
        "obj": result,
        "set_name": set_name,
        "set_type": API_CLASS.set_type(),
        "set_description": set_description,
        "n_items": len(assembly_refs),
        "second_set_item": set_items[1],
    }


@pytest.fixture(scope="module")
def empty_assembly_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> dict[str, int | str | dict[str, Any]]:
    """A set with no description and an empty items list."""
    set_name = "empty_assembly_set"
    # omit the set description and make the set items an empty list
    set_data = {
        "items": [],
    }

    result = save_assembly_set(set_api_client, context, ws_id, set_name, set_data)

    return {
        "obj": result,
        "set_name": set_name,
        "set_type": API_CLASS.set_type(),
        # the class fills in the missing description field
        "set_description": "",
        "n_items": 0,
    }


def test_save_assembly_set(
    assembly_set: dict[str, int | str | dict[str, Any]],
) -> None:
    check_save_set_output(**assembly_set)


# it's possible to create an empty assembly set, so let's test it!
def test_save_assembly_set_no_assemblies(
    empty_assembly_set: dict[str, Any],
) -> None:
    check_save_set_output(**empty_assembly_set)


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
def test_get_assembly_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_name: str,
    assembly_set: dict[str, Any],
    ref_args: str,
    get_method_args: dict[str, str | int],
) -> None:
    set_ref = assembly_set["obj"]["set_ref"]
    params = {}
    if ref_args == "__SET_REF__":
        params["ref"] = set_ref
    else:
        params["ref"] = f"{ws_name}/{assembly_set['set_name']}"

    for param in [INC_ITEM_INFO, INC_ITEM_REF_PATHS, REF_PATH_TO_SET]:
        if param in get_method_args:
            params[param] = get_method_args[param]

    if params.get(REF_PATH_TO_SET, []) != []:
        # add in a value for the REF_PATH_TO_SET
        params[REF_PATH_TO_SET] = [set_ref]

    fetched_set = set_api_client.get_assembly_set_v1(context, params)[0]

    args_to_check_get_set_output = {
        **{arg: assembly_set[arg] for arg in assembly_set if arg != "obj"},
        **params,
        "obj": fetched_set,
    }
    check_get_set_output(**args_to_check_get_set_output)
