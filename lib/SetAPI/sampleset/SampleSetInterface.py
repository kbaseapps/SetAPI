"""An interface for handling sample sets."""
from copy import deepcopy
from typing import Any

from installed_clients.WorkspaceClient import Workspace

from SetAPI.generic.SetInterfaceV1 import SetInterfaceV1


class SampleSetInterface:
    def __init__(self: "SampleSetInterface", workspace_client: Workspace):
        self.ws_client = workspace_client
        self.set_interface = SetInterfaceV1(workspace_client)

    @staticmethod
    def set_type() -> str:
        """The set type saved by this class."""
        return "KBaseRNASeq.RNASeqSampleSet"

    def create_sample_set(
        self: "SampleSetInterface", ctx: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Save a sample set to the workspace.

        :param self: this class
        :type self: SampleSetInterface
        :param ctx: KBase context
        :type ctx: dict[str, Any]
        :param params: request parameters
        :type params: dict[str, Any]
        :return: result of saving sampleset to the workspace
        :rtype: dict[str, Any]
        """
        output_object = deepcopy(params)

        # N.b. according to the spec, these are valid input params.
        # Just hope no one is trying to use them, eh?
        output_object["sample_ids"] = []
        output_object["condition"] = []
        for item in params.get("sample_n_conditions", []):
            item_condition = item["condition"]
            if not isinstance(item_condition, (str | list)):
                err_msg = "ERROR: condition should be either a list or a string"
                raise TypeError(err_msg)

            if isinstance(
                item_condition, list
            ):  # Auto populate UI puts input into an array
                if len(item_condition) != 1:
                    err_msg = "ERROR: please select 1 condition per reads object"
                    raise ValueError(err_msg)
                item["condition"] = item_condition[0]

            output_object["sample_ids"].extend(item["sample_id"])

            output_object["condition"].extend(
                [item["condition"] for _ in item["sample_id"]]
            )

        sample_ids = output_object["sample_ids"]
        output_object["num_samples"] = len(sample_ids)

        # check that the sampleset contains at least two samples
        if len(sample_ids) < 2:
            err_msg = "This method takes two (2) or more RNASeq Samples. \
                If you have only one read sample, run either 'Align Reads using Tophat' or 'Align Reads using Bowtie2' directly for getting alignment"

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
        all_reads_info_struct = self.ws_client.get_object_info3(
            {
                "objects": [{"ref": reads_ref} for reads_ref in sample_ids],
                "infostruct": 1,
            }
        )
        for item in all_reads_info_struct["infostructs"]:
            # Check that the item type contains one of the allowed types
            if not any(allowed_type in item["type"] for allowed_type in lib_type):
                err_msg = f"Please add only {output_object['Library_type']} typed objects in the Reads fields; you added an object of type {item['type']}."
                raise ValueError(err_msg)
            # add the item's UPA to the sample_refs list
            sample_refs.append(item["path"][0])

        ## Add in the Provenance, with additional info about the
        # input data object refs
        provenance = ctx.get("provenance", [{}])
        provenance[0]["input_ws_objects"] = sample_refs

        # Saving RNASeqSampleSet to Workspace
        print(f"Saving {output_object['sampleset_id']} object to workspace")

        return self.set_interface.save_set(
            self.set_type(),
            ctx["provenance"],
            {
                "workspace": params.get("ws_id"),
                "data": output_object,
                "output_object_name": output_object["sampleset_id"],
            },
        )
