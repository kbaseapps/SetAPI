"""An interface for handling sample sets."""

import traceback
from pprint import pprint

from SetAPI.util import convert_workspace_param, dfu_get_obj_data, info_to_ref


class SampleSetInterface:
    def __init__(self, workspace_client):
        self.ws_client = workspace_client

    def _check_condition_matching(self, conditionset_ref, matching_conditions):
        conditionset_data = dfu_get_obj_data(conditionset_ref)
        conditions = list(conditionset_data.get("conditions").keys())

        if not all(x in conditions for x in matching_conditions):
            error_msg = f"ERROR: Given conditions ({matching_conditions}) do not match ConditionSet conditions: {conditions}"
            raise ValueError(error_msg)

    def create_sample_set(self, ctx, params):
        # check the ws_id param to see if it is actually a ws_name to ensure
        # we use the right form of workspace identifier when saving
        ws_params = convert_workspace_param({"workspace": params.get("ws_id")})

        params["sample_ids"] = []
        params["condition"] = []
        for item in params.get("sample_n_conditions", []):
            item_condition = item["condition"]
            if not isinstance(item_condition, (str | list)):
                err_msg = "ERROR: condition should be either a list or a string"
                raise ValueError(err_msg)

            if isinstance(
                item_condition, list
            ):  # Auto populate UI puts input into an array
                if len(item_condition) > 1:
                    err_msg = "ERROR: please only select 1 condition per reads object"
                    raise ValueError(err_msg)
                item["condition"] = item_condition[0]

            params["sample_ids"].extend(item["sample_id"])

            params["condition"].extend([item["condition"] for i in item["sample_id"]])
        pprint(params)
        ### Create the working dir for the method; change it to a function call
        out_obj = {k: v for k, v in params.items() if k not in ("ws_id",)}

        sample_ids = params["sample_ids"]
        out_obj["num_samples"] = len(sample_ids)
        ## Validation to check if the Set contains more than one samples
        if len(sample_ids) < 2:
            err_msg = "This method takes two (2) or more RNASeq Samples. \
                If you have only one read sample, run either 'Align Reads using Tophat' or 'Align Reads using Bowtie2' directly for getting alignment"

            raise ValueError(err_msg)

        ## Validation to Check if the number of samples is equal to number of condition
        if len(params["condition"]) != out_obj["num_samples"]:
            err_msg = "Please specify a treatment label for each sample in the RNA-seq SampleSet. Please enter the same label for the replicates in a sample type"
            raise ValueError(err_msg)

        ## Validation to Check if the user is loading the same type as specified above
        if params["Library_type"] == "PairedEnd":
            lib_type = [
                "KBaseAssembly.PairedEndLibrary",
                "KBaseFile.PairedEndLibrary",
            ]
        else:
            lib_type = [
                "KBaseAssembly.SingleEndLibrary",
                "KBaseFile.SingleEndLibrary",
            ]
        sample_refs = []
        for reads_ref in sample_ids:
            # TODO: batch the ws calls instead of doing one sample at a time
            reads_info = self.ws_client.get_object_info3(
                {"objects": [{"ref": reads_ref}]}
            )["infos"][0]
            sample_refs.append(info_to_ref(reads_info))
            obj_type = reads_info[2].split("-")[0]
            if obj_type not in lib_type:
                err_msg = f"Library_type mentioned: {params['Library_type']}. Please add only {params['Library_type']} typed objects in Reads fields"
                raise ValueError(err_msg)

        ## Code to Update the Provenance; make it a function later
        provenance = ctx.get("provenance", [{}])
        # add additional info to provenance here, in this case the input data object reference
        provenance[0]["input_ws_objects"] = sample_refs

        # Saving RNASeqSampleSet to Workspace
        print(f"Saving {params['sampleset_id']} object to workspace")

        try:
            res = self.ws_client.save_objects(
                {
                    **ws_params,
                    "objects": [
                        {
                            "type": "KBaseRNASeq.RNASeqSampleSet",
                            "data": out_obj,
                            "name": out_obj["sampleset_id"],
                            "provenance": provenance,
                        }
                    ],
                }
            )[0]

            pprint(
                {
                    "set_ref": info_to_ref(res),
                    "set_info": res,
                }
            )

            return {
                "set_ref": info_to_ref(res),
                "set_info": res,
            }

        except Exception as e:
            err_msg = f"Error saving the object to workspace {params['sampleset_id']},{''.join(traceback.format_exc())}"

            raise Exception(err_msg) from e
