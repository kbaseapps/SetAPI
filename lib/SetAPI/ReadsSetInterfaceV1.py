


from SetAPI.SetInterfaceV1 import SetInterfaceV1

from biokbase.workspace.client import Workspace

from pprint import pprint



class ReadsSetInterfaceV1:


    def __init__(self, workspace_client):
        self.ws = workspace_client
        self.setInterface = SetInterfaceV1(workspace_client)

    def save_reads_set(self, ctx, params):
        if 'data' in params:
            self._validate_reads_set_data(params['data'])
        else:
            raise ValueError('"data" parameter field required to save a ReadsSet')

        save_result = self.setInterface.save_set(
                'KBaseSets.ReadsSet',
                ctx['provenance'],
                params
            )
        info = save_result[0]
        return {
            'set_ref': str(info[6]) + '/' + str(info[0]) + '/' + str(info[4]),
            'set_info': info
        }




    def _validate_reads_set_data(self, data):

        info = set['info']
        items = set['data']['items']
        set_ref = str(info[6]) + '/' + str(info[0]) + '/' + str(info[4])
        ref_path_to_item = ref_path_to_set + [set_ref]

        objects = []
        for item in items:
            objects.append(
                self._build_ws_obj_selector(item['ref'], ref_path_to_item))

        obj_info_list = self.ws.get_object_info_new({
                                    'objects': objects,
                                    'includeMetadata': 1 })

        for k in range(0, len(obj_info_list)):
            items[k]['info'] = obj_info_list[k]
        pass



    def get_reads_set(self, ctx, params):
        self._check_get_reads_set_params(params)

        include_item_info = False
        if 'include_item_info' in params:
            if params['include_item_info'] == 1:
                include_item_info = True

        ref_path_to_set = []
        if 'ref_path_to_set' in params:
            ref_path_to_set = params['ref_path_to_set']

        return self.setInterface.get_set(
                params['ref'],
                include_item_info,
                ref_path_to_set
            )

    def _check_get_reads_set_params(self, params):
        if 'ref' not in params:
            raise ValueError('"ref" parameter field specifiying the reads set is required')
        if 'include_item_info' in params:
            if params['include_item_info'] not in [0,1]:
                raise ValueError('"include_item_info" parameter field can only be set to 0 or 1')

