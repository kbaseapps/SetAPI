"""Some utility functions to help with testing. These mainly add fake objects to use in making sets."""
import json
from collections.abc import Callable
from typing import Any

from installed_clients.WorkspaceClient import Workspace
from SetAPI.generic.constants import (
    GENOME,
    GENOME_SEARCH,
    SAVE_SEARCH_SET,
    SET_ITEM_NAME_TO_SET_TYPE,
)
from SetAPI.SetAPIImpl import SetAPI
from SetAPI.util import info_to_ref

INFO_LENGTH = 11


def log_this(config: dict[str, str], file_name: str, output_obj: dict | list) -> None:
    """Utility function for printing JSON data to a file.

    :param config: configuration object
    :type config: dict[str, str]
    :param file_name: file to log to
    :type file_name: string
    :param output_obj: object to log. Must be a JSON-dumpable object.
    :type output_obj: dict|list
    """
    output_file = f"{config['scratch']}/{file_name}"
    with open(output_file, "w") as f:
        f.write(json.dumps(output_obj, indent=2, sort_keys=True))


def info_to_name(info: list[int | str | dict[str, str]]) -> str:
    """Gets the obj name from a KBase info list.

    :param info: info list
    :type info: list[int | str | dict[str, str]]
    :return: object name
    :rtype: str
    """
    return info[1]


def info_to_type(info: list[int | str | dict[str, str]]) -> str:
    """Gets the object type from a KBase info list.

    :param info: info list
    :type info: list[int | str | dict[str, str]]
    :return: object type
    :rtype: str
    """
    return info[2]


def info_to_usermeta(info: list[int | str | dict[str, str]]) -> dict[str, str]:
    """Gets the user-entered metadata from a KBase info list.

    :param info: info list
    :type info: list[int | str | dict[str, str]]
    :return: the metadata (if it exists)
    :rtype: dict[str, Any]
    """
    return info[10]


def _save_set(
    set_item_name: str,
    set_name: str,
    set_description: str,
    set_data: dict[str, Any],
    save_method: Callable,
    context: dict[str, Any],
    ws_id: int,
    n_items: int,
    second_set_item: dict[str, Any] | None,
    kwargs: dict[str, str | bool | int] | None = None,
) -> dict[str, Any]:
    """Save a set to the workspace.

    :param set_item_name: name of the objects in the set, e.g. "genome"
    :type set_item_name: str
    :param set_name: set name
    :type set_name: str
    :param set_description: description for the set; may be an empty string
    :type set_description: str
    :param set_data: the items in the set plus the description
    :type set_data: dict[str, Any]
    :param save_method: API function to be called
    :type save_method: Callable
    :param context: KBase context
    :type context: dict[str, Any]
    :param ws_id: workspace ID
    :type ws_id: int
    :param n_items: how many items in the set
    :type n_items: int
    :param second_set_item: second item in the set, if available
    :type second_set_item: dict[str, Any] | None
    :param kwargs: any extra fun and games to be added to the WS save params, defaults to None
    :type kwargs: dict[str, str  |  bool  |  int] | None, optional
    :return: dictionary with the various pieces of info required to test the output of the save command
    :rtype: dict[str, Any]
    """
    if not kwargs:
        kwargs = {}

    result = save_method(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": set_name,
            "data": set_data,
            **kwargs,
        },
    )[0]

    return {
        "obj": result,
        "set_name": set_name,
        "set_item_name": set_item_name,
        "kbase_set_type": SET_ITEM_NAME_TO_SET_TYPE[set_item_name],
        "set_description": set_description,
        "n_items": n_items,
        "second_set_item": second_set_item,
    }


def save_set(
    set_item_name: str,
    set_api_client: SetAPI,
    context: dict[str, str | list],
    refs: list[str],
    ws_id: int,
    name_qualifier: str | None = None,
) -> dict[str, Any]:
    """A set with name, description, and items populated."""
    set_name = f"test_{set_item_name}_set"
    if name_qualifier:
        set_name = f"test_{set_item_name}_{name_qualifier}_set"
    set_description = "a set comprised of {set_item_name} objects"
    set_items = [{"label": "some_label", "ref": ref} for ref in refs]
    set_data = {
        "items": set_items,
        "description": set_description,
    }
    save_method = getattr(set_api_client, f"save_{set_item_name}_set_v1")

    return _save_set(
        set_item_name=set_item_name,
        set_name=set_name,
        set_description=set_description,
        set_data=set_data,
        save_method=save_method,
        context=context,
        ws_id=ws_id,
        n_items=len(set_items),
        second_set_item=set_items[1],
    )


def save_empty_set(
    set_item_name: str,
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> dict[str, Any]:
    """A set with no description and an empty items list."""
    set_name = f"test_empty_{set_item_name}_set"
    # omit the set description and make the set items an empty list
    set_data = {
        "items": [],
    }
    save_method = getattr(set_api_client, f"save_{set_item_name}_set_v1")

    return _save_set(
        set_item_name=set_item_name,
        set_name=set_name,
        set_description="",
        set_data=set_data,
        save_method=save_method,
        context=context,
        ws_id=ws_id,
        n_items=0,
        second_set_item=None,
    )


def save_kbase_search_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    refs: list[str],
    ws_id: int,
) -> dict[str, Any]:
    """A KBaseSearch genome set."""
    set_item_name = GENOME_SEARCH
    set_name = f"test_{set_item_name}_set"
    set_description = f"a set comprised of {set_item_name} objects"
    set_items = {
        ref: {"ref": ref, "metadata": {"some": "thing", "or": "other"}} for ref in refs
    }
    set_data = {
        "elements": set_items,
        "description": set_description,
    }
    save_method = getattr(set_api_client, f"save_{GENOME}_set_v1")

    return _save_set(
        set_item_name=set_item_name,
        set_name=set_name,
        set_description=set_description,
        set_data=set_data,
        save_method=save_method,
        context=context,
        ws_id=ws_id,
        n_items=len(refs),
        second_set_item=set_items[refs[1]],
        kwargs={SAVE_SEARCH_SET: True},
    )


def make_fake_alignment(
    dummy_file_shock_handle: str,
    name: str,
    reads_ref: str,
    genome_ref: str,
    ws_id: int,
    ws_client: Workspace,
) -> str:
    """Makes a Fake KBaseRNASeq.RNASeqAlignment object and returns a ref to it.

    dummy_file_shock_handle: shock handle for a dummy file
    name: the name of the object
    reads_ref: a reference to a valid (probably fake) reads library
    genome_ref: a reference to a valid (also probably fake) genome
    ws_id: the ID of the workspace to save this object
    ws_client: a Workspace client tuned to the server of your choice.
    """
    alignment = {
        "file": dummy_file_shock_handle,
        "library_type": "fake",
        "read_sample_id": reads_ref,
        "condition": "fake",
        "genome_id": genome_ref,
    }
    return make_fake_object(
        alignment, "KBaseRNASeq.RNASeqAlignment", name, ws_id, ws_client
    )


def make_fake_annotation(
    dummy_file_shock_handle: str,
    name: str,
    ws_id: int,
    ws_client: Workspace,
) -> str:
    annotation = {
        "handle": dummy_file_shock_handle,
        "size": 0,
        "genome_id": "not_a_real_genome",
        "genome_scientific_name": "Genomus falsus",
    }
    return make_fake_object(
        annotation, "KBaseRNASeq.GFFAnnotation", name, ws_id, ws_client
    )


def make_fake_diff_exp_matrix(
    name: str, ws_id: int, ws_client: Workspace, genome_ref: None | str = None
) -> str:
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
    matrix_data = {"row_ids": ["row1"], "col_ids": ["col1"], "values": [[0.0]]}
    diff_exp_matrix = {"type": "level", "scale": "raw", "data": matrix_data}
    if genome_ref is not None:
        diff_exp_matrix["genome_ref"] = genome_ref
    return make_fake_object(
        diff_exp_matrix,
        "KBaseFeatureValues.DifferentialExpressionMatrix",
        name,
        ws_id,
        ws_client,
    )


def make_fake_expression(
    dummy_file_shock_handle: str,
    name: str,
    genome_ref: str,
    annotation_ref: str,
    alignment_ref: str,
    ws_id: int,
    ws_client: Workspace,
) -> str:
    """
    Makes a Fake KBaseRNASeq.RNASeqExpression object and returns a ref to it.

    genome_ref: reference to a genome object
    annotation_ref: reference to a KBaseRNASeq.GFFAnnotation
    alignment_ref: reference to a KBaseRNASeq.RNASeqAlignment
    """
    exp = {
        "id": "fake",
        "type": "fake",
        "numerical_interpretation": "fake",
        "expression_levels": {"feature_1": 0, "feature_2": 1, "feature_3": 2},
        "genome_id": genome_ref,
        "annotation_id": annotation_ref,
        "mapped_rnaseq_alignment": {"iobj": alignment_ref},
        "condition": "",
        "tool_used": "none",
        "tool_version": "0.0.0",
        "file": dummy_file_shock_handle,
    }
    return make_fake_object(exp, "KBaseRNASeq.RNASeqExpression", name, ws_id, ws_client)


def make_fake_feature_set(
    name: str, genome_ref: str, ws_id: int, ws_client: Workspace
) -> str:
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
            "feature3": [genome_ref],
        },
    }
    return make_fake_object(
        feature_set, "KBaseCollections.FeatureSet", name, ws_id, ws_client
    )


def make_fake_rnaseq_alignment_set(
    name: str,
    reads_refs: list[str],
    genome_ref: str,
    sampleset_ref: str,
    alignments_refs: list[str],
    ws_id: int,
    ws_client: Workspace,
    include_sample_alignments: bool = False,
) -> str:
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
    mapped_alignments_ids = [
        {ref: alignments_refs[idx]} for idx, ref in enumerate(reads_refs)
    ]

    rnaseq_alignment_set = {
        "sampleset_id": sampleset_ref,
        "genome_id": genome_ref,
        "read_sample_ids": reads_refs,
        "mapped_rnaseq_alignments": mapped_alignments_ids,
        "mapped_alignments_ids": mapped_alignments_ids,
    }
    if include_sample_alignments:
        rnaseq_alignment_set["sample_alignments"] = alignments_refs
    return make_fake_object(
        rnaseq_alignment_set,
        "KBaseRNASeq.RNASeqAlignmentSet",
        name,
        ws_id,
        ws_client,
    )


def make_fake_rnaseq_expression_set(
    name: str,
    genome_ref: str,
    sampleset_ref: str,
    alignments_refs: list[str],
    alignmentset_ref: str,
    expressions_refs: list[str],
    ws_id: int,
    ws_client: Workspace,
    include_sample_expressions: bool = False,
) -> str:
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
    mapped_expression_ids = [
        {ref: expressions_refs[idx]} for idx, ref in enumerate(alignments_refs)
    ]

    rnaseq_expression_set = {
        "sampleset_id": sampleset_ref,
        "genome_id": genome_ref,
        "mapped_expression_ids": mapped_expression_ids,
        "mapped_expression_objects": [],
        "alignmentSet_id": alignmentset_ref,
    }
    if include_sample_expressions:
        rnaseq_expression_set["sample_expression_ids"] = expressions_refs
    return make_fake_object(
        rnaseq_expression_set,
        "KBaseRNASeq.RNASeqExpressionSet",
        name,
        ws_id,
        ws_client,
    )


def make_fake_sampleset(
    name: str,
    reads_refs: list[str],
    conditions: list[str],
    ws_id: int,
    ws_client: Workspace,
) -> str:
    """
    Make a fake KBaseRNASeq.RNASeqSampleSet object.
    reads_refs and conditions are expected to be the same length, and that length can be 0.
    """
    if len(reads_refs) != len(conditions):
        raise ValueError("reads_refs and conditions must be the same length!")
    sampleset = {
        "sampleset_id": "fake",
        "sampleset_desc": "fake",
        "domain": "fake",
        "num_samples": len(reads_refs),
        "condition": conditions,
        "sample_ids": reads_refs,
        "Library_type": "fake",
    }
    return make_fake_object(
        sampleset, "KBaseRNASeq.RNASeqSampleSet", name, ws_id, ws_client
    )


def make_fake_object(
    obj: dict[str, Any],
    obj_type: str,
    name: str,
    ws_id: int,
    workspace_client: Workspace,
) -> str:
    """
    Saves a dummy object (obj) of given type obj_type and name to the given workspace ID using the
    provided workspace client.

    Returns a reference to that object.
    """
    return info_to_ref(
        workspace_client.save_objects(
            {
                "id": ws_id,
                "objects": [{"type": obj_type, "meta": {}, "data": obj, "name": name}],
            }
        )[0]
    )
