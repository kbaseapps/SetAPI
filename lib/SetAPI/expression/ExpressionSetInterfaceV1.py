"""
An interface for handling sets of Expression objects.
"""
from SetAPI import util
from SetAPI.generic.SetInterfaceV1 import SetInterfaceV1


class ExpressionSetInterfaceV1:
    def __init__(self, workspace_client):
        self.workspace_client = workspace_client
        self.set_interface = SetInterfaceV1(workspace_client)

    def save_expression_set(self, ctx, params):
        if 'data' in params and params['data'] is not None:
            self._validate_expression_set_data(params['data'])
        else:
            raise ValueError('"data" parameter field required to save an ExpressionSet')

        save_result = self.set_interface.save_set(
            'KBaseSets.ExpressionSet',
            ctx['provenance'],
            params
        )
        info = save_result[0]
        return {
            'set_ref': str(info[6]) + '/' + str(info[0]) + '/' + str(info[4]),
            'set_info': info
        }

    def _validate_expression_set_data(self, data):
        # Normalize the object, make empty strings where necessary
        if "description" not in data:
            data["description"] = ""

        if "items" not in data or len(data.get("items", [])) == 0:
            raise ValueError("An ExpressionSet must contain at "
                             "least one Expression object reference.")

        refs = list()
        for item in data["items"]:
            refs.append(item["ref"])
            if "label" not in item:
                item["label"] = ""

        ref_list = list([{"ref": r} for r in refs])

        # Get all the genome ids from our Expression references (it's the genome_id key in
        # the object metadata). Make a set out of them.
        # If there's 0 or more than 1 item in the set, then either those items are bad, or they're
        # aligned against different genomes.
        info = self.workspace_client.get_object_info3({"objects": ref_list, "includeMetadata": 1})
        num_genomes = len(set([item[10]["genome_id"] for item in info["infos"]]))
        if num_genomes == 0 or num_genomes > 1:
            raise ValueError("All Expression objects in the set must use "
                             "the same genome reference.")

    def get_expression_set(self, ctx, params):
        set_type, obj_spec = self._check_get_expression_set_params(params)

        include_item_info = False
        if 'include_item_info' in params:
            if params['include_item_info'] == 1:
                include_item_info = True

        include_set_item_ref_paths = False
        if 'include_set_item_ref_paths' in params:
            if params['include_set_item_ref_paths'] == 1:
                include_set_item_ref_paths = True

        ref_path_to_set = []
        if 'ref_path_to_set' in params:
            ref_path_to_set = params['ref_path_to_set']

        if "KBaseSets" in set_type:
            # If it's a KBaseSets type, then we know the usual interface will work...
            return self.set_interface.get_set(
                params['ref'],
                include_item_info,
                ref_path_to_set,
                include_set_item_ref_paths
            )
        else:
            # ...otherwise, we need to fetch it directly from the workspace and tweak it into the
            # expected return object

            obj_data = self.workspace_client.get_objects2({"objects": [obj_spec]})["data"][0]

            obj = obj_data["data"]
            obj_info = obj_data["info"]

            if "sample_expression_ids" in obj:
                expression_ref_list = obj["sample_expression_ids"]
            else:
                alignments_to_expressions = obj.get('mapped_expression_ids')

                refs = set()
                for mapping in alignments_to_expressions:
                    refs.update(list(mapping.values()))
                expression_ref_list = list(refs)

            expression_items = [{"ref": i} for i in expression_ref_list]

            item_infos = self.workspace_client.get_object_info3(
                {"objects": expression_items, "includeMetadata": 1})["infos"]
            for idx, ref in enumerate(expression_items):
                expression_items[idx]["label"] = item_infos[idx][10].get("condition", None)
                if include_item_info:
                    expression_items[idx]["info"] = item_infos[idx]
            """
            If include_set_item_ref_paths is set, then add a field ref_path in alignment items
            """
            if include_set_item_ref_paths:
                util.populate_item_object_ref_paths(expression_items, obj_spec)

            return {
                "data": {
                    "items": expression_items,
                    "description": ""
                },
                "info": obj_info
            }

    def _check_get_expression_set_params(self, params):
        if 'ref' not in params or params['ref'] is None:
            raise ValueError('"ref" parameter field specifiying the expression set is required')
        elif not util.check_reference(params['ref']):
            raise ValueError('"ref" parameter must be a valid workspace reference')
        if 'include_item_info' in params:
            if params['include_item_info'] not in [0, 1]:
                raise ValueError('"include_item_info" parameter field can only be set to 0 or 1')
        obj_spec = util.build_ws_obj_selector(params.get('ref'),
                                              params.get('ref_path_to_set', []))
        info = self.workspace_client.get_object_info3({"objects": [obj_spec]})

        return info["infos"][0][2], obj_spec
