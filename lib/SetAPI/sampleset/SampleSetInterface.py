"""
An interface for handling sample sets
"""

import traceback
import os
from pprint import pprint
from SetAPI import util

class SampleSetInterface:

    def __init__(self, workspace_client):
        self.ws_client = workspace_client

    def _ws_get_ref(self, ws_id, obj_id):
        if '/' in obj_id:
            return obj_id
        else:
            info = self.ws_client.get_object_info_new({"objects": [{'name': obj_id, 'workspace': ws_id}]})[0]
            return "{0}/{1}/{2}".format(info[6], info[0], info[4])

    def _ws_get_obj_name(self, obj_id):
        info = self.ws_client.get_object_info_new({"objects": [{'ref': obj_id}]})[0]
        return info[1]

    def _check_condition_matching(self, conditionset_ref, matching_conditions):

        conditionset_data = util.dfu_get_obj_data(conditionset_ref)
        conditions = list(conditionset_data.get('conditions').keys())

        if not all([x in conditions for x in matching_conditions]):
            error_msg = 'ERROR: Given conditions ({}) '.format(matching_conditions)
            error_msg += 'are not matching ConditionSet conditions: {}'.format(conditions)
            raise ValueError(error_msg)

    def create_sample_set(self, ctx, params):

        params["sample_ids"] = []
        params["condition"] = []
        for item in params.get('sample_n_conditions', []):
            item_condition = item['condition']
            if not isinstance(item_condition, (str, list)):
                raise ValueError('ERROR: condition should be either a list or a string')

            if isinstance(item_condition, list): # Auto populate UI puts input into an array
                if len(item_condition) > 1:
                    raise ValueError('ERROR: please only select 1 condition per Reads')
                item['condition'] = item_condition[0]

            params["sample_ids"].extend(item['sample_id'])
            params["condition"].extend([item['condition'] for i in item['sample_id']])


        pprint(params)

        # conditionset_ref = params.get('conditionset_ref')
        # if conditionset_ref:
        #     self._check_condition_matching(conditionset_ref, params["condition"])
        # else:
        #     del params['conditionset_ref']
        try:
            ### Create the working dir for the method; change it to a function call
            out_obj = {k: v for k, v in params.items() if k not in ('ws_id',)}

            sample_ids = params["sample_ids"]
            out_obj['num_samples'] = len(sample_ids)
            ## Validation to check if the Set contains more than one samples
            if len(sample_ids) < 2:
                raise ValueError(
                    "This methods can only take 2 or more RNASeq Samples. \
                     If you have only one read sample, run either 'Align Reads using Tophat/Bowtie2' \
                     methods directly for getting alignment")

            ## Validation to Check if the number of samples is equal to number of condition
            if len(params["condition"]) != out_obj['num_samples']:
                raise ValueError(
                    "Please specify a treatment label for each sample in the RNA-seq SampleSet. \
                     Please enter the same label for the replicates in a sample type")

            ## Validation to Check if the user is loading the same type as specified above
            if params["Library_type"] == 'PairedEnd':
                lib_type = ['KBaseAssembly.PairedEndLibrary', 'KBaseFile.PairedEndLibrary']
            else:
                lib_type = ['KBaseAssembly.SingleEndLibrary', 'KBaseFile.SingleEndLibrary']
            for reads_ref in sample_ids:
                reads_info = self.ws_client.get_object_info3({'objects': [{"ref": reads_ref}]})
                obj_type = reads_info['infos'][0][2].split('-')[0]
                if not (obj_type in lib_type):
                    raise ValueError("Library_type mentioned : {0}. Please add only {1} typed objects in Reads fields".format(
                                      params["Library_type"], params["Library_type"]))

            ## Code to Update the Provenance; make it a function later
            provenance = [{}]
            if 'provenance' in ctx:
                provenance = ctx['provenance']
            # add additional info to provenance here, in this case the input data object reference
            provenance[0]['input_ws_objects'] = [self._ws_get_ref(params['ws_id'], sample) for sample in sample_ids]

            # Saving RNASeqSampleSet to Workspace
            print(("Saving {0} object to workspace".format(params['sampleset_id'])))
            res = self.ws_client.save_objects(
                {"workspace": params['ws_id'],
                 "objects": [{
                     "type": "KBaseRNASeq.RNASeqSampleSet",
                     "data": out_obj,
                     "name": out_obj['sampleset_id'],
                     "provenance": provenance}]
                 })[0]
            '''
            out_obj['sample_ids'] = [self._ws_get_obj_name(sample_id) for
                                     sample_id in params['sample_ids']]
            '''
            result = dict()
            result['set_ref'] = "{0}/{1}/{2}".format(res[6], res[0], res[4])
            result['set_info'] = res

            pprint(result)
            return result

        except Exception as e:
            raise Exception(
                "Error Saving the object to workspace {0},{1}".format(out_obj['sampleset_id'], "".join(traceback.format_exc())))
