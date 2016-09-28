


from biokbase.workspace.client import Workspace

from pprint import pprint




class SetInterfaceV1:


    def __init__(self, workspace_client):
        self.ws = workspace_client;

    def save_set(self, set_type, provenance, params):
        '''
        Save a set object to the Workspace using the set_type provided (e.g. set_type=KBaseSets.ReadsSet)
        '''
        self._check_save_set_params(params)
        save_params = self._build_ws_save_obj_params(set_type, provenance, params)
        results = self.ws.save_objects(save_params)
        return results


    def _check_save_set_params(self, params):
        if 'data' not in params:
            raise ValueError('"data" parameter field specifiying the set is required')
        if 'workspace_id' not in params and 'workspace_name' not in params:
            raise ValueError('"workspace_id" or "workspace_name" parameter fields specifiying the workspace is required')
        if 'output_object_name' not in params:
            raise ValueError('"output_object_name" parameter field is required')


    def _build_ws_save_obj_params(self, set_type, provenance, params):

        save_params = {
            'objects': [{
                'name': params['output_object_name'],
                'data': params['data'],
                'type': set_type,
                'provenance': provenance,
                'hidden': 0
            }]
        }

        if 'workspace_name' in params:
            save_params['workspace'] = params['workspace_name']
        else:
            save_params['id'] = params['workspace_id']

        return save_params



    def get_set(self, ref, include_item_info=False, ref_path_to_set=[]):
        '''
        Get a set object from the Workspace using the set_type provided (e.g. set_type=KBaseSets.ReadsSet)
        '''
        ws_data = self._get_set_from_ws(ref, ref_path_to_set)

        if include_item_info:
            self._populate_item_object_info(ws_data['data'], ref_path_to_set)

        return ws_data
    



    def _get_set_from_ws(self, ref, ref_path_to_set):

        # typedef structure {
        #     list<ObjectSpecification> objects;
        #     boolean ignoreErrors;
        #     boolean no_data;
        # } GetObjects2Params;
        selector = self._build_ws_obj_selector(ref, ref_path_to_set)
        ws_data = self.ws.get_objects2({'objects': [selector] })
        pprint(ws_data)

        data = ws_data['data'][0]['data']
        info = ws_data['data'][0]['info']

        return { 'data': data, 'info': info }



    def _populate_item_object_info(self, set_data):

        pass


    def _build_ws_obj_selector(self, ref, ref_path_to_set):
        if ref_path_to_set and len(ref_path_to_set)>0:
            obj_ref_path = []
            for r in ref_path_to_set[1:]:
                obj_ref_path.append(r)
            obj_ref_path.append(ref)
            return {
                'ref': ref_path_to_genome[0],
                'obj_ref_path':obj_ref_path
            }
        return { 'ref': ref } 


