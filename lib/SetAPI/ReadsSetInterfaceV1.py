


from SetAPI.SetInterfaceV1 import SetInterfaceV1

from biokbase.workspace.client import Workspace

from pprint import pprint



class ReadsSetInterfaceV1:


    def __init__(self, workspace_client):
        self.set = SetInterfaceV1(workspace_client)

    def save_reads_set(self, ctx, params):
        save_result = self.set.save_set(
                'KBaseSets.ReadsSet',
                ctx['provenance'],
                params
            )
        info = save_result[0]
        return {
            'set_ref': str(info[6]) + '/' + str(info[0]) + '/' + str(info[4]),
            'set_info': info
        }


    def get_reads_set(self, ctx, params):
        self._check_get_reads_set_params(params)

        include_item_info = False
        if 'include_item_info' in params:
            if params['include_item_info'] == 1:
                include_item_info = True

        ref_path_to_set = None
        if 'ref_path_to_set' in params:
            ref_path_to_set = params['ref_path_to_set']

        return self.set.get_set(
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

