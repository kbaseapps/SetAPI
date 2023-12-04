"""An interface for handling sets of Assemblies."""
from typing import Any

from installed_clients.WorkspaceClient import Workspace

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
    check_reference,
    info_to_ref,
)


class AssemblySetInterfaceV1:
    def __init__(self: "AssemblySetInterfaceV1", workspace_client: Workspace):
        self.ws = workspace_client
        self.set_interface = SetInterfaceV1(workspace_client)

    @staticmethod
    def set_type() -> str:
        """The set type saved by this class."""
        return "KBaseSets.AssemblySet"

    @staticmethod
    def set_items_type() -> str:
        """The type of object in the sets."""
        return "Assembly"

    @staticmethod
    def allows_empty_set() -> bool:
        """Whether or not the class allows the creation of empty sets."""
        return True

    def save_assembly_set(
        self: "AssemblySetInterfaceV1", ctx: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, str | list[str | int | dict[str, Any]]]:
        """Save new assembly sets.

        :param self: this class
        :type self: AssemblySetInterfaceV1
        :param ctx: KBase context
        :type ctx: dict[str, Any]
        :param params: parameters for the new AssemblySet
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
        self: "AssemblySetInterfaceV1", params: dict[str, Any]
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

        # N.b. AssemblySets allow an empty items list so we don't
        # need to check that params["data"]["items"] is populated
        if "items" not in params["data"]:
            raise ValueError(list_required("items"))

        # add 'description' and item 'label' fields if not present:
        if "description" not in params["data"]:
            params["data"]["description"] = ""

        seen_refs = set()
        for item in params["data"]["items"]:
            if "label" not in item:
                item["label"] = ""
            if item["ref"] in seen_refs:
                raise ValueError(no_dupes())
            seen_refs.add(item["ref"])

    def get_assembly_set(
        self: "AssemblySetInterfaceV1", _, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Retrieve assembly sets.

        :param self: this class
        :type self: AssemblySetInterfaceV1
        :param _: unused (KBase context)
        :type ctx: dict[str, Any]
        :param params: dictionary of parameters
        :type params: dict[str, Any]
        :return: results of the get_set query
        :rtype: dict[str, Any]
        """
        checked_params = self._check_get_set_params(params)
        return self.set_interface.get_set(**checked_params)

    def _check_get_set_params(
        self: "AssemblySetInterfaceV1", params: dict[str, Any]
    ) -> dict[str, str | bool | list[str]]:
        """Perform basic validation on the get_set parameters.

        :param self: this class
        :type self: AssemblySetInterfaceV1
        :param params: parameters to the get_set function
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
