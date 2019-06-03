from SetAPI.generic.SetInterfaceV1 import SetInterfaceV1


class GenomeSetInterfaceV1:

    def __init__(self, workspace_client):
        self.ws = workspace_client
        self.setInterface = SetInterfaceV1(workspace_client)

    def save_genome_set(self, ctx, params):
        """
        by default save 'KBaseSets.GenomeSet'
        save 'KBaseSearch.GenomeSet' by setting save_search_set
        """
        save_search_set = params.get('save_search_set', False)

        if 'data' in params:
            self._validate_genome_set_data(params['data'], save_search_set)
        else:
            raise ValueError('"data" parameter field required to save an GenomeSet')

        genome_type = 'KBaseSets.GenomeSet'
        if save_search_set:
            genome_type = 'KBaseSearch.GenomeSet'

        save_result = self.setInterface.save_set(
            genome_type,
            ctx['provenance'],
            params
        )
        info = save_result[0]
        return {
            'set_ref': str(info[6]) + '/' + str(info[0]) + '/' + str(info[4]),
            'set_info': info
        }

    def _validate_genome_set_data(self, data, save_search_set):
        # TODO: add checks that only one copy of each genome data is in the set
        if save_search_set:
            if 'elements' not in data:
                raise ValueError('"elements" list must be defined in data to save an KBaseSearch.GenomeSet')

            if 'description' not in data:
                data['description'] = ''
        else:
            if 'items' not in data:
                raise ValueError('"items" list must be defined in data to save an KBaseSets.GenomeSet')

            # add 'description' and 'label' fields if not present in data:
            for item in data['items']:
                if 'label' not in item:
                    item['label'] = ''
            if 'description' not in data:
                data['description'] = ''

    def get_genome_set(self, ctx, params):
        self._check_get_genome_set_params(params)

        include_item_info = False
        if 'include_item_info' in params:
            if params['include_item_info'] == 1:
                include_item_info = True

        include_set_item_ref_paths = False
        if 'include_set_item_ref_paths' in params:
            if params['include_set_item_ref_paths'] == 1:
                include_set_item_ref_paths = True

        ref_path_to_set = []
        if 'ref_path_to_set' in params:
            ref_path_to_set = params['ref_path_to_set']

        set_data = self.setInterface.get_set(
            params['ref'],
            include_item_info,
            ref_path_to_set,
            include_set_item_ref_paths
        )
        set_data = self._normalize_genome_set_data(set_data)

        return set_data

    def _check_get_genome_set_params(self, params):
        if 'ref' not in params:
            raise ValueError('"ref" parameter field specifiying the genome  set is required')
        if 'include_item_info' in params:
            if params['include_item_info'] not in [0, 1]:
                raise ValueError('"include_item_info" parameter field can only be set to 0 or 1')

    def _normalize_genome_set_data(self, set_data):
        # make sure that optional/missing fields are filled in or are defined
        # TODO: populate empty description field
        # TODO?: populate empty label fields
        return set_data
