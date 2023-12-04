"""An interface for handling reads sets."""
from typing import Any

from SetAPI.error_messages import (
    include_params_valid,
    list_required,
    no_dupes,
    param_required,
    ref_must_be_valid,
    ref_path_must_be_valid,
)
from SetAPI.generic.constants import INC_ITEM_INFO, INC_ITEM_REF_PATHS, REF_PATH_TO_SET
from SetAPI.generic.SetInterfaceV1 import SetInterfaceV1
from SetAPI.util import (
    build_ws_obj_selector,
    check_reference,
    info_to_ref,
    populate_item_object_ref_paths,
)


class ReadsSetInterfaceV1:
    def __init__(self, workspace_client):
        self.workspace_client = workspace_client
        self.set_interface = SetInterfaceV1(workspace_client)

    @staticmethod
    def set_type() -> str:
        return "KBaseSets.ReadsSet"

    @staticmethod
    def set_items_type() -> str:
        return "Reads"

    @staticmethod
    def allows_empty_set() -> bool:
        return True

    def save_reads_set(self, ctx, params):
        self._validate_save_set_params(params)

        save_result = self.set_interface.save_set(
            self.set_type(), ctx["provenance"], params
        )
        info = save_result[0]
        return {
            "set_ref": info_to_ref(info),
            "set_info": info,
        }

    def _validate_save_set_params(
        self: "ReadsSetInterfaceV1", params: dict[str, Any]
    ) -> None:
        """Perform basic validation on the save set parameters.

        :param self: this class
        :type self: ReadsSetInterfaceV1
        :param params: parameters to the save_set function
        :type params: dict[str, Any]
        """
        if params.get("data", None) is None:
            err_msg = param_required("data")
            raise ValueError(err_msg)

        if "items" not in params["data"]:
            raise ValueError(list_required("items"))

        # add 'description' and 'label' fields if not present in data:
        if "description" not in params["data"]:
            params["data"]["description"] = ""

        seen_refs = set()
        for item in params["data"]["items"]:
            if "label" not in item:
                item["label"] = ""
            if item["ref"] in seen_refs:
                raise ValueError(no_dupes())
            seen_refs.add(item["ref"])
        # TODO: add checks that only one copy of each reads data is in the set
        # TODO?: add checks that reads data list is homogenous (no mixed single/paired-end libs)

    def get_reads_set(self, ctx, params):
        checked_params = self._check_get_set_params(params)

        # check the type of the set itself
        obj_ref_dict = build_ws_obj_selector(
            checked_params["ref"], checked_params[REF_PATH_TO_SET]
        )

        info = self.workspace_client.get_object_info3({"objects": [obj_ref_dict]})
        set_type = info["infos"][0][2]

        if "KBaseSets" in set_type:
            # If it's a KBaseSets type, then we know the usual interface will work...
            return self.set_interface.get_set(**checked_params)

        # Otherwise, fetch the SampleSet info from the workspace and go on from there.
        if "KBaseRNASeq.RNASeqSampleSet" in set_type:
            return self.get_rnaseq_sample_set(
                obj_ref_dict,
                checked_params[INC_ITEM_INFO],
                checked_params[INC_ITEM_REF_PATHS],
            )

        # Otherwise-otherwise, it's not the right type for this getter.
        raise ValueError(f"The object type {set_type} is invalid for get_reads_set_v1")

    def _check_get_set_params(
        self: "ReadsSetInterfaceV1", params: dict[str, Any]
    ) -> dict[str, Any]:
        """Perform basic validation on the get_set parameters.

        :param self: this class
        :type self: ReadsSetInterfaceV1
        :param params: method params
        :type params: dict[str, Any]
        :return: validated parameters
        :rtype: dict[str, str | bool | list[str]]
        """
        if not params.get("ref", None):
            raise ValueError(param_required("ref"))

        if not check_reference(params["ref"]):
            raise ValueError(ref_must_be_valid())

        ref_path_to_set = params.get(REF_PATH_TO_SET, [])
        for path in ref_path_to_set:
            if not check_reference(path):
                raise ValueError(ref_path_must_be_valid())

        for param in [INC_ITEM_INFO, INC_ITEM_REF_PATHS]:
            if param in params and params[param] not in [0, 1]:
                raise ValueError(include_params_valid(param))

        return {
            "ref": params["ref"],
            INC_ITEM_INFO: params.get(INC_ITEM_INFO, 0) == 1,
            INC_ITEM_REF_PATHS: params.get(INC_ITEM_REF_PATHS, 0) == 1,
            REF_PATH_TO_SET: ref_path_to_set,
        }

    def get_rnaseq_sample_set(
        self: "ReadsSetInterfaceV1",
        obj_ref_dict: dict[str, str],
        include_item_info: bool = False,
        include_set_item_ref_paths: bool = False,
    ) -> dict[str, Any]:
        """Retrieve and reconstitute a KBase RNASeqAlignmentSet from the workspace.

        :param self: this class
        :type self: ReadsAlignmentSetInterfaceV1
        :param obj_ref_dict: dictionary with key "ref" and value reference for the set
        :type obj_ref_dict: dict[str, str]
        :param include_item_info: whether info should be included for each set item
        :type include_item_info: bool, defaults to False
        :param include_set_item_ref_paths: whether the item ref paths should be included
        :type include_set_item_ref_paths: bool, defaults to False
        :return: standard set output structure
        :rtype: dict[str, Any]
        """

        obj_data = self.workspace_client.get_objects2({"objects": [obj_ref_dict]})[
            "data"
        ][0]
        obj = obj_data["data"]
        obj_info = obj_data["info"]
        desc = obj.get("sampleset_desc", "")
        obj_info[10]["description"] = desc
        obj_info[10]["item_count"] = len(obj.get("sample_ids", []))
        set_data = {"data": {"items": [], "description": desc}, "info": obj_info}

        reads_items = []
        if len(obj.get("sample_ids")) != len(obj.get("condition")):
            raise RuntimeError(
                "Invalid RNASeqSampleSet! The number of conditions doesn't match the number of reads objects."
            )
        if len(obj.get("sample_ids", [])) == 0:
            return set_data
        for idx, _ in enumerate(obj["sample_ids"]):
            reads_items.append(
                {"ref": obj["sample_ids"][idx], "label": obj["condition"][idx]}
            )

        if include_item_info:
            reads_obj_specs = [{"ref": i["ref"]} for i in reads_items]
            infos = self.workspace_client.get_object_info3(
                {"objects": reads_obj_specs, "includeMetadata": 1}
            )["infos"]
            for idx, info in enumerate(infos):
                reads_items[idx]["info"] = info

        if include_set_item_ref_paths:
            populate_item_object_ref_paths(reads_items, obj_ref_dict)

        set_data["data"]["items"] = reads_items
        return set_data
