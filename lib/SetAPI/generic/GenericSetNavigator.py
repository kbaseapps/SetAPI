# -*- coding: utf-8 -*-

import time


from Workspace.WorkspaceClient import Workspace

from pprint import pprint

from SetAPI.generic.WorkspaceListObjectsIterator import WorkspaceListObjectsIterator


class GenericSetNavigator:


    SET_TYPES = ['KBaseSets.ReadsSet']
    DEBUG = False


    def __init__(self, workspace_client, data_palette_cache=None, token=None):
        self.ws = workspace_client
        self.dpc = data_palette_cache
        self.token = token

    def list_sets(self, params):
        '''
        Get a list of the top-level sets (that is, sets that are unreferenced by
        any other sets in the specified workspace). Set item references are always
        returned, ws info for each of those items can optionally be included too.
        '''
        t1 = time.time()
        self._validate_list_params(params)

        workspace = params.get('workspace')
        workspaces = params.get('workspaces')
        include_metadata = params.get('include_metadata', 0)
        if not workspaces:
            workspaces = [str(workspace)]
        [all_sets, raw_dp, raw_dp_refs] = self._list_all_sets(workspaces, include_metadata)
        t2 = time.time()
        all_sets = self._populate_set_refs(all_sets)

        # the top level sets list includes not just the set info, but
        # the list of obj refs contained in each of those sets
        top_level_sets = self._get_top_level_sets(all_sets)

        if 'include_set_item_info' in params and params['include_set_item_info']==1:
            top_level_sets = self._populate_set_item_info(top_level_sets)

        if self.DEBUG:
            print("Time of populate_sets: " + str(time.time() - t2))
            print("Total time of list_sets: " + str(time.time() - t1))

        ret = {'sets': top_level_sets}
        include_raw_data_palettes = params.get('include_raw_data_palettes', 0)
        if include_raw_data_palettes == 1:
            ret['raw_data_palettes'] = raw_dp
            ret['raw_data_palette_refs'] = raw_dp_refs
        return ret


    def _validate_list_params(self, params):
        if ('workspace' not in params) and ('workspaces' not in params):
            raise ValueError('One of "workspace" or "workspaces" field required to list sets')

        if 'include_set_item_info' in params and params['include_set_item_info'] is not None:
            if params['include_set_item_info'] not in [0,1]:
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
            print("Time of ws_info listing: " + str(time.time() - t1))
        
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
            print("Time of object info listing: " + str(time.time() - t2))
        
        t3 = time.time()
        [dp_info_list, raw_dp, raw_dp_refs] = self._list_from_data_palette(
                workspaces, GenericSetNavigator.SET_TYPES, include_metadata)
        for dp_info in dp_info_list:
            s = dp_info['info']
            dp_ref = dp_info['dp_ref']
            ref = self._build_obj_ref(s)
            if ref not in processed_refs:
                sets.append({'ref': ref, 'info': s, 'dp_ref': dp_ref})
                processed_refs[ref] = True
        if self.DEBUG:
            print("Time of data palette loading: " + str(time.time() - t3))

        return [sets, raw_dp, raw_dp_refs]


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

        if len(objects)>0:
            obj_data = self.ws.get_objects2({
                    'objects':objects,
                    'no_data':1
                })['data']

            # if ws call worked, then len(obj_data)==len(set_list)
            for k in range(0,len(obj_data)):
                items = []
                for item_ref in obj_data[k]['refs']:
                    items.append({'ref':item_ref})
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

        if len(objects)>0:
            obj_info_list = self.ws.get_object_info_new({
                                        'objects':objects,
                                        'includeMetadata':1
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

        return { 'sets': set_list }


    def _validate_get_set_items_params(self, params):
        if 'set_refs' not in params:
            raise ValueError('"set_refs" field providing list of refs to sets is required to get_set_items')
        for s in params['set_refs']:
            if 'ref' not in s:
                raise ValueError('"ref" field in each object of "set_refs" list is required')



    def _get_set_info(self, set_refs):

        objects = []
        for s in set_refs:
            if 'path_to_set' in s and s['path_to_set'] is not None and len(s['path_to_set'])>0:
                obj_ref_path = s['path_to_set'][1:]
                obj_ref_path.append(s['ref'])
                objects.append({
                        'ref': s['path_to_set'][0],
                        'obj_ref_path': obj_ref_path
                    })
            else:
                objects.append({'ref':s['ref']})

        if len(objects)>0:
            obj_info_list = self.ws.get_object_info_new({
                                        'objects':objects,
                                        'includeMetadata':1
                                    })
            set_list = []
            for o in obj_info_list:
                set_list.append({
                        'ref': self._build_obj_ref(o),
                        'info': o
                    })
        return set_list


    def _list_from_data_palette(self, workspaces, type_list, include_metadata):
        if not self.dpc:
            raise ValueError("'data_palette_client' parameter is not set in GenericSetNavigator")
        type_map = {obj_type: True for obj_type in type_list}
        dp_info_list = []
        dp_ret = self.dpc.call_method('list_data', [{'workspaces': workspaces,
                                                     'include_metadata': include_metadata}], self.token)
        for item in dp_ret['data']:
            info = item['info']
            obj_type = info[2].split('-')[0]
            if obj_type in type_map:
                dp_info_list.append({'info': info, 'dp_ref': item['dp_ref']})
        return [dp_info_list, dp_ret['data'], dp_ret['data_palette_refs']]


    # def _populate_set_item_info(self, set_list):

    #     # keys are refs to items, values are a ref to one of the
    #     # sets that they are in.  We build a lookup here first so that
    #     # we don't duplicate items in the ws call, but depending
    #     # on the set composition it may be cheaper to omit this
    #     # check and build the objects call directly with duplicates
    #     item_refs = {}
    #     for s in set_list:
    #         for i in s['items']:
    #             item_refs[i['ref']] = s['ref']

    #     objects = []
    #     for ref in item_refs:
    #         objects.append({
    #                 'ref': item_refs[ref],
    #                 'obj_ref_path': [ref]
    #             })

    #     obj_info_list = self.ws.get_object_info_new({
    #                                 'objects':objects,
    #                                 'includeMetadata':1
    #                             })

    #     # build info lookup
    #     item_info = {}
    #     for o in obj_info_list:
    #         item_info[self._build_obj_ref(o)] = o

    #     for s in set_list:
    #         for item in s['items']:
    #             if item['ref'] in item_info:
    #                 item['info'] = item_info[item['ref']]

    #     return set_list


    # def _check_save_set_params(self, params):
    #     if 'data' not in params:
    #         raise ValueError('"data" parameter field specifiying the set is required')
    #     if 'workspace_id' not in params and 'workspace_name' not in params:
    #         raise ValueError('"workspace_id" or "workspace_name" parameter fields specifiying the workspace is required')
    #     if 'output_object_name' not in params:
    #         raise ValueError('"output_object_name" parameter field is required')


    # def _build_ws_save_obj_params(self, set_type, provenance, params):

    #     save_params = {
    #         'objects': [{
    #             'name': params['output_object_name'],
    #             'data': params['data'],
    #             'type': set_type,
    #             'provenance': provenance,
    #             'hidden': 0
    #         }]
    #     }

    #     if 'workspace_name' in params:
    #         save_params['workspace'] = params['workspace_name']
    #     else:
    #         save_params['id'] = params['workspace_id']

    #     return save_params



    # def get_set(self, ref, include_item_info=False, ref_path_to_set=[]):
    #     '''
    #     Get a set object from the Workspace using the set_type provided (e.g. set_type=KBaseSets.ReadsSet)
    #     '''
    #     ws_data = self._get_set_from_ws(ref, ref_path_to_set)

    #     if include_item_info:
    #         self._populate_item_object_info(ws_data, ref_path_to_set)

    #     return ws_data
    


    # def _get_set_from_ws(self, ref, ref_path_to_set):

    #     # typedef structure {
    #     #     list<ObjectSpecification> objects;
    #     #     boolean ignoreErrors;
    #     #     boolean no_data;
    #     # } GetObjects2Params;
    #     selector = self._build_ws_obj_selector(ref, ref_path_to_set)
    #     ws_data = self.ws.get_objects2({'objects': [selector] })

    #     data = ws_data['data'][0]['data']
    #     info = ws_data['data'][0]['info']

    #     return { 'data': data, 'info': info }



    # def _populate_item_object_info(self, set, ref_path_to_set):

    #     info = set['info']
    #     items = set['data']['items']
    #     set_ref = str(info[6]) + '/' + str(info[0]) + '/' + str(info[4])
    #     ref_path_to_item = ref_path_to_set + [set_ref]

    #     objects = []
    #     for item in items:
    #         objects.append(
    #             self._build_ws_obj_selector(item['ref'], ref_path_to_item))

    #     obj_info_list = self.ws.get_object_info_new({
    #                                 'objects': objects,
    #                                 'includeMetadata': 1 })

    #     for k in range(0, len(obj_info_list)):
    #         items[k]['info'] = obj_info_list[k]


    # def _build_ws_obj_selector(self, ref, ref_path_to_set):
    #     if ref_path_to_set and len(ref_path_to_set)>0:
    #         obj_ref_path = []
    #         for r in ref_path_to_set[1:]:
    #             obj_ref_path.append(r)
    #         obj_ref_path.append(ref)
    #         return {
    #             'ref': ref_path_to_set[0],
    #             'obj_ref_path':obj_ref_path
    #         }
    #     return { 'ref': ref } 


