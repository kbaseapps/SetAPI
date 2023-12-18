"""General save and get tests of the SetAPI.

See save_set_error_test.py and get_set_error_test.py for error handling tests.
"""
from test.common_test import check_get_set, check_get_set_output, check_save_set_output
from test.conftest import SET_FIXTURE_MAP
from typing import Any

import pytest
from _pytest.fixtures import FixtureRequest
from SetAPI.generic.constants import INC_ITEM_INFO, INC_ITEM_REF_PATHS, REF_PATH_TO_SET
from SetAPI.SetAPIImpl import SetAPI


@pytest.mark.parametrize(
    ("ws_id", "data_fixture"),
    [("default_ws_id", data_fixture) for data_fixture in SET_FIXTURE_MAP],
    indirect=["ws_id", "data_fixture"],
)
def test_save_set(ws_id: int, data_fixture: dict[str, Any]) -> None:
    """Test that saving a set produces the expected output.

    This saves sets in the default workspace (default_ws_id) and uses the
    fixtures corresponding to the keys in the SET_FIXTURE_MAP mapping.
    See test/conftest.py for SET_FIXTURE_MAP.

    :param ws_id: workspace ID of the workspace that the sets are saved in
    :type ws_id: int
    :param data_fixture: name of the data fixture to use in the test
    :type data_fixture: dict[str, Any]
    """
    check_save_set_output(**data_fixture)


@pytest.mark.parametrize("ws_id", ["default_ws_id"], indirect=["ws_id"])
@pytest.mark.parametrize("set_name", list(SET_FIXTURE_MAP))
def test_get_set_all_set_types(
    request: FixtureRequest,
    set_name: str,
    set_api_client: SetAPI,
    context: dict[str, str | list],
    default_ws_name: str,
    ws_id: int,
) -> None:
    """Test getting a set from the default workspace.

    This fetches sets in the default workspace (default_ws_id) and uses the
    fixtures corresponding to the keys in the SET_FIXTURE_MAP mapping.
    See test/conftest.py for SET_FIXTURE_MAP; it includes all the set types
    that have a `get_***_set` method in the SetAPIImpl file.

    These tests have "include_item_info" and "include_set_item_ref_paths"
    both set to be true, and use the KBase UPA as input.

    See below for variations in these parameters.

    """
    # Retrieve the fixture corresponding to set_name
    set_fixture = request.getfixturevalue(set_name)

    # Retrieve a value from the SET_FIXTURE_MAP
    set_item_name = SET_FIXTURE_MAP[set_name]["set_item_name"]

    check_get_set(
        set_to_get=set_fixture,
        set_item_name=set_item_name,
        set_api_client=set_api_client,
        context=context,
        ws_name=default_ws_name,
        ref_args="__SET_REF__",
        get_method_args={INC_ITEM_INFO: 1, INC_ITEM_REF_PATHS: 1},
    )


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
@pytest.mark.parametrize(
    "inc_item_info", [pytest.param(val, id=f"iii={val}") for val in STANDARD_VALUES]
)
@pytest.mark.parametrize(
    "inc_item_ref_paths",
    [pytest.param(val, id=f"iirp={val}") for val in STANDARD_VALUES],
)
@pytest.mark.parametrize(
    "ref_path_to_set_present",
    [pytest.param(val, id=f"rp2s={val}") for val in STANDARD_VALUES],
)
def test_get_set_all_params(
    set_api_client: SetAPI,
    context: dict[str, Any],
    default_ws_name: str,
    ref_args: str,
    random_fixture: dict[str, Any],
    inc_item_info: int | None,
    inc_item_ref_paths: int | None,
    ref_path_to_set_present: int | None,
    ws_id: int,
) -> None:
    """Test set retrieval for with a variety of parameter configurations.

    This uses `random_fixture` to pick one of the set types and run through the different combinations of
    parameters that can be used for a `get_set_v1` query.
    """
    set_ref = random_fixture["obj"]["set_ref"]

    ref_path_to_set = None
    if ref_path_to_set_present is not None:
        ref_path_to_set = [set_ref] if ref_path_to_set_present else []

    ref = (
        set_ref
        if ref_args == "__SET_REF__"
        else f"{default_ws_name}/{random_fixture['set_name']}"
    )

    fetched_set = set_api_client.get_set_v1(
        context,
        {
            "ref": ref,
            REF_PATH_TO_SET: ref_path_to_set,
            INC_ITEM_INFO: bool(inc_item_info),
            INC_ITEM_REF_PATHS: bool(inc_item_ref_paths),
        },
    )

    args_to_check_get_set_output = {
        **{arg: random_fixture[arg] for arg in random_fixture if arg != "obj"},
        "include_item_info": inc_item_info,
        "include_set_item_ref_paths": inc_item_ref_paths,
        "ref_path_to_set": ref_path_to_set,
        "obj": fetched_set[0],
        "ref": ref,
    }
    check_get_set_output(**args_to_check_get_set_output)
