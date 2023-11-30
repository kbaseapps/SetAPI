from SetAPI.generic.SetInterfaceV1 import SetInterfaceV1
from SetAPI.util import (
    populate_item_object_ref_paths,
    check_reference,
    build_ws_obj_selector,
    info_to_ref,
)
from SetAPI.generic.constants import INC_ITEM_INFO, INC_ITEM_REF_PATHS, REF_PATH_TO_SET


class ReadsSetInterfaceV1:
    def __init__(self, workspace_client):
        self.ws = workspace_client
        self.set_interface = SetInterfaceV1(workspace_client)

    def save_reads_set(self, ctx, params):
        if "data" in params:
            self._validate_reads_set_data(params["data"])
        else:
            raise ValueError('"data" parameter field required to save a ReadsSet')

        save_result = self.set_interface.save_set(
            "KBaseSets.ReadsSet", ctx["provenance"], params
        )
        info = save_result[0]
        return {
            "set_ref": info_to_ref(info),
            "set_info": info,
        }

    def _validate_reads_set_data(self, data):
        # TODO: add checks that only one copy of each reads data is in the set
        # TODO?: add checks that reads data list is homogenous (no mixed single/paired-end libs)

        if "items" not in data:
            raise ValueError('"items" list must be defined in data to save a ReadsSet')

        # add 'description' and 'label' fields if not present in data:
        for item in data["items"]:
            if "label" not in item:
                item["label"] = ""
        if "description" not in data:
            data["description"] = ""

    def get_reads_set(self, ctx, params):
        set_type, obj_spec = self._check_get_reads_set_params(params)

        include_item_info = True if params.get(INC_ITEM_INFO, 0) == 1 else False

        include_set_item_ref_paths = (
            True if params.get(INC_ITEM_REF_PATHS, 0) == 1 else False
        )

        ref_path_to_set = params.get(REF_PATH_TO_SET, [])

        # If this is a KBaseSets.ReadsSet, do as normal.
        if "KBaseSets" in set_type:
            set_data = self.set_interface.get_set(
                params["ref"],
                include_item_info,
                ref_path_to_set,
                include_set_item_ref_paths,
            )
            return self._normalize_read_set_data(set_data)

        # Otherwise, fetch the SampleSet info from the workspace and go on from there.
        elif "KBaseRNASeq.RNASeqSampleSet" in set_type:
            obj_data = self.ws.get_objects2({"objects": [obj_spec]})["data"][0]
            obj = obj_data["data"]
            obj_info = obj_data["info"]
            desc = obj.get("sampleset_desc", "")
            obj_info[10]["description"] = desc
            obj_info[10]["item_count"] = len(obj.get("sample_ids", []))
            set_data = {"data": {"items": [], "description": desc}, "info": obj_info}

            reads_items = []
            if len(obj.get("sample_ids")) != len(obj.get("condition")):
                raise RuntimeError(
                    "Invalid RNASeqSampleSet! The number of conditions \
                                    doesn't match the number of reads objects."
                )
            if len(obj.get("sample_ids", [])) == 0:
                return set_data
            for idx, ref in enumerate(obj["sample_ids"]):
                reads_items.append(
                    {"ref": obj["sample_ids"][idx], "label": obj["condition"][idx]}
                )
            if include_item_info:
                reads_obj_specs = [{"ref": i["ref"]} for i in reads_items]
                infos = self.ws.get_object_info3(
                    {"objects": reads_obj_specs, "includeMetadata": 1}
                )["infos"]
                for idx, info in enumerate(infos):
                    reads_items[idx]["info"] = info
            """
            If include_set_item_ref_paths is set, then add a field ref_path in alignment items
            """
            if include_set_item_ref_paths:
                populate_item_object_ref_paths(reads_items, obj_spec)

            set_data["data"]["items"] = reads_items
            return set_data
        # Otherwise-otherwise, it's not the right type for this getter.
        else:
            raise ValueError(
                "The object type {} is invalid for get_reads_set_v1".format(set_type)
            )

    def _check_get_reads_set_params(self, params):
        if "ref" not in params:
            raise ValueError(
                '"ref" parameter field specifying the reads set is required'
            )
        if not check_reference(params["ref"]):
            raise ValueError('"ref" parameter must be a valid workspace reference')
        if INC_ITEM_INFO in params:
            if params[INC_ITEM_INFO] not in [0, 1]:
                raise ValueError(
                    '"include_item_info" parameter field can only be set to 0 or 1'
                )

        obj_spec = build_ws_obj_selector(
            params.get("ref"), params.get(REF_PATH_TO_SET, [])
        )

        info = self.ws.get_object_info3({"objects": [obj_spec]})

        return info["infos"][0][2], obj_spec

    def _normalize_read_set_data(self, set_data):
        # make sure that optional/missing fields are filled in or are defined
        # TODO: populate empty description field
        # TODO?: populate empty label fields
        return set_data
