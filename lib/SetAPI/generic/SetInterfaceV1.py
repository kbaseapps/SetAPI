"""The main interface for the Set API."""
from typing import Any

from installed_clients.WorkspaceClient import Workspace

from SetAPI.error_messages import param_required
from SetAPI.generic.constants import ASSEMBLY, FEATURE_SET, GENOME, READS
from SetAPI.util import (
    build_ws_obj_selector,
    convert_workspace_param,
    info_to_ref,
    populate_item_object_ref_paths,
)

ALLOWS_EMPTY_SETS = [ASSEMBLY, FEATURE_SET, GENOME, READS]


class SetInterfaceV1:
    """The core interface for saving and retrieving sets."""

    def __init__(self: "SetInterfaceV1", workspace_client: Workspace) -> None:
        """Initialise the class.

        :param self: this class
        :type self: SetInterfaceV1
        :param workspace_client: workspace client
        :type workspace_client: Workspace
        """
        self.ws = workspace_client

    def save_set(
        self: "SetInterfaceV1",
        set_type: str,
        provenance: dict[str, Any],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Save a set to the workspace as the set type provided.

        :param self: this class
        :type self: SetInterfaceV1
        :param set_type: set type, e.g. KBaseSets.AssemblySet
        :type set_type: str
        :param provenance: provenance
        :type provenance: dict[str, Any]
        :param params: parameters for the request
        :type params: dict[str, Any]
        :return: newly-created set item
        :rtype: dict[str, Any]
        """
        self._check_save_set_params(params)
        save_params = {
            "objects": [
                {
                    "name": params["output_object_name"],
                    "data": params["data"],
                    "type": set_type,
                    "provenance": provenance,
                    "hidden": 0,
                }
            ]
        }
        ws_params = convert_workspace_param(params)

        save_result = self.ws.save_objects({**save_params, **ws_params})
        info = save_result[0]
        return {
            "set_ref": info_to_ref(info),
            "set_info": info,
        }

    def _check_save_set_params(self: "SetInterfaceV1", params: dict[str, Any]) -> None:
        """Validate the params for saving a set.

        :param self: this class
        :type self: SetInterfaceV1
        :param params: set parameters
        :type params: dict[str, Any]
        """
        if (
            not params.get("workspace")
            and not params.get("workspace_id")
            and not params.get("workspace_name")
        ):
            raise ValueError(
                param_required('workspace" or "workspace_id" or "workspace_name')
            )

        for param in ["data", "output_object_name"]:
            if not params.get(param):
                raise ValueError(param_required(param))

    def get_set(
        self: "SetInterfaceV1",
        ref: str,
        include_item_info: bool = False,
        ref_path_to_set: list[str] | None = None,
        include_set_item_ref_paths: bool = False,
    ) -> dict[str, Any]:
        """Retrieve an object from the workspace.

        N.b. this method assumes that the object is a set, but it
        will happily retrieve other objects too.

        :param self: this class
        :type self: SetInterfaceV1
        :param ref: object reference
        :type ref: str
        :param include_item_info: whether or not to populate the info of the set items, defaults to False
        :type include_item_info: bool, optional
        :param ref_path_to_set: ref path for the object, defaults to None
        :type ref_path_to_set: list[str] | None, optional
        :param include_set_item_ref_paths: whether or not to add ref paths, defaults to False
        :type include_set_item_ref_paths: bool, optional
        :return: set data
        :rtype: dict[str, Any]
        """
        if ref_path_to_set is None:
            ref_path_to_set = []
        obj_selector = build_ws_obj_selector(ref, ref_path_to_set)

        # retrieve the object from the workspace
        ws_data = self.ws.get_objects2({"objects": [obj_selector]})

        set_data = {
            "data": ws_data["data"][0]["data"],
            "info": ws_data["data"][0]["info"],
        }

        # not all sets have 'items' (e.g. KBaseSearch.GenomeSet);
        # if they don't, skip the following steps as they will error out
        if not set_data["data"].get("items", []):
            return set_data

        if include_item_info:
            self._populate_item_object_info(set_data, ref_path_to_set)

        if include_set_item_ref_paths:
            set_items = set_data["data"]["items"]
            populate_item_object_ref_paths(set_items, obj_selector)

        return set_data

    def _populate_item_object_info(
        self: "SetInterfaceV1", set_data: dict[str, Any], ref_path_to_set: list[str]
    ) -> None:
        items = set_data["data"].get("items")
        if not items:
            return
        # generate a list of ws refs for the items in the set
        objects = [
            build_ws_obj_selector(item["ref"], [*ref_path_to_set, item["ref"]])
            for item in items
        ]
        obj_info_dump = self.ws.get_object_info3(
            {"objects": objects, "includeMetadata": 1}
        )["infos"]

        for k in range(len(obj_info_dump)):
            items[k]["info"] = obj_info_dump[k]
