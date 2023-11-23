from SetAPI import util


class SetInterfaceV1:
    def __init__(self, workspace_client):
        self.ws = workspace_client

    def save_set(self, set_type, provenance, params):
        """
        Save a set object to the Workspace using the set_type provided (e.g. set_type=KBaseSets.ReadsSet)
        """
        self._check_save_set_params(params)
        save_params = self._build_ws_save_obj_params(set_type, provenance, params)
        results = self.ws.save_objects(save_params)
        return results

    def _check_save_set_params(self, params):
        if "data" not in params:
            raise ValueError('"data" parameter field specifiying the set is required')
        if (
            "workspace" not in params
            and "workspace_id" not in params
            and "workspace_name" not in params
        ):
            raise ValueError(
                '"workspace" or "workspace_id" or "workspace_name" parameter field is required'
            )
        if "output_object_name" not in params:
            raise ValueError('"output_object_name" parameter field is required')

    def _build_ws_save_obj_params(self, set_type, provenance, params):
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
        ws_params = util.convert_workspace_param(params)
        return {**save_params, **ws_params}

    def get_set(
        self,
        ref,
        include_item_info=False,
        ref_path_to_set=[],
        include_set_item_ref_paths=False,
    ):
        """
        Get a set object from the Workspace using the set_type provided (e.g. set_type=KBaseSets.ReadsSet)
        """
        obj_selector = util.build_ws_obj_selector(ref, ref_path_to_set)
        ws_data = self._get_set_from_ws(obj_selector)

        if include_item_info:
            self._populate_item_object_info(ws_data, ref_path_to_set)

        if include_set_item_ref_paths:
            set_items = ws_data["data"]["items"]
            util.populate_item_object_ref_paths(set_items, obj_selector)

        return ws_data

    def _get_set_from_ws(self, selector):
        # typedef structure {
        #     list<ObjectSpecification> objects;
        #     boolean ignoreErrors;
        #     boolean no_data;
        # } GetObjects2Params;

        ws_data = self.ws.get_objects2({"objects": [selector]})

        return {"data": ws_data["data"][0]["data"], "info": ws_data["data"][0]["info"]}

    def _populate_item_object_info(self, set, ref_path_to_set):
        items = set["data"]["items"]

        objects = []
        for item in items:
            ref_path_to_item = ref_path_to_set + [item["ref"]]
            objects.append(util.build_ws_obj_selector(item["ref"], ref_path_to_item))

        if len(objects) > 0:
            obj_info_list = self.ws.get_object_info_new(
                {"objects": objects, "includeMetadata": 1}
            )

            for k in range(0, len(obj_info_list)):
                items[k]["info"] = obj_info_list[k]
