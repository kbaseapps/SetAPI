"""
Some utility functions to help with testing. These mainly add fake objects to use in making sets.
"""
from installed_clients.DataFileUtilClient import DataFileUtil


def info_to_ref(info):
    """
    Just a one liner that converts the usual Workspace ObjectInfo list into an object reference
    string.
    (Honestly, I just got sick of rewriting this everywhere and forgetting the indices - Bill).
    """
    return "{}/{}/{}".format(info[6], info[0], info[4])


def make_fake_alignment(callback_url, dummy_file, name, reads_ref, genome_ref, ws_name, ws_client):
    """
    Makes a Fake KBaseRNASeq.RNASeqAlignment object and returns a ref to it.
    callback_url: needed for DataFileUtil,
    dummy_file: path to some dummy "alignment" file (make it small - needs to be uploaded to shock)
    name: the name of the object
    reads_ref: a reference to a valid (probably fake) reads library
    genome_ref: a reference to a valid (also probably fake) genome
    workspace_name: the name of the workspace to save this object
    workspace_client: a Workspace client tuned to the server of your choice
    """
    dfu = DataFileUtil(callback_url)
    dummy_shock_info = dfu.file_to_shock({
        "file_path": dummy_file,
        "make_handle": 1
    })
    fake_alignment = {
        "file": dummy_shock_info['handle'],
        "library_type": "fake",
        "read_sample_id": reads_ref,
        "condition": "fake",
        "genome_id": genome_ref
    }
    return make_fake_object(fake_alignment, "KBaseRNASeq.RNASeqAlignment", name, ws_name, ws_client)


def make_fake_sampleset(name, reads_refs, conditions, ws_name, ws_client):
    """
    Make a fake KBaseRNASeq.RNASeqSampleSet object.
    reads_refs and conditions are expected to be the same length, and that length can be 0.
    """
    if len(reads_refs) != len(conditions):
        raise ValueError("reads_refs and conditions must be the same length!")
    fake_sampleset = {
        "sampleset_id": "fake",
        "sampleset_desc": "fake",
        "domain": "fake",
        "num_samples": len(reads_refs),
        "condition": conditions,
        "sample_ids": reads_refs,
        "Library_type": "fake",
    }
    return make_fake_object(fake_sampleset, "KBaseRNASeq.RNASeqSampleSet", name, ws_name, ws_client)


def make_fake_old_alignment_set(name, reads_refs, genome_ref, sampleset_ref, alignments_refs,
                                ws_name, ws_client, include_sample_alignments=False):
    """
    Make a fake set object for KBaseRNASeq.RNASeqAlignmentSet objects
    Needs a whole bunch of stuff:
        list of reads_refs
        list of alignments_refs
        genome_ref
        sampleset_ref (can be dummied up with make_fake_sampleset)
    Setting include_sample_alignments to True will include the optional "sample_alignments"
    attribute of the object.
    """
    mapped_alignments_ids = list()
    for idx, ref in enumerate(reads_refs):
        mapped_alignments_ids.append({ref: alignments_refs[idx]})

    fake_rnaseq_alignment_set = {
        "sampleset_id": sampleset_ref,
        "genome_id": genome_ref,
        "read_sample_ids": reads_refs,
        "mapped_rnaseq_alignments": mapped_alignments_ids,
        "mapped_alignments_ids": mapped_alignments_ids
    }
    if include_sample_alignments:
        fake_rnaseq_alignment_set["sample_alignments"] = alignments_refs
    return make_fake_object(fake_rnaseq_alignment_set, "KBaseRNASeq.RNASeqAlignmentSet",
                            name, ws_name, ws_client)


def make_fake_old_expression_set(name, genome_ref, sampleset_ref,
                                 alignments_refs, alignmentset_ref,
                                 expressions_refs, ws_name, ws_client,
                                 include_sample_expressions=False):
    """
    Make a fake set object for KBaseRNASeq.RNASeqAlignmentSet objects
    Needs a whole bunch of stuff:
        list of reads_refs
        list of alignments_refs
        genome_ref
        sampleset_ref (can be dummied up with make_fake_sampleset)
    Setting include_sample_alignments to True will include the optional "sample_alignments"
    attribute of the object.
    """
    mapped_expression_ids = list()
    for idx, ref in enumerate(alignments_refs):
        mapped_expression_ids.append({ref: expressions_refs[idx]})

    fake_rnaseq_expression_set = {
        "sampleset_id": sampleset_ref,
        "genome_id": genome_ref,
        "mapped_expression_ids": mapped_expression_ids,
        "mapped_expression_objects": [],
        "alignmentSet_id": alignmentset_ref
    }
    if include_sample_expressions:
        fake_rnaseq_expression_set["sample_expression_ids"] = expressions_refs
    return make_fake_object(fake_rnaseq_expression_set, "KBaseRNASeq.RNASeqExpressionSet",
                            name, ws_name, ws_client)


def make_fake_annotation(callback_url, dummy_file, name, ws_name, ws_client):
    dfu = DataFileUtil(callback_url)
    dummy_shock_info = dfu.file_to_shock({
        "file_path": dummy_file,
        "make_handle": 1
    })
    annotation = {
        "handle": dummy_shock_info['handle'],
        "size": 0,
        "genome_id": "not_a_real_genome",
        "genome_scientific_name": "Genomus falsus"
    }
    return make_fake_object(annotation, "KBaseRNASeq.GFFAnnotation", name, ws_name, ws_client)


def make_fake_expression(callback_url, dummy_file, name, genome_ref, annotation_ref, alignment_ref, ws_name, ws_client):
    """
    Makes a Fake KBaseRNASeq.RNASeqExpression object and returns a ref to it.
    genome_ref: reference to a genome object
    annotation_ref: reference to a KBaseRNASeq.GFFAnnotation
    alignment_ref: reference to a KBaseRNASeq.RNASeqAlignment
    """
    dfu = DataFileUtil(callback_url)
    dummy_shock_info = dfu.file_to_shock({
        "file_path": dummy_file,
        "make_handle": 1
    })
    exp = {
        "id": "fake",
        "type": "fake",
        "numerical_interpretation": "fake",
        "expression_levels": {"feature_1": 0, "feature_2": 1, "feature_3": 2},
        "genome_id": genome_ref,
        "annotation_id": annotation_ref,
        "mapped_rnaseq_alignment": {"id1": alignment_ref},
        "condition": "",
        "tool_used": "none",
        "tool_version": "0.0.0",
        "file": dummy_shock_info['handle']
    }
    return make_fake_object(exp, "KBaseRNASeq.RNASeqExpression", name, ws_name, ws_client)


def make_fake_feature_set(name, genome_ref, ws_name, ws_client):
    """
    Makes a fake KBaseCollections.FeatureSet object and returns a ref to it.
    KBaseCollections.FeatureSet type:
    typedef structure {
        string description;
        list<feature_id> element_ordering;
        mapping<feature_id, list<genome_ref>> elements;
    } FeatureSet;
    """
    feature_set = {
        "description": "some features",
        "element_ordering": ["feature1", "feature2", "feature3"],
        "elements": {
            "feature1": [genome_ref],
            "feature2": [genome_ref],
            "feature3": [genome_ref]
        }
    }
    return make_fake_object(feature_set, "KBaseCollections.FeatureSet", name, ws_name, ws_client)


def make_fake_diff_exp_matrix(name, ws_name, ws_client, genome_ref=None):
    """
    Makes a fake KBaseFeatureValues.DifferentialExpressionMatrix object and returns a ref ot it.
    * = optional (so, left out of this fake stuff)

    typedef structure {
        list<string> row_ids;
        list<string> col_ids;
        list<list<float>> values;
    } FloatMatrix2D;

    typedef structure {
        * string description;
        string type;
        string scale;
        * string row_normalization;
        * string col_normalization;

        * ws_genome_id genome_ref;
        * mapping<string, string> feature_mapping;

        * ws_conditionset_id conditionset_ref;
        * mapping<string, string> condition_mapping;

        FloatMatrix2D data;
        * AnalysisReport report;
    } DifferentialExpressionMatrix;

    Makes the dumbest matrix ever - just a single row, a single column, a single 0 value.
    """
    matrix_data = {
        "row_ids": ["row1"],
        "col_ids": ["col1"],
        "values": [[0.0]]
    }
    diff_exp_matrix = {
        "type": "level",
        "scale": "raw",
        "data": matrix_data
    }
    if genome_ref is not None:
        diff_exp_matrix['genome_ref'] = genome_ref
    return make_fake_object(diff_exp_matrix, "KBaseFeatureValues.DifferentialExpressionMatrix",
                            name, ws_name, ws_client)


def make_fake_object(obj, obj_type, name, workspace_name, workspace_client):
    """
    Saves a dummy object (obj) of given type obj_type and name to the given workspace_name using the
    provided workspace client.

    Returns a reference to that object.
    """
    return info_to_ref(
        workspace_client.save_objects({
            "workspace": workspace_name,
            "objects": [{
                "type": obj_type,
                "meta": {},
                "data": obj,
                "name": name
            }]
        })[0]
    )
