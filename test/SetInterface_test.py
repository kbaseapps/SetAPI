"""Generic SetInterface tests."""
from test.common_test import check_get_set_output
from typing import Any

import pytest
from SetAPI.generic.SetInterfaceV1 import SetInterfaceV1

STANDARD_VALUES = [None, 0, 1]


@pytest.mark.parametrize(
    "ws_id",
    ["default_ws_id"],
    indirect=["ws_id"],
)
@pytest.mark.parametrize(
    "ref_args",
    [
        pytest.param("__SET_REF__", id="set_ref"),
        pytest.param("__WS_NAME__SET_NAME__", id="ws_name_set_name"),
    ],
)
@pytest.mark.parametrize("inc_item_info", STANDARD_VALUES)
@pytest.mark.parametrize("inc_item_ref_paths", STANDARD_VALUES)
@pytest.mark.parametrize("ref_path_to_set_present", STANDARD_VALUES)
def test_get_set(
    clients: dict[str, Any],
    default_ws_name: str,
    ref_args: str,
    ws_id: int,
    random_fixture: dict[str, Any],
    inc_item_info: int | None,
    inc_item_ref_paths: int | None,
    ref_path_to_set_present: int | None,
) -> None:
    """Test set retrieval for all the boring normal sets."""

    set_ref = random_fixture["obj"]["set_ref"]

    ref_path_to_set = None
    if ref_path_to_set_present is not None:
        ref_path_to_set = [set_ref] if ref_path_to_set_present else []

    ref = (
        set_ref
        if ref_args == "__SET_REF__"
        else f"{default_ws_name}/{random_fixture['set_name']}"
    )

    set_interface = SetInterfaceV1(clients["ws"])
    fetched_set = set_interface.get_set(
        ref, bool(inc_item_info), ref_path_to_set, bool(inc_item_ref_paths)
    )

    args_to_check_get_set_output = {
        **{arg: random_fixture[arg] for arg in random_fixture if arg != "obj"},
        "include_item_info": inc_item_info,
        "include_set_item_ref_paths": inc_item_ref_paths,
        "ref_path_to_set": ref_path_to_set,
        "obj": fetched_set,
        "ref": ref,
    }
    check_get_set_output(**args_to_check_get_set_output)
