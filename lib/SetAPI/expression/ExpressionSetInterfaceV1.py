"""An interface for handling sets of Expression objects."""
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


class ExpressionSetInterfaceV1:
    def __init__(self, workspace_client):
        self.workspace_client = workspace_client
        self.set_interface = SetInterfaceV1(workspace_client)

    @staticmethod
    def set_type() -> str:
        return "KBaseSets.ExpressionSet"

    @staticmethod
    def set_items_type() -> str:
        return "Expression"

    @staticmethod
    def allows_empty_set() -> bool:
        return False

    def save_expression_set(self, ctx, params):
        self.set_interface._check_save_set_params(params)
        self._validate_save_set_data(params)

        save_result = self.set_interface.save_set(
            "KBaseSets.ExpressionSet", ctx["provenance"], params
        )
        info = save_result[0]
        return {
            "set_ref": info_to_ref(info),
            "set_info": info,
        }

    def _validate_save_set_data(self, params):
        if params.get("data") is None:
            err_msg = param_required("data")
            raise ValueError(err_msg)

        if "items" not in params["data"]:
            raise ValueError(list_required("items"))

        if not params["data"].get("items"):
            raise ValueError(no_items(self.set_type()))

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

        # Get all the genome ids from our Expression references (it's the genome_id key in
        # the object metadata). Make a set out of them.
        # If there's 0 or more than 1 item in the set, then either those items are bad, or they're
        # aligned against different genomes.
        ref_list = [{"ref": ref} for ref in seen_refs]
        info = self.workspace_client.get_object_info3(
            {"objects": ref_list, "includeMetadata": 1}
        )
        num_genomes = len({item[10]["genome_id"] for item in info["infos"]})
        if num_genomes != 1:
            err_msg = same_ref(self.set_type())
            raise ValueError(err_msg)

    def get_expression_set(self, ctx, params):
        checked_params = self._check_get_set_params(params)

        obj_spec = build_ws_obj_selector(
            checked_params["ref"], checked_params[REF_PATH_TO_SET]
        )
        info = self.workspace_client.get_object_info3({"objects": [obj_spec]})
        set_type = info["infos"][0][2]

        if "KBaseSets" in set_type:
            # If it's a KBaseSets type, then we know the usual interface will work...
            return self.set_interface.get_set(**checked_params)

        # get_rnaseq_expression_set
        # ...otherwise, we need to fetch it directly from the workspace and tweak it into the
        # expected return object

        obj_data = self.workspace_client.get_objects2({"objects": [obj_spec]})["data"][
            0
        ]

        obj = obj_data["data"]
        obj_info = obj_data["info"]

        if "sample_expression_ids" in obj:
            expression_ref_list = obj["sample_expression_ids"]
        else:
            alignments_to_expressions = obj.get("mapped_expression_ids")

            refs = set()
            for mapping in alignments_to_expressions:
                refs.update(list(mapping.values()))
            expression_ref_list = list(refs)

        expression_items = [{"ref": i} for i in expression_ref_list]

        item_infos = self.workspace_client.get_object_info3(
            {"objects": expression_items, "includeMetadata": 1}
        )["infos"]
        for idx, _ in enumerate(expression_items):
            expression_items[idx]["label"] = item_infos[idx][10].get("condition")
            if checked_params[INC_ITEM_INFO]:
                expression_items[idx]["info"] = item_infos[idx]

        if checked_params[INC_ITEM_REF_PATHS]:
            populate_item_object_ref_paths(expression_items, obj_spec)

        # retrofit missing description / item count
        obj_info[10]["description"] = ""
        obj_info[10]["item_count"] = str(len(expression_items))

        return {
            "data": {"items": expression_items, "description": ""},
            "info": obj_info,
        }

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
