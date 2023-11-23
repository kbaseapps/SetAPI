"""
This module contains some utility functions for the SetAPI.
"""
import os
import re
from installed_clients.DataFileUtilClient import DataFileUtil


def check_reference(ref):
    """
    Returns True if ref looks like an actual object reference: xx/yy/zz or xx/yy
    Returns False otherwise.
    """
    obj_ref_regex = re.compile(r"^((\d+)|[A-Za-z].*)\/((\d+)|[A-Za-z].*)(\/\d+)?$")
    # obj_ref_regex = re.compile("^(?P<wsid>\d+)\/(?P<objid>\d+)(\/(?P<ver>\d+))?$")
    if ref is None or not obj_ref_regex.match(ref):
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
    if "workspace" in params:
        if str(params["workspace"]).isdigit():
            return {"id": int(params["workspace"])}
        return {"workspace": params["workspace"]}

    if "workspace_id" in params:
        return {"id": params["workspace_id"]}
    if "ws_id" in params:
        return {"id": params["ws_id"]}

    if "workspace_name" in params:
        return {"workspace": params["workspace_name"]}
    if "ws_name" in params:
        return {"workspace": params["ws_name"]}

    raise ValueError("No appropriate key found for workspace name or ID")


def build_ws_obj_selector(ref, ref_path_to_set):
    if ref_path_to_set and len(ref_path_to_set) > 0:
        return {"ref": ";".join(ref_path_to_set)}
    return {"ref": ref}


def populate_item_object_ref_paths(set_items, obj_selector):
    """
    Called when include_set_item_ref_paths is set.
    Add a field ref_path to each item in set
    """
    for set_item in set_items:
        set_item["ref_path"] = obj_selector["ref"] + ";" + set_item["ref"]
    return set_items


def dfu_get_obj_data(obj_ref):
    dfu = DataFileUtil(os.environ["SDK_CALLBACK_URL"])
    return dfu.get_objects({"object_refs": [obj_ref]})["data"][0]["data"]
