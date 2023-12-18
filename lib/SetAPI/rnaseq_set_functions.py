"""Functions for retrieving various RNASeq sets from the DB."""
from typing import Any

from installed_clients.WorkspaceClient import Workspace

from SetAPI.util import populate_item_object_ref_paths


def get_rnaseq_set(
    workspace_client: Workspace,
    obj_selector: dict[str, str],
    set_type: str,
    obj_data: dict[str, Any],
    include_item_info: bool = False,
    include_set_item_ref_paths: bool = False,
) -> dict[str, Any]:
    """Retrieve and reconstitute a KBase RNASeqAlignmentSet or RNASeqExpressionSet from the workspace.

    :param workspace_client: workspace client
    :type workspace_client: Workspace
    :param obj_selector: dictionary with key "ref" and value reference for the set
    :type obj_selector: dict[str, str]
    :param set_type: the set type
    :type set_type: str
    :param include_item_info: whether info should be included for each set item
    :type include_item_info: bool, defaults to False
    :param include_set_item_ref_paths: whether the item ref paths should be included
    :type include_set_item_ref_paths: bool, defaults to False
    :return: standard set output structure
    :rtype: dict[str, Any]
    """
    set_data = obj_data["data"]
    set_info = obj_data["info"]

    is_expression = "expression" in set_type or "Expression" in set_type
    list_data_key = "sample_expression_ids" if is_expression else "sample_alignments"
    map_data_key = "mapped_expression_ids" if is_expression else "mapped_alignments_ids"

    ref_list = []
    if list_data_key in set_data:
        ref_list = set_data[list_data_key]
    else:
        # this is a list of dicts of random strings -> alignment refs
        # need them all as a set, then emit as a list.
        refs = set()
        for mapping in set_data[map_data_key]:
            refs.update(list(mapping.values()))
        ref_list = list(refs)

    set_items = [{"ref": i} for i in ref_list]

    item_infos = workspace_client.get_object_info3(
        {"objects": set_items, "includeMetadata": 1}
    )["infos"]

    for idx, _ in enumerate(set_items):
        set_items[idx]["label"] = item_infos[idx][10].get("condition")
        if include_item_info:
            set_items[idx]["info"] = item_infos[idx]

    # If include_set_item_ref_paths is set, then add a field ref_path in alignment items
    if include_set_item_ref_paths:
        populate_item_object_ref_paths(set_items, obj_selector)

    # retrofit missing description / item count
    set_info[10]["description"] = ""
    set_info[10]["item_count"] = str(len(set_items))

    return {
        "data": {"items": set_items, "description": ""},
        "info": set_info,
    }


def get_rnaseq_sample_set(
    workspace_client: Workspace,
    obj_selector: dict[str, str],
    ws_data: dict[str, Any],
    include_item_info: bool = False,
    include_set_item_ref_paths: bool = False,
) -> dict[str, Any]:
    """Retrieve and reconstitute a KBase RNASeqSampleSet from the workspace.

    :param obj_selector: dictionary with key "ref" and value reference for the set
    :type obj_selector: dict[str, str]
    :param include_item_info: whether info should be included for each set item
    :type include_item_info: bool, defaults to False
    :param include_set_item_ref_paths: whether the item ref paths should be included
    :type include_set_item_ref_paths: bool, defaults to False
    :return: standard set output structure
    :rtype: dict[str, Any]
    """
    obj_data = ws_data["data"]
    set_info = ws_data["info"]
    desc = obj_data.get("sampleset_desc", "")
    set_info[10]["description"] = desc
    set_info[10]["item_count"] = len(obj_data.get("sample_ids", []))

    set_items = []
    set_data = {"data": {"items": set_items, "description": desc}, "info": set_info}

    if len(obj_data.get("sample_ids")) != len(obj_data.get("condition")):
        err_msg = "Invalid RNASeqSampleSet! The number of conditions doesn't match the number of reads objects."
        raise RuntimeError(err_msg)

    if len(obj_data.get("sample_ids", [])) == 0:
        return set_data

    for idx, _ in enumerate(obj_data["sample_ids"]):
        set_items.append(
            {"ref": obj_data["sample_ids"][idx], "label": obj_data["condition"][idx]}
        )

    if include_item_info:
        set_item_refs = [{"ref": i["ref"]} for i in set_items]
        infos = workspace_client.get_object_info3(
            {"objects": set_item_refs, "includeMetadata": 1}
        )["infos"]
        for idx, info in enumerate(infos):
            set_items[idx]["info"] = info

    if include_set_item_ref_paths:
        populate_item_object_ref_paths(set_items, obj_selector)

    return {
        "data": {"items": set_items, "description": desc},
        "info": set_info,
    }
