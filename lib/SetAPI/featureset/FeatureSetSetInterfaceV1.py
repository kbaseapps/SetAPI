"""An interface for saving and retrieving Sets of FeatureSets."""
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


class FeatureSetSetInterfaceV1:
    def __init__(self, workspace_client):
        self.ws = workspace_client
        self.set_interface = SetInterfaceV1(workspace_client)

    @staticmethod
    def set_type() -> str:
        return "KBaseSets.FeatureSetSet"

    @staticmethod
    def set_items_type() -> str:
        return "FeatureSet"

    @staticmethod
    def allows_empty_set() -> bool:
        return True

    def save_feature_set_set(self, ctx, params):
        self.set_interface._check_save_set_params(params)
        self._validate_save_set_params(params)
        return self.set_interface.save_set(self.set_type(), ctx["provenance"], params)

    def _validate_save_set_params(self, params):
        if params.get("data") is None:
            err_msg = param_required("data")
            raise ValueError(err_msg)

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

    def get_feature_set_set(self, ctx, params):
        checked_params = self._check_get_set_params(params)
        return self.set_interface.get_set(**checked_params)

    def _check_get_set_params(self, params):
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
