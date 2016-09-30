


from biokbase.workspace.client import Workspace

from pprint import pprint



class GenericSetNavigator:


    SET_TYPES = ['KBaseSets.ReadsSet']


    def __init__(self, workspace_client):
        self.ws = workspace_client



    # typedef structure {
    #     string workspace;
    #     boolean include_set_contents;
    # } ListSetParams;


    # typedef structure {
    #     ws_obj_id ref;
    #     Workspace.object_info info;
    # } SetItemInfo;

    # typedef structure {
    #     Workspace.object_info info;
    #     list<SetItemInfo> items;
    # } SetInfo;

    # typedef structure {
    #     list <SetInfo> sets;
    # } ListSetResult;

    # /* Use to get the top-level sets in a WS. Optionally can include
    # one level down members of those sets. */
    # funcdef list_sets(ListSetParams params)
    #             returns (ListSetResult result) authentication optional;

    def list_sets(self, params):

        self._validate_list_params(params)

        workspace = params['workspace']
        all_sets = self._list_all_sets(workspace)
        print('ALL SETS')
        pprint(all_sets)

        # the top level sets list includes not just the set info, but
        # the list of obj refs contained in each of those sets
        top_level_sets = self._get_top_level_sets(all_sets)

        return {}


    def _validate_list_params(self, params):
        if 'workspace' not in params:
            raise ValueError('"workspace" field required to list sets')


    def _list_all_sets(self, workspace):
        ws_info = self._get_workspace_info(workspace)
        max_id = ws_info[4]

        list_params = { 'includeMetadata': 1 }
        if str(workspace).isdigit():
            list_params['ids'] = [ int(workspace) ]
        else:
            list_params['workspaces'] = [workspace]

        sets = []
        for t in GenericSetNavigator.SET_TYPES:
            list_params['type'] = t
            sets.extend(self._list_until_exhausted(list_params, max_id))
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



    def _list_until_exhausted(self, options, max_id):
        min_id = 0
        step = 10000
        obj_info_list = []
        while min_id < max_id:
            options['minObjectID'] = min_id
            options['maxObjectID'] = min_id + step
            min_id = min_id + step
            result = self.ws.list_objects(options)
            obj_info_list.extend(result)
        return obj_info_list


    def _get_top_level_sets(self, set_list):

        set_refs = self._get_set_refs(set_list)
        return []




    def _get_set_refs(self, set_list):

        objects = []
        for s in set_list:
            objects.append({'ref': str(s[6]) + '/' + str(s[0]) + '/' + str(s[4]) })
        obj_data = self.ws.get_objects2({
                'objects':objects,
                'no_data':1
            })

        refs = []
        for d in obj_data['data']:
            refs.append(d['refs'])


        print(refs)


        return []








 # list<ws_name> workspaces;
 #        list<ws_id> ids;
 #        type_string type;
 #        permission perm;
 #        list<username> savedby;
 #        usermeta meta;
 #        timestamp after;
 #        timestamp before;
 #        epoch after_epoch;
 #        epoch before_epoch;
 #        obj_id minObjectID;
 #        obj_id maxObjectID;
 #        boolean showDeleted;
 #        boolean showOnlyDeleted;
 #        boolean showHidden;
 #        boolean showAllVersions;
 #        boolean includeMetadata;
 #        boolean excludeGlobal;
 #        int limit;





    def get_set_items(self, params):
        

        return {}


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


