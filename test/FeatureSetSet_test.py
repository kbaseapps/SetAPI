"""Basic FeatureSet tests."""
from test.common_test import check_save_set_output
from typing import Any

import pytest
from SetAPI.featureset.FeatureSetSetInterfaceV1 import FeatureSetSetInterfaceV1
from SetAPI.generic.constants import INC_ITEM_INFO, INC_ITEM_REF_PATHS
from SetAPI.SetAPIImpl import SetAPI
from SetAPI.util import info_to_ref

API_CLASS = FeatureSetSetInterfaceV1


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


def test_get_feature_set_set(
    featureset_refs: list,
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> None:
    set_name = "test_featureset_set2"
    set_items = [{"label": "wt", "ref": ref} for ref in featureset_refs]
    n_items = len(featureset_refs)
    featureset_set = {"description": "test_alignments", "items": set_items}
    featureset_set_ref = set_api_client.save_feature_set_set_v1(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": set_name,
            "data": featureset_set,
        },
    )[0]["set_ref"]

    fetched_set = set_api_client.get_feature_set_set_v1(
        context, {"ref": featureset_set_ref, INC_ITEM_INFO: 0}
    )[0]
    assert fetched_set is not None
    assert "data" in fetched_set
    assert "info" in fetched_set
    assert len(fetched_set["data"]["items"]) == n_items
    assert featureset_set_ref == info_to_ref(fetched_set["info"])
    for item in fetched_set["data"]["items"]:
        assert "info" not in item
        assert "ref_path" not in item
        assert "ref" in item
        assert "label" in item

    fetched_set_with_info = set_api_client.get_feature_set_set_v1(
        context,
        {
            "ref": featureset_set_ref,
            INC_ITEM_INFO: 1,
            INC_ITEM_REF_PATHS: 1,
        },
    )[0]
    assert fetched_set_with_info is not None
    assert "data" in fetched_set_with_info
    for item in fetched_set_with_info["data"]["items"]:
        assert "info" in item
        assert "ref" in item
        assert "label" in item
        assert "ref_path" in item
        assert item["ref_path"] == featureset_set_ref + ";" + item["ref"]
