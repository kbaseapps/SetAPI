"""This module contains some utility functions for the SetAPI."""
import os
import re
from typing import Any

from installed_clients.DataFileUtilClient import DataFileUtil

KBASE_UPA_REGEX = re.compile(r"^\d+/\d+(/\d+)?$")
WS_NAME_OBJ_NAME_REGEX = re.compile(r"^([\w\.\-\|]+:)?[\w\.\-\|]+/[\w\.\-\|]+$")


def check_reference(ref: str | None) -> bool:
    r"""Check whether a string looks like an object reference.

    Valid object references may be of the form

    \d+/\d+/\d+  classic KBase UPA
    \d+/\d+      ws ID and obj ID, no version
    \w+/\w+      ws name, object name (|, -, and . are also valid characters, but are omitted here for brevity)
    \w+:\w+/\w+  user ID, ws name, object name

    :param ref: a KBase object reference
    :type ref: str | None
    :return: True if ref looks like an object reference; False otherwise.
    :rtype: bool
    """
    if not ref:
        return False

    if not (WS_NAME_OBJ_NAME_REGEX.match(ref) or KBASE_UPA_REGEX.match(ref)):
        return False

    parts = ref.split("/")
    # do we have a KBase UPA (\d+/\d+ or \d+/\d+/\d+)?
    could_be_ints = sum(1 for item in parts if item.isdigit())
    if could_be_ints == len(parts):
        return True

    # otherwise, we have a ws name and object name, so there should only be two parts
    # none of the remaining parts should be integers
    if len(parts) == 3 or could_be_ints != 0:
        return False

    # make sure that if there's a ":" in the first part, the stuff on either side isn't an int
    if ":" in parts[0]:
        name_parts = parts[0].split(":")
        if any(item.isdigit() or len(item) == 0 for item in name_parts):
            return False

    return True


def info_to_ref(info: list[str | int | dict[str, str]]) -> str:
    """Extract the KBase UPA from a KBase object info list.

    :param info: object info list, as produced by the workspace
    :type info: list[str | int | dict[str, str]]
    :return: KBase UPA for the object
    :rtype: str
    """
    return f"{info[6]}/{info[0]}/{info[4]}"


def convert_workspace_param(params: dict[str, int | str]) -> dict[str, int | str]:
    """Find and convert the workspace name or ID into the appropriate version for ws.save_objects.

    :param params: parameters
    :type params: dict[str, str]
    :return: the key and value to be used in the WS request
    :rtype: dict[str, str]
    """
    if params:
        # check the workspace_id, ws_id, and workspace fields for potential IDs or names
        ws_id_like = params.get(
            "workspace_id", params.get("ws_id", params.get("workspace"))
        )
        if ws_id_like:
            if str(ws_id_like).isdigit():
                return {"id": int(ws_id_like)}
            # otherwise, we probably have a workspace name posing as a workspace ID
            return {"workspace": ws_id_like}

        ws_name_like = params.get("workspace_name", params.get("ws_name"))
        if ws_name_like:
            return {"workspace": str(ws_name_like)}

    raise ValueError("No appropriate key found for workspace name or ID")


def build_ws_obj_selector(
    ref: str, ref_path_to_set: None | list[str]
) -> dict[str, str]:
    """Build the appropriate workspace object selector.

    :param ref: a workspace object reference
    :type ref: str
    :param ref_path_to_set: a list of WS refs to the set
    :type ref_path_to_set: None | list[str]
    :return: the appropriate WS object ref
    :rtype: dict[str, str]
    """
    if ref_path_to_set and len(ref_path_to_set) > 0:
        return {"ref": ";".join(ref_path_to_set)}
    return {"ref": ref}


def populate_item_object_ref_paths(
    set_items: list[dict[str, Any]], obj_selector: dict[str, Any]
) -> list[dict[str, Any]]:
    """Add a field ref_path to each item in set; called when include_set_item_ref_paths is set.

    :param set_items: list of items in a set
    :type set_items: list[dict[str, Any]]
    :param obj_selector:
    :type obj_selector: dict[str, Any]

    :return: set items with "ref_path" field added
    :rtype: list[dict[str, Any]]
    """
    for set_item in set_items:
        set_item["ref_path"] = f"{obj_selector['ref']};{set_item['ref']}"
    return set_items


def dfu_get_obj_data(obj_ref):
    dfu = DataFileUtil(os.environ["SDK_CALLBACK_URL"])
    return dfu.get_objects({"object_refs": [obj_ref]})["data"][0]["data"]
