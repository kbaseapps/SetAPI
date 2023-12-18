"""The main interface for the Set API."""
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
from SetAPI.generic.constants import (
    ASSEMBLY,
    DIFFERENTIAL_EXPRESSION_MATRIX,
    EXPRESSION,
    FEATURE_SET,
    GENOME,
    GENOME_SEARCH,
    INC_ITEM_INFO,
    INC_ITEM_REF_PATHS,
    READS,
    READS_ALIGNMENT,
    REF_PATH_TO_SET,
    RNASEQ_SAMPLE,
    SAVE_SEARCH_SET,
    SET_ITEM_NAME_TO_SET_TYPE,
)
from SetAPI.rnaseq_set_functions import get_rnaseq_sample_set, get_rnaseq_set
from SetAPI.util import (
    build_ws_obj_selector,
    check_reference,
    convert_workspace_param,
    info_to_ref,
    populate_item_object_ref_paths,
)

ALLOWS_EMPTY_SETS = [ASSEMBLY, FEATURE_SET, GENOME, READS]

GENOME_REF_CHECKS = {
    DIFFERENTIAL_EXPRESSION_MATRIX: "Genome",
    EXPRESSION: "genome_id",
    READS_ALIGNMENT: "genome_id",
}

ALLOWS_ZERO_GENOMES = [DIFFERENTIAL_EXPRESSION_MATRIX]


class SetInterfaceV1:
    """The core interface for saving and retrieving sets."""

    def __init__(self: "SetInterfaceV1", workspace_client: Workspace) -> None:
        """Initialise the class.

        :param self: this class
        :type self: SetInterfaceV1
        :param workspace_client: workspace client
        :type workspace_client: Workspace
        """
        self.ws_client = workspace_client

    def save_set(
        self: "SetInterfaceV1",
        set_item_name: str,
        provenance: dict[str, Any],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Save a set to the workspace as the set type provided.

        :param self: this class
        :type self: SetInterfaceV1
        :param set_item_name: name of the objects in the set, e.g. "genome"
        :type set_item_name: str
        :param provenance: provenance
        :type provenance: dict[str, Any]
        :param params: parameters for the request
        :type params: dict[str, Any]
        :return: newly-created set item
        :rtype: dict[str, Any]
        """
        set_item_name = self._check_save_set_params(set_item_name, params)

        save_params = {
            "objects": [
                {
                    "name": params["output_object_name"],
                    "data": params["data"],
                    "type": SET_ITEM_NAME_TO_SET_TYPE[set_item_name],
                    "provenance": provenance,
                    "hidden": 0,
                }
            ]
        }
        ws_params = convert_workspace_param(params)

        save_result = self.ws_client.save_objects({**save_params, **ws_params})
        info = save_result[0]
        return {
            "set_ref": info_to_ref(info),
            "set_info": info,
        }

    def _check_save_set_params(
        self: "SetInterfaceV1", set_item_name: str, params: dict[str, Any]
    ) -> str:
        """Validate the params for saving a set.

        :param self: this class
        :type self: SetInterfaceV1
        :param set_item_name: name of the objects in the set, e.g. "genome"
        :type set_item_name: str
        :param params: set parameters
        :type params: dict[str, Any]
        :return set_item_name: possibly updated set_item_name parameter
        :rtype set_item_name: str
        """
        # check required params
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

        # this should not happen with the current API, but best to check
        if not set_item_name or set_item_name not in SET_ITEM_NAME_TO_SET_TYPE:
            err_msg = f"invalid set item name: {set_item_name}"
            raise ValueError(err_msg)

        # bail out early for RNASeqSampleSets
        if set_item_name == RNASEQ_SAMPLE:
            return set_item_name

        # convert the set item name into the set type
        save_search_set = params.get(SAVE_SEARCH_SET, False)
        if save_search_set and set_item_name == "genome":
            set_item_name = GENOME_SEARCH

        list_item_type = "elements" if save_search_set else "items"
        if list_item_type not in params["data"]:
            raise ValueError(list_required(list_item_type))

        if "description" not in params["data"]:
            params["data"]["description"] = ""

        # ensure that empty sets are only present in those set types
        # that allow them
        if set_item_name not in ALLOWS_EMPTY_SETS and not params["data"].get(
            list_item_type
        ):
            raise ValueError(no_items(SET_ITEM_NAME_TO_SET_TYPE[set_item_name]))

        if list_item_type == "elements":
            return set_item_name

        # add 'label' fields if not present in data:
        seen_refs = set()
        for item in params["data"]["items"]:
            if "label" not in item:
                item["label"] = ""
            if item["ref"] in seen_refs:
                raise ValueError(no_dupes())
            seen_refs.add(item["ref"])

        if set_item_name in GENOME_REF_CHECKS:
            self._check_genome_refs(seen_refs, set_item_name)

        return set_item_name

    def _check_genome_refs(
        self: "SetInterfaceV1", seen_refs: set[str], set_item_name: str
    ) -> None:
        """Ensure that the same genome is referenced by all set members.

        :param self: this class
        :type self: SetInterfaceV1
        :param seen_refs: deduplicated list of references
        :type seen_refs: set[str]
        :param set_item_name: name of the objects in the set, e.g. "genome"
        :type set_item_name: str
        :raises ValueError: if zero or more than one ref genomes have been used
        """
        genome_field_name = GENOME_REF_CHECKS[set_item_name]
        ref_list = [{"ref": ref} for ref in seen_refs]
        info_list = self.ws_client.get_object_info3(
            {"objects": ref_list, "includeMetadata": 1}
        )["infos"]
        num_genomes = len({item[10].get(genome_field_name) for item in info_list})
        # If more than 1 item in the set, then either those items are bad, or they're
        # aligned against different genomes.
        # If there are zero genomes in the set, check whether this set type allows
        # there to be no genome or not.
        if num_genomes != 1 and not (
            num_genomes == 0 and set_item_name in ALLOWS_ZERO_GENOMES
        ):
            raise ValueError(same_ref(SET_ITEM_NAME_TO_SET_TYPE[set_item_name]))

    def get_set(
        self: "SetInterfaceV1",
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Retrieve an object from the workspace.

        N.b. this method assumes that the object is a set, but it
        will happily retrieve other objects too.

        :param self: this class
        :type self: SetInterfaceV1
        :param params: dictionary of parameters for the request
        :type params: dict[str, Any]
        :return: set data
        :rtype: dict[str, Any]
        """
        checked_params = self._check_get_set_params(params)

        obj_selector = build_ws_obj_selector(
            checked_params["ref"], checked_params[REF_PATH_TO_SET]
        )

        resp = self.ws_client.get_objects2({"objects": [obj_selector]})
        set_data = {
            "data": resp["data"][0]["data"],
            "info": resp["data"][0]["info"],
        }
        kbase_set_type = set_data["info"][2]

        if "KBaseSets" not in kbase_set_type:
            return self._populate_non_kbase_set(
                obj_selector, kbase_set_type, set_data, checked_params
            )

        # not all sets have 'items' (e.g. KBaseSearch.GenomeSet);
        # if they don't, skip the following steps as they will error out
        if not set_data["data"].get("items", []):
            return set_data

        if checked_params[INC_ITEM_INFO]:
            self._populate_item_object_info(set_data, checked_params[REF_PATH_TO_SET])

        if checked_params[INC_ITEM_REF_PATHS]:
            set_items = set_data["data"]["items"]
            populate_item_object_ref_paths(set_items, obj_selector)

        return set_data

    def _check_get_set_params(
        self: "SetInterfaceV1", params: dict[str, Any]
    ) -> dict[str, Any]:
        """Perform basic validation on the get_set parameters.

        :param self: this class
        :type self: SetInterfaceV1
        :param params: parameters to the get_set function
        :type params: dict[str, Any]
        :return: validated parameters
        :rtype: dict[str, Any]
        """
        if not params.get("ref"):
            raise ValueError(param_required("ref"))

        if not check_reference(params["ref"]):
            raise ValueError(ref_must_be_valid())

        ref_path_to_set = params.get(REF_PATH_TO_SET) or []
        if ref_path_to_set:
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

    def _get_object_from_ws(
        self: "SetInterfaceV1", selector: dict[str, str]
    ) -> dict[str, Any]:
        """Retrieve an object from the workspace.

        :param self: this class
        :type self: SetInterfaceV1
        :param selector: object selector
        :type selector: dict[str, str]
        :return: object data and info from the workspace
        :rtype: dict[str, Any]
        """
        # typedef structure {
        #     list<ObjectSpecification> objects;
        #     boolean ignoreErrors;
        #     boolean no_data;
        # } GetObjects2Params;

        ws_data = self.ws_client.get_objects2({"objects": [selector]})

        return {"data": ws_data["data"][0]["data"], "info": ws_data["data"][0]["info"]}

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
        obj_info_dump = self.ws_client.get_object_info3(
            {"objects": objects, "includeMetadata": 1}
        )["infos"]

        for k in range(len(obj_info_dump)):
            items[k]["info"] = obj_info_dump[k]

    def _populate_non_kbase_set(
        self: "SetInterfaceV1",
        obj_selector: dict[str, str],
        kbase_set_type: str,
        obj_data: dict[str, Any],
        checked_params: dict[str, Any],
    ) -> dict[str, Any]:
        if "KBaseSearch" in kbase_set_type:
            # this doesn't get any love, sob!
            return obj_data

        if "Sample" in kbase_set_type:
            return get_rnaseq_sample_set(
                self.ws_client,
                obj_selector,
                obj_data,
                checked_params[INC_ITEM_INFO],
                checked_params[INC_ITEM_REF_PATHS],
            )

        # RNASeqAlignmentSet, RNASeqExpressionSet
        return get_rnaseq_set(
            self.ws_client,
            obj_selector,
            kbase_set_type,
            obj_data,
            checked_params[INC_ITEM_INFO],
            checked_params[INC_ITEM_REF_PATHS],
        )
