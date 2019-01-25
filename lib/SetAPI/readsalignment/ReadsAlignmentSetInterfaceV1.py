"""
An interface for handling sets of ReadsAlignments.
"""

from pprint import pprint

from SetAPI.generic.SetInterfaceV1 import SetInterfaceV1
from SetAPI import util


class ReadsAlignmentSetInterfaceV1:
    def __init__(self, workspace_client):
        self.workspace_client = workspace_client
        self.set_interface = SetInterfaceV1(workspace_client)

    def save_reads_alignment_set(self, ctx, params):
        if 'data' in params and params['data'] is not None:
            self._validate_reads_alignment_set_data(params['data'])
        else:
            raise ValueError('"data" parameter field required to save a ReadsAlignmentSet')

        save_result = self.set_interface.save_set(
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
            raise ValueError("A ReadsAlignmentSet must contain at "
                             "least one ReadsAlignment reference.")

        refs = list()
        for item in data["items"]:
            refs.append(item["ref"])
            if "label" not in item:
                item["label"] = ""

        ref_list = list([{"ref": r} for r in refs])

        # Get all the genome ids from our ReadsAlignment references (it's the genome_id key in
        # the object metadata). Make a set out of them.
        # If there's 0 or more than 1 item in the set, then either those items are bad, or they're
        # aligned against different genomes.
        info = self.workspace_client.get_object_info3({"objects": ref_list, "includeMetadata": 1})
        num_genomes = len(set([item[10]["genome_id"] for item in info["infos"]]))
        if num_genomes == 0 or num_genomes > 1:
            raise ValueError("All ReadsAlignments in the set must be aligned "
                             "against the same genome reference.")

    def get_reads_alignment_set(self, ctx, params):
        """
        If the set is a KBaseSets.ReadsAlignmentSet, it gets returned as-is.
        If it's a KBaseRNASeq.RNASeqAlignmentSet, a few things get juggled.
        1. We try to figure out the object references for the alignments (which are optional)
        2. From each ref, we try to figure out the condition, and apply those as labels (also
           might be optional)
        """
        set_type, obj_spec = self._check_get_reads_alignment_set_params(params)

        include_item_info = False
        if 'include_item_info' in params:
            if params['include_item_info'] == 1:
                include_item_info = True

        include_set_item_ref_paths = False
        if 'include_set_item_ref_paths' in params:
            if params['include_set_item_ref_paths'] == 1:
                include_set_item_ref_paths = True

        ref_path_to_set = []
        if 'ref_path_to_set' in params and len(params['ref_path_to_set']) > 0:
            ref_path_to_set = params['ref_path_to_set']

        if "KBaseSets" in set_type:
            # If it's a KBaseSets type, then we know the usual interface will work...
            return self.set_interface.get_set(
                params['ref'],
                include_item_info,
                ref_path_to_set,
                include_set_item_ref_paths
            )
        else:
            # ...otherwise, we need to fetch it directly from the workspace and tweak it into the
            # expected return object

            obj_data = self.workspace_client.get_objects2({"objects": [obj_spec]})["data"][0]

            obj = obj_data["data"]
            obj_info = obj_data["info"]
            alignment_ref_list = list()
            if "sample_alignments" in obj:
                alignment_ref_list = obj["sample_alignments"]
            else:
                # this is a list of dicts of random strings -> alignment refs
                # need them all as a set, then emit as a list.
                reads_to_alignments = obj["mapped_alignments_ids"]
                refs = set()
                for mapping in reads_to_alignments:
                    refs.update(list(mapping.values()))
                alignment_ref_list = list(refs)
            alignment_items = [{"ref": i} for i in alignment_ref_list]

            item_infos = self.workspace_client.get_object_info3(
                {"objects": alignment_items, "includeMetadata": 1})["infos"]
            for idx, ref in enumerate(alignment_items):
                alignment_items[idx]["label"] = item_infos[idx][10].get("condition", None)
                if include_item_info:
                    alignment_items[idx]["info"] = item_infos[idx]
            """
            If include_set_item_ref_paths is set, then add a field ref_path in alignment items
            """
            if include_set_item_ref_paths:
                util.populate_item_object_ref_paths(alignment_items, obj_spec)

            return {
                "data": {
                    "items": alignment_items,
                    "description": ""
                },
                "info": obj_info
            }

    def _check_get_reads_alignment_set_params(self, params):
        if 'ref' not in params or params['ref'] is None:
            raise ValueError(
                '"ref" parameter field specifiying the reads alignment set is required')
        elif not util.check_reference(params['ref']):
            raise ValueError('"ref" parameter must be a valid workspace reference')
        if 'include_item_info' in params:
            if params['include_item_info'] not in [0, 1]:
                raise ValueError('"include_item_info" parameter field can only be set to 0 or 1')

        obj_spec = util.build_ws_obj_selector(params.get('ref'), params.get('ref_path_to_set', []))

        info = self.workspace_client.get_object_info3({"objects": [obj_spec]})

        return info["infos"][0][2], obj_spec
