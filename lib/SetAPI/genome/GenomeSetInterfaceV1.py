"""An interface for handling genome sets."""
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
from SetAPI.util import check_reference, info_to_ref


class GenomeSetInterfaceV1:
    def __init__(self, workspace_client):
        self.ws = workspace_client
        self.set_interface = SetInterfaceV1(workspace_client)

    @staticmethod
    def set_type() -> str:
        return "KBaseSets.GenomeSet"

    @staticmethod
    def set_items_type() -> str:
        return "Genome"

    @staticmethod
    def allows_empty_set() -> bool:
        return True

    def save_genome_set(self, ctx, params):
        """
        by default save 'KBaseSets.GenomeSet'
        save 'KBaseSearch.GenomeSet' by setting save_search_set
        """
        save_search_set = params.get("save_search_set", False)
        self._validate_save_set_params(params, save_search_set)

        genome_type = "KBaseSearch.GenomeSet" if save_search_set else self.set_type()

        save_result = self.set_interface.save_set(
            genome_type, ctx["provenance"], params
        )
        info = save_result[0]
        return {
            "set_ref": info_to_ref(info),
            "set_info": info,
        }

    def _validate_save_set_params(
        self: "GenomeSetInterfaceV1",
        params: dict[str, Any],
        save_search_set: bool = False,
    ) -> None:
        """Perform basic validation on the save set parameters.

        :param self: this class
        :type self: GenomeSetInterfaceV1
        :param params: parameters to the save_set function
        :type params: dict[str, Any]
        :param save_search_set: whether the set type should be a search set or a set set
        :type save_search_set: bool
        """
        if params.get("data") is None:
            err_msg = param_required("data")
            raise ValueError(err_msg)

        list_item_type = "elements" if save_search_set else "items"
        if list_item_type not in params["data"]:
            raise ValueError(list_required(list_item_type))

        # add 'description' and 'label' fields if not present in data:
        if "description" not in params["data"]:
            params["data"]["description"] = ""

        seen_refs = set()
        for item in params["data"].get("items", []):
            if "label" not in item:
                item["label"] = ""
            if item["ref"] in seen_refs:
                raise ValueError(no_dupes())
            seen_refs.add(item["ref"])

    def get_genome_set(self, ctx, params):
        checked_params = self._check_get_set_params(params)
        return self.set_interface.get_set(**checked_params)

    def _check_get_set_params(
        self: "GenomeSetInterfaceV1", params: dict[str, Any]
    ) -> dict[str, Any]:
        """Perform basic validation on the get_set parameters.

        :param self: this class
        :type self: ReadsSetInterfaceV1
        :param params: method params
        :type params: dict[str, Any]
        :return: validated parameters
        :rtype: dict[str, str | bool | list[str]]
        """
        if not params.get("ref"):
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
