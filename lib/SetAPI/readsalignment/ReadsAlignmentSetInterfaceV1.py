"""
An interface for handling sets of ReadsAlignments.
"""
from SetAPI.generic.SetInterfaceV1 import SetInterfaceV1
from biokbase.workspace.client import Workspace


class ReadsAlignmentSetInterfaceV1:
    def __init__(self, workspace_client):
        self.workspace_client = workspace_client
        self.set_interface = SetInterfaceV1(workspace_client)

    def save_reads_alignment_set(self, ctx, params):
        if 'data' in params:
            self._validate_reads_set_data(params['data'])
        else:
            raise ValueError('"data" parameter field required to save a ReadsAlignmentSet')

        save_result = self.setInterface.save_set(
                'KBaseSets.ReadsAlignmentSet',
                ctx['provenance'],
                params
            )
        info = save_result[0]
        return {
            'set_ref': str(info[6]) + '/' + str(info[0]) + '/' + str(info[4]),
            'set_info': info
        }

    def _validate_reads_alignment_set_data(self, data):
        # Normalize the object, make empty strings where necessary
        if "description" not in data:
            data["description"] = ""

        if "items" not in data or len(data.get("items", [])) == 0:
            raise ValueError("A ReadsAlignmentSet must contain at least one ReadsAlignment reference.")

        refs = list()
        for item in data["items"]:
            refs.append(item["ref"])
            if "label" not in item:
                item["label"] = ""

        ref_list = list(map(lambda r: {"ref": r}, refs))

        # Get all the genome ids from our ReadsAlignment references (it's the genome_id key in
        # the object metadata). Make a set out of them.
        # If there's 0 or more than 1 item in the set, then either those items are bad, or they're
        # aligned against different genomes.
        info = self.workspace_client.get_object_info3({"objects": ref_list, "includeMetadata": 1})
        num_genomes = len(set([item[10]["genome_id"] for item in info["infos"]]))
        if num_genomes == 0 or num_genomes > 1:
            raise ValueError("All ReadsAlignments in the set should be aligned against the same genome reference.")


    def get_reads_alignment_set(self, ctx, params):
        pass
