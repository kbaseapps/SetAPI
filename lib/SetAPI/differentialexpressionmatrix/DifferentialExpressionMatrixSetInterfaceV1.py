"""
An interface for handling sets of Expression objects.
"""
from SetAPI.generic.SetInterfaceV1 import SetInterfaceV1
from SetAPI.util import check_reference


class DifferentialExpressionMatrixSetInterfaceV1:
    def __init__(self, workspace_client):
        self.workspace_client = workspace_client
        self.set_interface = SetInterfaceV1(workspace_client)

    def save_differential_expression_matrix_set(self, ctx, params):
        if 'data' in params and params['data'] is not None:
            self._validate_differential_expression_matrix_set_data(params['data'])
        else:
            raise ValueError('"data" parameter field required to save a DifferentialExpressionMatrixSet')

        save_result = self.set_interface.save_set(
                'KBaseSets.DifferentialExpressionMatrixSet',
                ctx['provenance'],
                params
            )
        info = save_result[0]
        return {
            'set_ref': str(info[6]) + '/' + str(info[0]) + '/' + str(info[4]),
            'set_info': info
        }

    def _validate_differential_expression_matrix_set_data(self, data):
        # Normalize the object, make empty strings where necessary
        if "description" not in data:
            data["description"] = ""

        if "items" not in data or len(data.get("items", [])) == 0:
            raise ValueError("A DifferentialExpressionMatrixSet must contain at "
                             "least one DifferentialExpressionMatrix object reference.")

        refs = list()
        for item in data["items"]:
            refs.append(item["ref"])
            if "label" not in item:
                item["label"] = ""

        ref_list = list(map(lambda r: {"ref": r}, refs))

        # Get all the genome ids from our DifferentialExpressionMatrix references (it's the
        # Genome key in the object metadata). Make a set out of them.
        # If there's more than 1 item in the set, then either those items are bad, or they're
        # aligned against different genomes.
        info = self.workspace_client.get_object_info3({"objects": ref_list, "includeMetadata": 1})
        num_genomes = len(set([item[10].get("Genome", None) for item in info["infos"]]))
        if num_genomes > 1:
            raise ValueError("All Differential Expression Matrix objects in the set must use "
                             "the same genome reference.")

    def get_differential_expression_matrix_set(self, ctx, params):
        self._check_get_differential_expression_matrix_set_params(params)

        include_item_info = False
        if 'include_item_info' in params:
            if params['include_item_info'] == 1:
                include_item_info = True

        ref_path_to_set = []
        if 'ref_path_to_set' in params:
            ref_path_to_set = params['ref_path_to_set']

        set_data = self.set_interface.get_set(
                params['ref'],
                include_item_info,
                ref_path_to_set
            )
        return set_data

    def _check_get_differential_expression_matrix_set_params(self, params):
        if 'ref' not in params or params['ref'] is None:
            raise ValueError('"ref" parameter field specifiying the DifferentialExpressionMatrix set is required')
        elif not check_reference(params['ref']):
            raise ValueError('"ref" parameter must be a valid workspace reference')
        if 'include_item_info' in params:
            if params['include_item_info'] not in [0, 1]:
                raise ValueError('"include_item_info" parameter field can only be set to 0 or 1')
