"""
An interface for saving and retrieving Sets of FeatureSets.
"""
from SetAPI.generic.SetInterfaceV1 import SetInterfaceV1
from SetAPI.util import check_reference, info_to_ref
from SetAPI.generic.constants import INC_ITEM_INFO, INC_ITEM_REF_PATHS, REF_PATH_TO_SET


class FeatureSetSetInterfaceV1:
    def __init__(self, workspace_client):
        self.ws = workspace_client
        self.set_interface = SetInterfaceV1(workspace_client)

    def save_feature_set_set(self, ctx, params):
        if "data" in params and params["data"] is not None:
            self._validate_feature_set_set_data(params["data"])
        else:
            raise ValueError('"data" parameter field required to save a FeatureSetSet')

        save_result = self.set_interface.save_set(
            "KBaseSets.FeatureSetSet", ctx["provenance"], params
        )
        info = save_result[0]
        return {
            "set_ref": info_to_ref(info),
            "set_info": info,
        }

    def _validate_feature_set_set_data(self, data):
        if "items" not in data:
            raise ValueError(
                '"items" list must be defined in data to save a FeatureSetSet'
            )

        # add 'description' and 'label' fields if not present in data:
        for item in data["items"]:
            if "label" not in item:
                item["label"] = ""
        if "description" not in data:
            data["description"] = ""

    def get_feature_set_set(self, ctx, params):
        self._check_get_feature_set_set_params(params)

        include_item_info = True if params.get(INC_ITEM_INFO, 0) == 1 else False

        include_set_item_ref_paths = (
            True if params.get(INC_ITEM_REF_PATHS, 0) == 1 else False
        )

        ref_path_to_set = params.get(REF_PATH_TO_SET, [])

        set_data = self.set_interface.get_set(
            params["ref"],
            include_item_info,
            ref_path_to_set,
            include_set_item_ref_paths,
        )
        set_data = self._normalize_feature_set_set_data(set_data)

        return set_data

    def _check_get_feature_set_set_params(self, params):
        if "ref" not in params or params["ref"] is None:
            raise ValueError(
                '"ref" parameter field specifying the FeatureSet set is required'
            )
        if not check_reference(params["ref"]):
            raise ValueError('"ref" parameter must be a valid workspace reference')
        if INC_ITEM_INFO in params and params[INC_ITEM_INFO] not in [0, 1]:
            raise ValueError(
                '"include_item_info" parameter field can only be set to 0 or 1'
            )

    def _normalize_feature_set_set_data(self, set_data):
        # make sure that optional/missing fields are filled in or are defined
        # TODO: populate empty description field
        # TODO?: populate empty label fields
        return set_data
