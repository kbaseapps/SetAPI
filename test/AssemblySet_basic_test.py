"""Basic tests for the AssemblySet class."""
from test.util import INFO_LENGTH
from SetAPI.SetAPIImpl import SetAPI


SET_TYPE = "KBaseSets.AssemblySet"


def test_basic_save_and_get(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    ws_name: str,
    assembly_refs: list[str],
) -> None:
    set_name = "set_of_assemblies"
    set_description = "my first assembly set"
    second_item_data = {"ref": assembly_refs[1], "label": "assembly_ref[1]"}
    n_items = len(assembly_refs)
    # create the set object
    set_data = {
        "description": set_description,
        "items": [
            {"ref": assembly_refs[0], "label": "assembly_ref[0]"},
            second_item_data,
        ],
    }

    # test a save
    res = set_api_client.save_assembly_set_v1(
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
    assert res["set_info"][10]["item_count"] == str(n_items)

    # test get of that object
    d1 = set_api_client.get_assembly_set_v1(context, {"ref": ws_name + "/" + set_name})[
        0
    ]
    assert "data" in d1
    assert "info" in d1
    assert len(d1["info"]) == INFO_LENGTH
    assert "item_count" in d1["info"][10]
    assert d1["info"][10]["item_count"] == str(n_items)

    assert d1["data"]["description"] == set_description
    assert len(d1["data"]["items"]) == n_items

    item2 = d1["data"]["items"][1]
    assert "info" not in item2
    assert "ref_path" not in item2
    assert "ref" in item2
    assert "label" in item2
    assert item2["label"] == second_item_data["label"]
    assert item2["ref"] == assembly_refs[1]

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
    assert d2["info"][10]["item_count"] == str(n_items)
    assert d2["data"]["description"] == set_description
    assert len(d2["data"]["items"]) == n_items

    item2 = d2["data"]["items"][1]
    assert "info" in item2
    assert len(item2["info"]), INFO_LENGTH
    assert "ref" in item2
    assert item2["ref"] == assembly_refs[1]

    assert "ref_path" in item2
    assert item2["ref_path"] == res["set_ref"] + ";" + item2["ref"]


def check_empty_set(obj: dict, description: str) -> None:
    """Check that a set object has zero items in it.

    :param obj: set data as returned by the SetAPI
    :type obj: dict
    :param description: description parameter of the set
    :type description: str
    """
    assert "data" in obj
    assert "info" in obj
    assert len(obj["info"]) == INFO_LENGTH
    assert "item_count" in obj["info"][10]
    assert obj["info"][10]["item_count"] == "0"
    assert obj["data"]["description"] == description
    assert len(obj["data"]["items"]) == 0


def test_save_and_get_of_empty_set(
    set_api_client: SetAPI, context: dict[str, str | list], ws_id: int, ws_name: str
) -> None:
    set_name = "nada_set"
    set_description = "nothing to see here"
    n_items = 0

    # create the set object
    set_data = {"description": set_description, "items": []}
    # test a save
    res = set_api_client.save_assembly_set_v1(
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
    assert res["set_info"][10]["item_count"] == str(n_items)

    # test get of that object
    d1 = set_api_client.get_assembly_set_v1(context, {"ref": ws_name + "/" + set_name})[
        0
    ]
    check_empty_set(d1, set_description)

    d2 = set_api_client.get_assembly_set_v1(
        context, {"ref": res["set_ref"], "include_item_info": 1}
    )[0]
    check_empty_set(d2, set_description)
