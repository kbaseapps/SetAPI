


from SetAPI.generic.SetInterfaceV1 import SetInterfaceV1

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
        # TODO: add checks that only one copy of each reads data is in the set
        # TODO?: add checks that reads data list is homogenous (no mixed single/paired-end libs)
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

        set_data = self.setInterface.get_set(
                params['ref'],
                include_item_info,
                ref_path_to_set
            )
        set_data = self._normalize_read_set_data(set_data)

        return set_data

    def _check_get_reads_set_params(self, params):
        if 'ref' not in params:
            raise ValueError('"ref" parameter field specifiying the reads set is required')
        if 'include_item_info' in params:
            if params['include_item_info'] not in [0,1]:
                raise ValueError('"include_item_info" parameter field can only be set to 0 or 1')


    def _normalize_read_set_data(self, set_data):
        # make sure that optional/missing fields are filled in or are defined
        # TODO: populate empty description field
        # TODO?: populate empty label fields
        return set_data



