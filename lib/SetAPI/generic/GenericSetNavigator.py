# -*- coding: utf-8 -*-

import time

from SetAPI.generic.WorkspaceListObjectsIterator import WorkspaceListObjectsIterator
from SetAPI.util import (
    info_to_ref,
    build_ws_obj_selector,
    populate_item_object_ref_paths,
)
from SetAPI.generic.constants import INC_ITEM_REF_PATHS, REF_PATH_TO_SET


class GenericSetNavigator:
    SET_TYPES = ["KBaseSets.ReadsSet"]
    DEBUG = False

    def __init__(self, workspace_client, token=None):
        self.ws = workspace_client
        self.token = token

    def list_sets(self, params):
        """
        Get a list of the top-level sets (that is, sets that are unreferenced by
        any other sets in the specified workspace). Set item references are always
        returned, ws info for each of those items can optionally be included too.

        params: dict with keys-
            workspace - string - workspace to search for sets
            workspaces - list<string> - list of workspaces to search for sets
            include_metadata - [0, 1], default=0 - if 1, get metadata for set items
            include_set_item_info [0, 1], default=0 - if 1, get Workspace object_info
                for each set item
            include_set_item_ref_paths [0, 1], default=0 - if 1, build ref paths for
                each set item returned

        returns: dict with key "sets"
            value: list of sets in the workspaces given by params
        """
        t1 = time.time()
        self._validate_list_params(params)

        workspace = params.get("workspace")
        workspaces = params.get("workspaces")
        include_metadata = params.get("include_metadata", 0)
        if not workspaces:
            workspaces = [str(workspace)]
        all_sets = self._list_all_sets(workspaces, include_metadata)
        t2 = time.time()
        all_sets = self._populate_set_refs(all_sets)

        # the top level sets list includes not just the set info, but
        # the list of obj refs contained in each of those sets
        top_level_sets = self._get_top_level_sets(all_sets)

        if params.get("include_set_item_info", 0) == 1:
            top_level_sets = self._populate_set_item_info(top_level_sets)

        if params.get(INC_ITEM_REF_PATHS, 0) == 1:
            top_level_sets = self._populate_set_item_ref_path(top_level_sets)

        if self.DEBUG:
            print(("Time of populate_sets: " + str(time.time() - t2)))
            print(("Total time of list_sets: " + str(time.time() - t1)))

        ret = {"sets": top_level_sets}
        return ret

    def _validate_list_params(self, params):
        """
        Validates the parameters set to list_sets.
        Rules:
        1. At least one of workspace and workspaces must be present as keys. If
           both are missing, raise a ValueError
        2. include_set_item_info must be 0 or 1 if present
        """
        if "workspace" not in params and "workspaces" not in params:
            raise ValueError(
                'One of "workspace" or "workspaces" field required to list sets'
            )

        if params.get("include_set_item_info", 0) not in [0, 1]:
            raise ValueError('"include_set_item_info" field must be set to 0 or 1')

    def _list_all_sets(self, workspaces, include_metadata):
        """
        Inputs:
        workspaces - list<string> - list of workspaces to search for sets
        include_metadata - [0,1] default=0 - get object metadata or not

        Outputs:
        list of sets where each set is a dict with 2 keys:
        ref - workspace reference (wsid/objid/ver)
        info - workspace object info tuple
        """
        ws_info_list = []
        t1 = time.time()
        if len(workspaces) == 1:
            # If just one workspaces, just fetch the one
            ws = workspaces[0]
            list_params = {}
            if str(ws).isdigit():
                list_params["id"] = int(ws)
            else:
                list_params["workspace"] = str(ws)
            ws_info_list.append(self.ws.get_workspace_info(list_params))
        else:
            # If > 1 workspace, it's faster to grab all workspaces the
            # user has access to and filter down to what's in the list
            ws_map = {key: True for key in workspaces}
            for ws_info in self.ws.list_workspace_info({"perm": "r"}):
                if ws_info[1] in ws_map or str(ws_info[0]) in ws_map:
                    ws_info_list.append(ws_info)
        if self.DEBUG:
            print(("Time of ws_info listing: " + str(time.time() - t1)))

        t2 = time.time()
        sets = [
            {"ref": info_to_ref(s), "info": s}
            for t in GenericSetNavigator.SET_TYPES
            for s in WorkspaceListObjectsIterator(
                self.ws,
                list_objects_params={"includeMetadata": include_metadata, "type": t},
                ws_info_list=ws_info_list,
            )
        ]

        if self.DEBUG:
            print(("Time of object info listing: " + str(time.time() - t2)))
        return sets

    def _get_top_level_sets(self, set_list):
        """
        Assumes set_list items are populated, kicks out any set that
        is directly referenced by another set on the list.

        set_list = list of dicts with keys
        ref - Workspace object reference

        """

        # create lookup hash for the sets
        set_ref_lookup = {}
        for s in set_list:
            set_ref_lookup[s["ref"]] = 1

        # create a lookup to identify non-root sets
        sets_referenced_by_another_set = {}
        for s in set_list:
            for i in s["items"]:
                if i["ref"] in set_ref_lookup:
                    sets_referenced_by_another_set[i["ref"]] = 1

        # only add the sets that are root in this WS
        top_level_sets = []
        for s in set_list:
            if s["ref"] in sets_referenced_by_another_set:
                continue
            top_level_sets.append(s)

        return top_level_sets

    def _populate_set_refs(self, set_list):
        """
        Given a list of sets, go fetch their items and attach them
        to the original list.

        Has a side effect of updating the input set_list.

        set_list = list<dict> where each item has (at least) keys:
        * ref - Workspace object reference for the set object

        updates each item to have a key "items" containing a list
        of Workspace object references in no particular order.
        """
        objects = []
        for s in set_list:
            objects.append({"ref": s["ref"]})

        if len(objects) > 0:
            obj_data = self.ws.get_objects2({"objects": objects, "no_data": 1})["data"]

            # if ws call worked, then len(obj_data)==len(set_list)
            for k in range(0, len(obj_data)):
                items = []
                for item_ref in obj_data[k]["refs"]:
                    items.append({"ref": item_ref})
                set_list[k]["items"] = items

        return set_list

    def _populate_set_item_info(self, set_list):
        # keys are refs to items, values are a ref to one of the
        # sets that they are in.  We build a lookup here first so that
        # we don't duplicate items in the ws call, but depending
        # on the set composition it may be cheaper to omit this
        # check and build the objects call directly with duplicates
        item_refs = {}
        for s in set_list:
            for i in s["items"]:
                set_ref = s["ref"]
                item_refs[i["ref"]] = set_ref

        objects = []
        for ref in item_refs:
            objects.append({"ref": item_refs[ref] + ";" + ref})

        if len(objects) > 0:
            obj_info_list = self.ws.get_object_info_new(
                {"objects": objects, "includeMetadata": 1}
            )
            # build info lookup
            item_info = {}
            for o in obj_info_list:
                item_info[info_to_ref(o)] = o

            for s in set_list:
                for item in s["items"]:
                    if item["ref"] in item_info:
                        item["info"] = item_info[item["ref"]]

        return set_list

    def _populate_set_item_ref_path(self, set_list):
        for s in set_list:
            obj_spec = build_ws_obj_selector(s["ref"], s.get(REF_PATH_TO_SET, []))
            populate_item_object_ref_paths(s["items"], obj_spec)

        return set_list

    # typedef structure {
    #     ws_obj_id ref;
    #     list <ws_obj_id> path_to_set;
    # } SetReference;

    # typedef structure {
    #     list <SetReference> SetReference;
    # } GetSetItemsParams;

    # typedef structure {
    #     list <SetInfo> sets;
    # } GetSetItemsResult;

    def get_set_items(self, params):
        """
        Given a list of references to set objects, get the list of items for each set
        with metadata.  NOTE: DOES NOT PRESERVE ORDERING OF ITEM LIST.

        params: dict with keys:
        * set_refs - list of Workspace refs to set objects
        * include_set_item_ref_paths - int (0 or 1). if 1, return the complete reference
            path (ws1/obj1/ver1;ws2/obj2/ver2; ... etc) for each set item

        outputs: dict with key "sets" with value = list of dicts. Each dict has keys:
        * ref - Workspace object ref
        * info - Workspace object info tuple
        * ref_path - reference path from set object to each item in the set
        * items - list of Workspace refs for each item in the set
        """
        self._validate_get_set_items_params(params)

        # get the set info for each set object
        set_list = self._get_set_info(params["set_refs"])
        # populate the list of items in each set
        set_list = self._populate_set_refs(set_list)
        # add the info for each set item in the list
        set_list = self._populate_set_item_info(set_list)

        if INC_ITEM_REF_PATHS in params and params[INC_ITEM_REF_PATHS] == 1:
            set_list = self._populate_set_item_ref_path(set_list)

        return {"sets": set_list}

    def _validate_get_set_items_params(self, params):
        if "set_refs" not in params:
            raise ValueError(
                '"set_refs" field providing list of refs to sets is required to get_set_items'
            )
        for s in params["set_refs"]:
            if "ref" not in s:
                raise ValueError(
                    '"ref" field in each object of "set_refs" list is required'
                )

    def _get_set_info(self, set_refs):
        objects = [
            build_ws_obj_selector(s["ref"], s.get("path_to_set", [])) for s in set_refs
        ]

        if objects:
            obj_info_list = self.ws.get_object_info_new(
                {"objects": objects, "includeMetadata": 1}
            )
            set_list = [{"ref": info_to_ref(o), "info": o} for o in obj_info_list]
        return set_list
