"""An interface for handling sets of ReadsAlignments."""
from typing import Any

from installed_clients.WorkspaceClient import Workspace

from SetAPI.error_messages import (
    include_params_valid,
    list_required,
    no_dupes,
    no_items,
    param_required,
    ref_must_be_valid,
    ref_path_must_be_valid,
    same_ref,
)
from SetAPI.generic.constants import INC_ITEM_INFO, INC_ITEM_REF_PATHS, REF_PATH_TO_SET
from SetAPI.generic.SetInterfaceV1 import SetInterfaceV1
from SetAPI.util import (
    build_ws_obj_selector,
    check_reference,
    info_to_ref,
    populate_item_object_ref_paths,
)


class ReadsAlignmentSetInterfaceV1:
    def __init__(self: "ReadsAlignmentSetInterfaceV1", workspace_client: Workspace):
        self.workspace_client = workspace_client
        self.set_interface = SetInterfaceV1(workspace_client)

    @staticmethod
    def set_type() -> str:
        """The set type saved by this class."""
        return "KBaseSets.ReadsAlignmentSet"

    @staticmethod
    def set_items_type() -> str:
        """The type of object in the sets."""
        return "ReadsAlignment"

    @staticmethod
    def allows_empty_set() -> bool:
        """Whether or not the class allows the creation of empty sets."""
        return False

    def save_reads_alignment_set(
        self: "ReadsAlignmentSetInterfaceV1",
        ctx: dict[str, Any],
        params: dict[str, Any],
    ) -> dict[str, str | list[str | int | dict[str, Any]]]:
        """Save new assembly sets.

        :param self: this class
        :type self: ReadsAlignmentSetInterfaceV1
        :param ctx: KBase context
        :type ctx: dict[str, Any]
        :param params: parameters for the new ReadsAlignmentSet
        :type params: dict[str, Any]
        :return: dict containing the new set reference and the set info
        :rtype: dict[str, str | list[str | int | dict[str, Any]]]
        """
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
        self: "ReadsAlignmentSetInterfaceV1", params: dict[str, Any]
    ) -> None:
        """Perform basic validation on the save set parameters.

        :param self: this class
        :type self: AssemblySetInterfaceV1
        :param params: parameters to the save_set function
        :type params: dict[str, Any]
        """
        if params.get("data", None) is None:
            err_msg = param_required("data")
            raise ValueError(err_msg)

        if "items" not in params["data"]:
            raise ValueError(list_required("items"))

        if not params["data"].get("items", None):
            raise ValueError(no_items(self.set_items_type()))

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

        # Get all the genome ids from our ReadsAlignment references (it's the genome_id key in
        # the object metadata). Make a set out of them.
        # If there's 0 or more than 1 item in the set, then either those items are bad, or they're
        # aligned against different genomes.
        ref_list = [{"ref": ref} for ref in seen_refs]
        info_list = self.workspace_client.get_object_info3(
            {"objects": ref_list, "includeMetadata": 1}
        )["infos"]
        num_genomes = len({item[10]["genome_id"] for item in info_list})
        if num_genomes != 1:
            raise ValueError(same_ref(self.set_items_type()))

    def get_reads_alignment_set(
        self: "ReadsAlignmentSetInterfaceV1", _, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Retrieve reads alignment sets.

        If the set is a KBaseSets.ReadsAlignmentSet, it gets returned as-is.
        If it's a KBaseRNASeq.RNASeqAlignmentSet, a few things get juggled.
        1. We try to figure out the object references for the alignments (which are optional)
        2. From each ref, we try to figure out the condition, and apply those as labels (also
           might be optional)

        :param self: this class
        :type self: ReadsAlignmentSetInterfaceV1
        :param _: unused (KBase context)
        :type ctx: dict[str, Any]
        :param params: dictionary of parameters
        :type params: dict[str, Any]
        :return: results of the get_set query
        :rtype: dict[str, Any]
        """
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

        # ...otherwise, we need to fetch it directly from the workspace and tweak it into the
        # expected return object
        return self.get_rnaseq_alignment_set(
            obj_ref_dict,
            checked_params[INC_ITEM_INFO],
            checked_params[INC_ITEM_REF_PATHS],
        )

    def get_rnaseq_alignment_set(
        self: "ReadsAlignmentSetInterfaceV1",
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
        alignment_ref_list = []
        if "sample_alignments" in obj:
            alignment_ref_list = obj["sample_alignments"]
        else:
            # this is a list of dicts of random strings -> alignment refs
            # need them all as a set, then emit as a list.
            reads_to_alignments = obj["mapped_alignments_ids"]
            refs = set()
            for mapping in reads_to_alignments:
                refs.update(list(mapping.values()))
            alignment_ref_list = list(refs)
        alignment_items = [{"ref": i} for i in alignment_ref_list]

        item_infos = self.workspace_client.get_object_info3(
            {"objects": alignment_items, "includeMetadata": 1}
        )["infos"]
        for idx, _ in enumerate(alignment_items):
            alignment_items[idx]["label"] = item_infos[idx][10].get("condition", None)
            if include_item_info:
                alignment_items[idx]["info"] = item_infos[idx]

        # If include_set_item_ref_paths is set, then add a field ref_path in alignment items
        if include_set_item_ref_paths:
            populate_item_object_ref_paths(alignment_items, obj_ref_dict)

        return {
            "data": {"items": alignment_items, "description": ""},
            "info": obj_data["info"],
        }

    def _check_get_set_params(
        self: "ReadsAlignmentSetInterfaceV1", params: dict[str, Any]
    ) -> dict[str, Any]:
        """Perform basic validation on the get_set parameters.

        :param self: this class
        :type self: ReadsAlignmentSetInterfaceV1
        :param params: parameters for the get_set query
        :type params: dict[str, Any]
        :return: validated parameters
        :rtype: dict[str, Any]
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
