"""Basic ReadsSet tests."""
from test.util import INFO_LENGTH

import pytest
from SetAPI.SetAPIImpl import SetAPI


def test_basic_save_and_get(
    reads_refs: list[str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> None:
    set_name = "set_o_reads"
    set_description = "my first reads"
    n_items_in_set = 3
    # create the set object
    set_data = {
        "description": set_description,
        "items": [
            {"ref": reads_refs[0], "label": "reads1"},
            {"ref": reads_refs[1], "label": "reads2"},
            {"ref": reads_refs[2]},
        ],
    }

    # test a save
    res = set_api_client.save_reads_set_v1(
        context,
        {
            "data": set_data,
            "output_object_name": set_name,
            "workspace_id": ws_id,
        },
    )[0]
    assert "set_ref" in res
    assert "set_info" in res
    assert len(res["set_info"]) == INFO_LENGTH

    assert res["set_info"][1] == set_name
    assert "item_count" in res["set_info"][10]
    assert res["set_info"][10]["item_count"] == str(n_items_in_set)

    # test get of that object
    d1 = set_api_client.get_reads_set_v1(context, {"ref": res["set_ref"]})[0]
    assert "data" in d1
    assert "info" in d1
    assert len(d1["info"]) == INFO_LENGTH
    assert "item_count" in d1["info"][10]
    assert d1["info"][10]["item_count"] == str(n_items_in_set)

    assert d1["data"]["description"] == set_description
    assert len(d1["data"]["items"]) == n_items_in_set

    item2 = d1["data"]["items"][1]
    assert "info" not in item2
    assert "ref" in item2
    assert "label" in item2
    assert item2["label"] == "reads2"
    assert item2["ref"] == reads_refs[1]

    item3 = d1["data"]["items"][2]
    assert "info" not in item3
    assert "ref" in item3
    assert "label" in item3
    assert item3["label"] == ""
    assert item3["ref"] == reads_refs[2]

    # test the call to make sure we get info for each item
    d2 = set_api_client.get_reads_set_v1(
        context,
        {
            "ref": res["set_ref"],
            "include_item_info": 1,
            "include_set_item_ref_paths": 1,
        },
    )[0]
    assert "data" in d2
    assert "info" in d2
    assert len(d2["info"]) == INFO_LENGTH
    assert "item_count" in d2["info"][10]
    assert d2["info"][10]["item_count"] == str(n_items_in_set)

    assert d2["data"]["description"] == set_description
    assert len(d2["data"]["items"]) == n_items_in_set

    item2 = d2["data"]["items"][1]
    assert "info" in item2
    assert len(item2["info"]), INFO_LENGTH
    assert "ref" in item2
    assert item2["ref"] == reads_refs[1]

    assert "ref_path" in item2
    assert item2["ref_path"] == res["set_ref"] + ";" + item2["ref"]


def test_save_and_get_of_empty_set(
    set_api_client: SetAPI, context: dict[str, str | list], ws_id: int
) -> None:
    set_name = "nada_set"
    set_description = "nothing to see here"
    n_items_in_set = 0

    # create the set object
    set_data = {"description": set_description, "items": []}

    # test a save
    res = set_api_client.save_reads_set_v1(
        context,
        {
            "data": set_data,
            "output_object_name": set_name,
            "workspace_id": ws_id,
        },
    )[0]
    assert "set_ref" in res
    assert "set_info" in res
    assert len(res["set_info"]) == INFO_LENGTH

    assert res["set_info"][1] == set_name
    assert "item_count" in res["set_info"][10]
    assert res["set_info"][10]["item_count"] == str(n_items_in_set)

    # test get of that object
    d1 = set_api_client.get_reads_set_v1(context, {"ref": res["set_ref"]})[0]
    assert "data" in d1
    assert "info" in d1
    assert len(d1["info"]) == INFO_LENGTH
    assert "item_count" in d1["info"][10]
    assert d1["info"][10]["item_count"] == str(n_items_in_set)

    assert d1["data"]["description"] == set_description
    assert len(d1["data"]["items"]) == 0

    d2 = set_api_client.get_reads_set_v1(
        context, {"ref": res["set_ref"], "include_item_info": 1}
    )[0]

    assert "data" in d2
    assert "info" in d2
    assert len(d2["info"]) == INFO_LENGTH
    assert "item_count" in d2["info"][10]
    assert d2["info"][10]["item_count"] == str(n_items_in_set)

    assert d2["data"]["description"] == set_description
    assert len(d2["data"]["items"]) == n_items_in_set


def test_get_sampleset_as_readsset(
    sampleset_ref: str,
    set_api_client: SetAPI,
    context: dict[str, str | list],
    reads_refs: list[str],
) -> None:
    param_set = [
        {"ref": sampleset_ref},
        {"ref": sampleset_ref, "include_item_info": 0},
        {"ref": sampleset_ref, "include_item_info": 1},
    ]
    n_items_in_set = len(
        reads_refs
    )  # sampleset_ref is created using all the reads_refs as samples
    for params in param_set:
        res = set_api_client.get_reads_set_v1(context, params)[0]
        assert "data" in res
        assert "items" in res["data"]
        assert "info" in res
        assert len(res["info"]) == INFO_LENGTH
        assert "item_count" in res["info"][10]
        assert res["info"][10]["item_count"] == n_items_in_set
        for item in res["data"]["items"]:
            assert "ref" in item
            if params.get("include_item_info", 0) == 1:
                assert "info" in item
                assert len(item["info"]) == INFO_LENGTH
            else:
                assert "info" not in item


def test_get_reads_set_bad_ref(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    with pytest.raises(
        ValueError, match='"ref" parameter must be a valid workspace reference'
    ):
        set_api_client.get_reads_set_v1(context, {"ref": "not_a_ref"})


def test_get_reads_set_bad_type(
    reads_refs: list[str], set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    with pytest.raises(ValueError, match="is invalid for get_reads_set_v1"):
        set_api_client.get_reads_set_v1(context, {"ref": reads_refs[0]})
