"""Basic FeatureSet tests."""
from test.common_test import check_get_set, check_save_set_output
from typing import Any

import pytest
from SetAPI.featureset.FeatureSetSetInterfaceV1 import FeatureSetSetInterfaceV1
from SetAPI.generic.constants import INC_ITEM_INFO, INC_ITEM_REF_PATHS, REF_PATH_TO_SET
from SetAPI.SetAPIImpl import SetAPI

API_CLASS = FeatureSetSetInterfaceV1
SET_TYPE = "feature_set"


def save_featureset_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    set_name: str,
    set_data: dict[str, Any],
) -> dict[str, Any]:
    """Given a set_name and set_data, save a featureset set."""
    return set_api_client.save_feature_set_set_v1(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": set_name,
            "data": set_data,
        },
    )[0]


@pytest.fixture(scope="module")
def featureset_set(
    featureset_refs: list[str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> dict[str, Any]:
    """A set with name, description, and items populated."""
    set_name = "test_featureset_set"
    set_description = "test_assemblies"
    set_items = [{"label": "some_label", "ref": ref} for ref in featureset_refs]
    set_data = {
        "description": set_description,
        "items": set_items,
    }

    result = save_featureset_set(set_api_client, context, ws_id, set_name, set_data)

    return {
        "obj": result,
        "set_name": set_name,
        "set_type": API_CLASS.set_type(),
        "set_description": set_description,
        "n_items": len(featureset_refs),
        "second_set_item": set_items[1],
    }


@pytest.fixture(scope="module")
def empty_featureset_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> dict[str, Any]:
    """A set with no description and an empty items list."""
    set_name = "empty_featureset_set"
    # omit the set description and make the set items an empty list
    set_data = {
        "items": [],
    }

    result = save_featureset_set(set_api_client, context, ws_id, set_name, set_data)

    return {
        "obj": result,
        "set_name": set_name,
        "set_type": API_CLASS.set_type(),
        # the class fills in the missing description field
        "set_description": "",
        "n_items": 0,
    }


def test_save_feature_set_set(featureset_set: dict[str, Any]) -> None:
    check_save_set_output(**featureset_set)


def test_save_featureset_set_no_featuresets(
    empty_featureset_set: dict[str, Any]
) -> None:
    check_save_set_output(**empty_featureset_set)


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
def test_get_feature_set_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_name: str,
    ref_args: str,
    get_method_args: dict[str, str | int],
    featureset_set: dict[str, Any],
    empty_featureset_set: dict[str, Any],
) -> None:
    for saved_set in [featureset_set, empty_featureset_set]:
        check_get_set(
            set_to_get=saved_set,
            set_type=SET_TYPE,
            set_api_client=set_api_client,
            context=context,
            ws_name=ws_name,
            ref_args=ref_args,
            get_method_args=get_method_args,
        )
