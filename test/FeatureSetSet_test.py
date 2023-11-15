"""Basic FeatureSet tests."""
from test.util import info_to_ref, make_fake_feature_set
from typing import Any

import pytest
from installed_clients.baseclient import ServerError
from SetAPI.SetAPIImpl import SetAPI

N_FEATURESET_REFS = 3


@pytest.fixture(scope="module")
def featureset_refs(
    genome_refs: list[str], ws_name: str, clients: dict[str, Any]
) -> list:
    # Make some fake feature sets
    return [
        make_fake_feature_set(
            f"feature_set_{i}", genome_refs[0], ws_name, clients["ws"]
        )
        for i in range(N_FEATURESET_REFS)
    ]


def test_save_feature_set_set(
    featureset_refs: list,
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_name: str,
) -> None:
    set_name = "test_feature_set_set"
    set_items = [{"label": "foo", "ref": ref} for ref in featureset_refs]
    expression_set = {"description": "test_expressions", "items": set_items}
    result = set_api_client.save_feature_set_set_v1(
        context,
        {
            "workspace": ws_name,
            "output_object_name": set_name,
            "data": expression_set,
        },
    )[0]
    assert result is not None
    assert "set_ref" in result
    assert "set_info" in result
    assert result["set_ref"] == info_to_ref(result["set_info"])
    assert result["set_info"][1] == set_name
    assert "KBaseSets.FeatureSetSet" in result["set_info"][2]


def test_save_feature_set_set_no_data(
    set_api_client: SetAPI, context: dict[str, str | list], ws_name: str
) -> None:
    with pytest.raises(
        ValueError, match='"data" parameter field required to save a FeatureSetSet'
    ):
        set_api_client.save_feature_set_set_v1(
            context,
            {
                "workspace": ws_name,
                "output_object_name": "foo",
                "data": None,
            },
        )


@pytest.mark.skip("Currently allow empty FeatureSetSets")
def test_save_feature_set_set_empty(
    set_api_client: SetAPI, context: dict[str, str | list], ws_name: str
) -> None:
    with pytest.raises(
        ValueError,
        match="At least one FeatureSet is required to save a FeatureSetSet.",
    ):
        set_api_client.save_feature_set_set_v1(
            context,
            {
                "workspace": ws_name,
                "output_object_name": "foo",
                "data": {"description": "empty_set", "items": []},
            },
        )


def test_get_feature_set_set(
    featureset_refs: list, set_api_client: SetAPI, context: dict[str, str | list], ws_name: str
) -> None:
    set_name = "test_featureset_set2"
    set_items = [{"label": "wt", "ref": ref} for ref in featureset_refs]
    featureset_set = {"description": "test_alignments", "items": set_items}
    featureset_set_ref = set_api_client.save_feature_set_set_v1(
        context,
        {
            "workspace": ws_name,
            "output_object_name": set_name,
            "data": featureset_set,
        },
    )[0]["set_ref"]

    fetched_set = set_api_client.get_feature_set_set_v1(
        context, {"ref": featureset_set_ref, "include_item_info": 0}
    )[0]
    assert fetched_set is not None
    assert "data" in fetched_set
    assert "info" in fetched_set
    assert len(fetched_set["data"]["items"]) == N_FEATURESET_REFS
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
            "include_item_info": 1,
            "include_set_item_ref_paths": 1,
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


def test_get_feature_set_set_bad_ref(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    with pytest.raises(
        ValueError, match='"ref" parameter must be a valid workspace reference'
    ):
        set_api_client.get_feature_set_set_v1(context, {"ref": "not_a_ref"})


def test_get_feature_set_set_bad_path(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    with pytest.raises(
        ServerError, match="JSONRPCError: -32500. Object 2 cannot be accessed:"
    ):
        set_api_client.get_feature_set_set_v1(
            context, {"ref": "1/2/3", "path_to_set": ["foo", "bar"]}
        )


def test_get_feature_set_set_no_ref(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    with pytest.raises(
        ValueError,
        match='"ref" parameter field specifiying the FeatureSet set is required',
    ):
        set_api_client.get_feature_set_set_v1(context, {"ref": None})
