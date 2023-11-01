"""Generic set functionality tests."""
import time
from pprint import pprint
from test.conftest import INFO_LENGTH
from typing import Any

import pytest
from SetAPI.generic.GenericSetNavigator import GenericSetNavigator
from SetAPI.SetAPIImpl import SetAPI

DEBUG = False


def create_sets(
    reads_refs: list[str],
    set_api_client: SetAPI,
    ctx: dict[str, str | list],
    ws_name: str,
) -> dict:
    set_names = ["set_o_reads1", "set_o_reads2", "set_o_reads3"]
    set_refs = []

    for s in set_names:
        set_data = {
            "description": "my first reads",
            "items": [
                {"ref": reads_refs[0], "label": "reads1"},
                {"ref": reads_refs[1], "label": "reads2"},
            ],
        }
        # test a save - makes a new ReadsSet object in the workspace.
        res = set_api_client.save_reads_set_v1(
            ctx,
            {"data": set_data, "output_object_name": s, "workspace": ws_name},
        )[0]
        set_refs.append(res["set_ref"])

    return {"set_names": set_names, "set_refs": set_refs}


def test_list_sets_bad_input(
    set_api_client: SetAPI, ctx: dict[str, str | list]
) -> None:
    with pytest.raises(
        ValueError,
        match='One of "workspace" or "workspaces" field required to list sets',
    ):
        set_api_client.list_sets(ctx, {"include_set_item_info": 1})

    with pytest.raises(
        ValueError, match='"include_set_item_info" field must be set to 0 or 1'
    ):
        set_api_client.list_sets(
            ctx, {"workspace": 12345, "include_set_item_info": "foo"}
        )


# FIXME: requires a clean WS!!
@pytest.mark.skip("requires a clean WS")
def test_list_sets(
    reads_refs: list[str],
    set_api_client: SetAPI,
    ctx: dict[str, str | list],
    ws_name: str,
    clients: dict[str, Any],
) -> None:
    list_sets_ws_name = f"{ws_name}_list_sets"
    clients["ws"].create_workspace({"workspace": list_sets_ws_name})

    # make sure we can see an empty list of sets before WS has any
    res = set_api_client.list_sets(
        ctx, {"workspace": list_sets_ws_name, "include_set_item_info": 1}
    )[0]
    assert len(res["sets"]) == 0

    # create the test sets, adds a ReadsSet object in the workspace
    set_data = create_sets(reads_refs, set_api_client, ctx, list_sets_ws_name)

    # Get the sets in the workspace along with their item info.
    res = set_api_client.list_sets(
        ctx, {"workspace": list_sets_ws_name, "include_set_item_info": 1}
    )[0]
    assert "sets" in res
    assert len(res["sets"]) == len(set_data["set_names"])
    for s in res["sets"]:
        assert "ref" in s
        assert "info" in s
        assert "items" in s
        assert len(s["info"]) == INFO_LENGTH
        assert len(s["items"]) == 2
        for item in s["items"]:
            assert "ref" in item
            assert "info" in item
            assert len(item["info"]) == INFO_LENGTH

    # Get the sets in a workspace without their item info (just the refs)
    res2 = set_api_client.list_sets(ctx, {"workspace": list_sets_ws_name})[0]
    assert "sets" in res2
    assert len(res2["sets"]) == len(set_data["set_names"])
    for s in res2["sets"]:
        assert "ref" in s
        assert "info" in s
        assert "items" in s
        assert len(s["info"]) == INFO_LENGTH
        assert len(s["items"]) == 2
        for item in s["items"]:
            assert "ref" in item
            assert "info" not in item

    # Get the sets with their reference paths
    res3 = set_api_client.list_sets(
        ctx, {"workspace": list_sets_ws_name, "include_set_item_ref_paths": 1}
    )[0]

    if DEBUG:
        print("Result from list_items with ref_paths")
        pprint(res3)
        print("=====================================")

    assert "sets" in res3
    assert len(res3["sets"]) == len(set_data["set_names"])
    for s in res3["sets"]:
        assert "ref" in s
        assert "info" in s
        assert "items" in s
        assert len(s["info"]) == INFO_LENGTH
        assert len(s["items"]) == 2
        for item in s["items"]:
            assert "ref" in item
            assert "info" not in item
            assert "ref_path" in item
            assert item["ref_path"] == s["ref"] + ";" + item["ref"]

    unit_test_get_set_items(set_api_client, ctx, set_data)


def test_bulk_list_sets(
    clients: dict[str, Any], set_api_client: SetAPI, ctx: dict[str, str | list]
) -> None:
    try:
        ids = []
        for ws_info in clients["ws"].list_workspace_info(
            {"perm": "r", "excludeGlobal": 1}
        ):
            if ws_info[4] < 1000:
                ids.append(str(ws_info[0]))
            else:
                print(f"Workspace: {ws_info[1]}, size={ws_info[4]} skipped")

        print("Number of workspaces for bulk list_sets: " + str(len(ids)))
        if len(ids) > 0:
            ret = set_api_client.list_sets(
                ctx,
                {"workspaces": [ids[0]], "include_set_item_info": 1},
            )[0]
        GenericSetNavigator.DEBUG = True
        t1 = time.time()
        ret = set_api_client.list_sets(
            ctx, {"workspaces": ids, "include_set_item_info": 1}
        )[0]

        print(f"Objects found: {len(ret['sets'])}, time={time.time() - t1}")
    finally:
        GenericSetNavigator.DEBUG = False


def unit_test_get_set_items(
    set_data: dict, set_api_client: SetAPI, ctx: dict[str, str | list]
) -> None:
    res = set_api_client.get_set_items(
        ctx,
        {
            "set_refs": [
                {"ref": set_data["set_refs"][0]},
                {"ref": set_data["set_refs"][1]},
                {"ref": set_data["set_refs"][2]},
            ],
            "include_set_item_ref_paths": 1,
        },
    )[0]
    if DEBUG:
        print("Result from get_set_items with ref_paths")
        pprint(res)
        print("========================================")

    assert len(res["sets"]) == 3
    for s in res["sets"]:
        assert "ref" in s
        assert "info" in s
        assert "items" in s
        assert len(s["info"]) == INFO_LENGTH
        assert len(s["items"]) == 2
        for item in s["items"]:
            assert "ref" in item
            assert "info" in item
            assert len(item["info"]) == INFO_LENGTH
            assert "ref_path" in item
            assert item["ref_path"] == s["ref"] + ";" + item["ref"]
