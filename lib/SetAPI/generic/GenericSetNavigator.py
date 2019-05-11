# -*- coding: utf-8 -*-

import time

from SetAPI import util
from SetAPI.generic.WorkspaceListObjectsIterator import WorkspaceListObjectsIterator


class GenericSetNavigator:
    SET_TYPES = ['KBaseSets.ReadsSet']
    DEBUG = False

    def __init__(self, workspace_client, token=None):
        self.ws = workspace_client
        self.token = token

    def list_sets(self, params):
        """
        Get a list of the top-level sets (that is, sets that are unreferenced by
        any other sets in the specified workspace). Set item references are always
        returned, ws info for each of those items can optionally be included too.
        """
        t1 = time.time()
        self._validate_list_params(params)

        workspace = params.get('workspace')
        workspaces = params.get('workspaces')
        include_metadata = params.get('include_metadata', 0)
        if not workspaces:
            workspaces = [str(workspace)]
        all_sets = self._list_all_sets(workspaces, include_metadata)
        t2 = time.time()
        all_sets = self._populate_set_refs(all_sets)

        # the top level sets list includes not just the set info, but
        # the list of obj refs contained in each of those sets
        top_level_sets = self._get_top_level_sets(all_sets)

        if 'include_set_item_info' in params and params['include_set_item_info'] == 1:
            top_level_sets = self._populate_set_item_info(top_level_sets)

        if 'include_set_item_ref_paths' in params and params['include_set_item_ref_paths'] == 1:
            top_level_sets = self._populate_set_item_ref_path(top_level_sets)

        if self.DEBUG:
            print(("Time of populate_sets: " + str(time.time() - t2)))
            print(("Total time of list_sets: " + str(time.time() - t1)))

        ret = {'sets': top_level_sets}
        return ret

    def _validate_list_params(self, params):
        if ('workspace' not in params) and ('workspaces' not in params):
            raise ValueError('One of "workspace" or "workspaces" field required to list sets')

        if 'include_set_item_info' in params and params['include_set_item_info'] is not None:
            if params['include_set_item_info'] not in [0, 1]:
                raise ValueError('"include_set_item_info" field must be set to 0 or 1')

    def _list_all_sets(self, workspaces, include_metadata):
        ws_info_list = []
        t1 = time.time()
        if len(workspaces) == 1:
            ws = workspaces[0]
            list_params = {}
            if str(ws).isdigit():
                list_params['id'] = int(ws)
            else:
                list_params['workspace'] = str(ws)
            ws_info_list.append(self.ws.get_workspace_info(list_params))
        else:
            ws_map = {key: True for key in workspaces}
            for ws_info in self.ws.list_workspace_info({'perm': 'r'}):
                if ws_info[1] in ws_map or str(ws_info[0]) in ws_map:
                    ws_info_list.append(ws_info)
        if self.DEBUG:
            print(("Time of ws_info listing: " + str(time.time() - t1)))

        t2 = time.time()
        sets = []
        processed_refs = {}
        for t in GenericSetNavigator.SET_TYPES:
            list_params = {'includeMetadata': include_metadata, 'type': t}
            for s in WorkspaceListObjectsIterator(self.ws, list_objects_params=list_params,
                                                  ws_info_list=ws_info_list):
                sets.append({'ref': self._build_obj_ref(s),
                             'info': s})
                ref = str(s[6]) + '/' + str(s[0]) + '/' + str(s[4])
                processed_refs[ref] = True
        if self.DEBUG:
            print(("Time of object info listing: " + str(time.time() - t2)))
        return sets

    def _get_workspace_info(self, workspace):
        # typedef tuple<ws_id 0:id, ws_name 1:workspace, username 2:owner, timestamp 3:moddate,
        # int 4max_objid, permission 5user_permission, permission 6globalread,
        # lock_status 7lockstat, usermeta 8metadata> workspace_info;
        ws_identity = {}
        if str(workspace).isdigit():
            ws_identity['id'] = int(workspace)
        else:
            ws_identity['workspace'] = workspace
        return self.ws.get_workspace_info(ws_identity)

    def _get_top_level_sets(self, set_list):
        '''
        Assumes set_list items are populated, kicks out any set that
        is directly referenced by another set on the list.
        '''

        # create lookup hash for the sets
        set_ref_lookup = {}
        for s in set_list:
            set_ref_lookup[s['ref']] = 1

        # create a lookup to identify non-root sets
        sets_referenced_by_another_set = {}
        for s in set_list:
            for i in s['items']:
                if i['ref'] in set_ref_lookup:
                    sets_referenced_by_another_set[i['ref']] = 1

        # only add the sets that are root in this WS
        top_level_sets = []
        for s in set_list:
            if s['ref'] in sets_referenced_by_another_set:
                continue
            top_level_sets.append(s)

        return top_level_sets

    def _populate_set_refs(self, set_list):

        objects = []
        for s in set_list:
            set_ref = s['ref']
            if 'dp_ref' in s:
                set_ref = s['dp_ref'] + ';' + set_ref
            objects.append({'ref': set_ref})

        if len(objects) > 0:
            obj_data = self.ws.get_objects2({
                'objects': objects,
                'no_data': 1
            })['data']

            # if ws call worked, then len(obj_data)==len(set_list)
            for k in range(0, len(obj_data)):
                items = []
                for item_ref in obj_data[k]['refs']:
                    items.append({'ref': item_ref})
                set_list[k]['items'] = items

        return set_list

    def _populate_set_item_info(self, set_list):

        # keys are refs to items, values are a ref to one of the
        # sets that they are in.  We build a lookup here first so that
        # we don't duplicate items in the ws call, but depending
        # on the set composition it may be cheaper to omit this
        # check and build the objects call directly with duplicates
        item_refs = {}
        for s in set_list:
            for i in s['items']:
                set_ref = s['ref']
                if 'dp_ref' in s:
                    set_ref = s['dp_ref'] + ';' + set_ref
                item_refs[i['ref']] = set_ref

        objects = []
        for ref in item_refs:
            objects.append({
                'ref': item_refs[ref] + ';' + ref
            })

        if len(objects) > 0:
            obj_info_list = self.ws.get_object_info_new({
                'objects': objects,
                'includeMetadata': 1
            })
            # build info lookup
            item_info = {}
            for o in obj_info_list:
                item_info[self._build_obj_ref(o)] = o

            for s in set_list:
                for item in s['items']:
                    if item['ref'] in item_info:
                        item['info'] = item_info[item['ref']]

        return set_list

    def _populate_set_item_ref_path(self, set_list):

        for s in set_list:
            obj_spec = util.build_ws_obj_selector(s['ref'],
                                                  s.get('ref_path_to_set', []))
            util.populate_item_object_ref_paths(s['items'], obj_spec)

        return set_list

    def _build_obj_ref(self, obj_info):
        return str(obj_info[6]) + '/' + str(obj_info[0]) + '/' + str(obj_info[4])

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
        '''
        Given a list of reference to set objects, get the list of items for each set
        with metadata.  NOTE: DOES NOT PRESERVE ORDERING OF ITEM LIST
        '''
        self._validate_get_set_items_params(params)

        set_list = self._get_set_info(params['set_refs'])

        set_list = self._populate_set_refs(set_list)
        set_list = self._populate_set_item_info(set_list)

        if 'include_set_item_ref_paths' in params and params['include_set_item_ref_paths'] == 1:
            set_list = self._populate_set_item_ref_path(set_list)

        return {'sets': set_list}

    def _validate_get_set_items_params(self, params):
        if 'set_refs' not in params:
            raise ValueError(
                '"set_refs" field providing list of refs to sets is required to get_set_items')
        for s in params['set_refs']:
            if 'ref' not in s:
                raise ValueError('"ref" field in each object of "set_refs" list is required')

    def _get_set_info(self, set_refs):

        objects = []
        for s in set_refs:
            objects.append(util.build_ws_obj_selector(s['ref'], s.get('path_to_set', [])))

        if len(objects) > 0:
            obj_info_list = self.ws.get_object_info_new({
                'objects': objects,
                'includeMetadata': 1
            })
            set_list = []
            for o in obj_info_list:
                set_list.append({
                    'ref': self._build_obj_ref(o),
                    'info': o
                })
        return set_list
