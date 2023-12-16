"""General tests to be performed on most or all classes."""
from test.conftest import SET_FIXTURE_MAP
from test.util import (
    INFO_LENGTH,
    info_to_name,
    info_to_ref,
    info_to_type,
    info_to_usermeta,
)
from typing import Any

import pytest
from SetAPI.generic.constants import (
    ASSEMBLY,
    DIFFERENTIAL_EXPRESSION_MATRIX,
    EXPRESSION,
    FEATURE_SET,
    GENOME,
    INC_ITEM_INFO,
    INC_ITEM_REF_PATHS,
    READS,
    READS_ALIGNMENT,
    REF_PATH_TO_SET,
    SET_ITEM_NAME_TO_SET_TYPE,
)
from SetAPI.SetAPIImpl import SetAPI

SET_ITEM_NAMES = [
    ASSEMBLY,
    DIFFERENTIAL_EXPRESSION_MATRIX,
    EXPRESSION,
    FEATURE_SET,
    GENOME,
    READS,
    READS_ALIGNMENT,
]


FAKE_WS_ID = 123456789
KBASE_UPA = "1/2/3"

# standard sets to test:
sets_to_test = {
    "assembly_set": "assembly_refs",
    "empty_assembly_set": None,
    "differential_expression_matrix_with_genome_set": "differential_expression_matrix_with_genome_refs",
    "differential_expression_matrix_no_genome_set": "differential_expression_matrix_no_genome_refs",
    "expression_set": "expression_refs",
    "feature_set_set": "feature_set_refs",
    "empty_feature_set_set": None,
    "genome_set": "genome_refs",
    "empty_genome_set": None,
    "reads_set": "reads_refs",
    "empty_reads_set": None,
    "reads_alignment_set": "reads_alignment_refs",
}


def is_info_object(
    obj: list[str | int | dict[str, str]],
    obj_name: str | None = None,
    kbase_obj_type: str | None = None,
    obj_description: str | None = None,
    n_items: int | None = None,
) -> None:
    """Checks whether a mysterious data structure is a KBase info list.

    If the set was not created by the SetAPI (is_fake_set = True), some of the
    fields will be filled out differently, so the checks reflect this.

    info list structure:
    obj_id objid - the numerical id of the object.
    obj_name name - the name of the object.
    type_string type - the type of the object.
    timestamp save_date - the save date of the object.
    obj_ver ver - the version of the object.
    username saved_by - the user that saved or copied the object.
    ws_id wsid - the workspace containing the object.
    ws_name workspace - the workspace containing the object.
    string chsum - the md5 checksum of the object.
    int size - the size of the object in bytes.
    usermeta meta - arbitrary user-supplied metadata about
        the object.

    :param obj: the mysterious data structure
    :type info: list[str|int|dict[str, str]]
    :param obj_name: expected object name, defaults to None
    :type obj_name: str | None, optional
    :param kbase_obj_type: expected KBase object type, defaults to None
    :type kbase_obj_type: str | None, optional
    :param obj_description: expected description in the user metadata, defaults to None
    :type obj_description: str | None, optional
    :param n_items: how many items are expected in the user metadata, defaults to None
    :type n_items: int | None, optional
    """
    assert isinstance(obj, list)
    assert len(obj) == INFO_LENGTH
    for ix in [0, 4, 6, 9]:
        assert isinstance(obj[ix], int)
    for ix in [1, 2, 3, 5, 7, 8]:
        assert isinstance(obj[ix], str)
    # usermeta field
    if obj[10]:
        assert isinstance(obj[10], dict)

    # some of these can be "falsy" values (0, empty string), so check explicitly against None
    if obj_name is not None:
        assert info_to_name(obj) == obj_name
    if kbase_obj_type:
        assert kbase_obj_type in info_to_type(obj)
    if obj_description is not None:
        assert "description" in info_to_usermeta(obj)
        assert info_to_usermeta(obj)["description"] == obj_description
    if n_items is not None:
        assert "item_count" in info_to_usermeta(obj)
        assert info_to_usermeta(obj)["item_count"] == str(n_items)


def check_save_set_output(
    obj: dict[str, Any],
    set_name: str,
    kbase_set_type: str,
    set_description: str | None = None,
    n_items: int | None = None,
    **kwargs,
) -> None:
    """Check the output of a save_set command.

    The output should be of the form
    { "set_ref": <upa>, "set_info": <kbase info list> }

    :param obj: API output to check
    :type obj: dict[str, Any]
    :param set_name: the set name
    :type set_name: str
    :param kbase_set_type: expected KBase object type, defaults to None
    :type kbase_set_type: str | None, optional
    :param set_description: user-entered description of the set, defaults to None
    :type set_description: str | None, optional
    :param n_items: number of items in the set, defaults to None
    :type n_items: int | None, optional
    :param kwargs: leftover params - not used
    :type kwargs: dict[str, Any], optional
    """
    assert obj is not None
    assert "set_ref" in obj
    assert "set_info" in obj
    assert obj["set_ref"] == info_to_ref(obj["set_info"])
    is_info_object(obj["set_info"], set_name, kbase_set_type, set_description, n_items)


def check_second_item(
    obj: dict[str, Any],
    expected_item_data: dict[str, str],
) -> None:
    """Check the second item in a set.

    :param obj: API output to check, with items stored in obj["data"]["items"]
    :type obj: dict[str, Any]
    :param expected_item_data: expected item data (should have ref and label)
    :type expected_item_data: dict[str, str]
    """
    second_item = obj["data"]["items"][1]
    assert second_item.get("ref") == expected_item_data["ref"]
    assert second_item.get("label") == expected_item_data["label"]


def check_get_set_output(
    obj: dict[str, Any],
    ref: str,
    set_name: str,
    kbase_set_type: str,
    set_description: str | None = None,
    n_items: int | None = None,
    second_set_item: dict[str, str] | None = None,
    include_item_info: int = 0,
    include_set_item_ref_paths: int = 0,
    ref_path_to_set: list[str] | None = None,
    **kwargs,
) -> None:
    """Checks the output of a get_set command.

    :param obj: API output to check
    :type obj: dict[str, Any]
    :param ref: reference used to access the set
    :type ref: str
    :param set_name: set name
    :type set_name: str
    :param kbase_set_type: expected KBase object type, defaults to None
    :type kbase_set_type: str | None, optional
    :param set_description: set description, defaults to None
    :type set_description: str | None, optional
    :param n_items: how many items are expected in the set, defaults to None
    :type n_items: int | None, optional
    :param second_set_item: dict containing label and ref for the second item in the set, defaults to None
    :type second_set_item: dict[str, str] | None, optional
    :param include_item_info: whether set items are expected to have item info, defaults to 0 (false)
    :type include_item_info: int, optional
    :param include_set_item_ref_paths: whether set items are expected to have a ref path, defaults to 0 (false)
    :type include_set_item_ref_paths: int, optional
    :param ref_path_to_set: list of references for the set, defaults to None
    :type ref_path_to_set: list[str], optional
    :param kwargs: leftover params - not used
    :type kwargs: dict[str, Any], optional
    """
    assert obj is not None
    assert "data" in obj
    assert "info" in obj
    is_info_object(obj["info"], set_name, kbase_set_type, set_description, n_items)

    assert obj["data"]["description"] == set_description
    assert len(obj["data"]["items"]) == n_items

    for item in obj["data"]["items"]:
        if include_item_info == 1:
            assert "info" in item
            is_info_object(item["info"])
        else:
            assert "info" not in item

        if include_set_item_ref_paths == 1:
            ref_path = item.get("ref_path", "NOT_FOUND")
            if ref_path_to_set:
                assert ref_path == ";".join(ref_path_to_set) + ";" + item["ref"]
            else:
                assert item.get("ref_path", "NOT_FOUND") == f"{ref};{item['ref']}"
        else:
            assert "ref_path" not in item

    if n_items and second_set_item:
        check_second_item(obj, second_set_item)


def param_wrangle(
    ref_args: str,
    get_method_args: dict[str, str | int],
    set_ref: str,
    set_name: str,
    ws_name: str,
) -> dict[str, Any]:
    # set up the parameters for a "get_***_set" query
    params = {}
    if ref_args == "__SET_REF__":
        params["ref"] = set_ref
    else:
        params["ref"] = f"{ws_name}/{set_name}"

    for param in [INC_ITEM_INFO, INC_ITEM_REF_PATHS, REF_PATH_TO_SET]:
        if param in get_method_args:
            params[param] = get_method_args[param]

    if params.get(REF_PATH_TO_SET, []) != []:
        # add in a value for the REF_PATH_TO_SET
        params[REF_PATH_TO_SET] = [set_ref]

    return params


def check_get_set(
    set_to_get: dict[str, Any],
    set_item_name: str,
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_name: str,
    ref_args: str,
    get_method_args: dict[str, str | int],
) -> None:
    """Test retrieval of the default data type for each set.

    This test does not test any of those RNASeq fake sets.

    :param set_to_get: the set to retrieve
    :type set_to_get: dict[str, Any]
    :param set_item_name: name of the objects in the set, e.g. "genome"
    :type set_item_name: str
    :param set_api_client: the SetAPI client
    :type set_api_client: SetAPI
    :param context: KBase context
    :type context: dict[str, str | list]
    :param ws_name: workspace name
    :type ws_name: str
    :param ref_args: how the set should be referred to
    :type ref_args: str
    :param get_method_args: other args
    :type get_method_args: dict[str, str | int]
    """
    set_ref = set_to_get["obj"]["set_ref"]

    params = param_wrangle(
        ref_args, get_method_args, set_ref, set_to_get["set_name"], ws_name
    )
    if ref_args == "__SET_REF__":
        params["ref"] = set_ref
    else:
        params["ref"] = f"{ws_name}/{set_to_get['set_name']}"

    for param in [INC_ITEM_INFO, INC_ITEM_REF_PATHS, REF_PATH_TO_SET]:
        if param in get_method_args:
            params[param] = get_method_args[param]

    if params.get(REF_PATH_TO_SET, []) != []:
        # add in a value for the REF_PATH_TO_SET
        params[REF_PATH_TO_SET] = [set_ref]

    get_method = getattr(set_api_client, f"get_{set_item_name}_set_v1")
    fetched_set = get_method(context, params)[0]

    args_to_check_get_set_output = {
        **{arg: set_to_get[arg] for arg in set_to_get if arg != "obj"},
        **params,
        "kbase_set_type": SET_ITEM_NAME_TO_SET_TYPE[set_item_name],
        "obj": fetched_set,
    }
    check_get_set_output(**args_to_check_get_set_output)


# mapping of fixture names to the set_item_name of the contents
all_set_types = {
    "assembly_set": ASSEMBLY,
    "empty_assembly_set": ASSEMBLY,
    "differential_expression_matrix_no_genome_set": DIFFERENTIAL_EXPRESSION_MATRIX,
    "differential_expression_matrix_with_genome_set": DIFFERENTIAL_EXPRESSION_MATRIX,
    "expression_set": EXPRESSION,
    "feature_set_set": FEATURE_SET,
    "empty_feature_set_set": FEATURE_SET,
    "genome_set": GENOME,
    "empty_genome_set": GENOME,
    "reads_set": READS,
    "empty_reads_set": READS,
    "reads_alignment_set": READS_ALIGNMENT,
}


@pytest.mark.parametrize(
    ("ws_id", "data_fixture"),
    [("default_ws_id", data_fixture) for data_fixture in SET_FIXTURE_MAP],
    indirect=["ws_id", "data_fixture"],
)
def test_save_set(ws_id: int, data_fixture: dict[str, Any]) -> None:
    """Test that saving a set produces the expected output.

    This saves sets in the default workspace (default_ws_id) and uses the
    fixtures corresponding to the keys in the "all_set_types" mapping.

    :param ws_id: workspace ID of the workspace that the sets are saved in
    :type ws_id: int
    :param data_fixture: name of the data fixture to use in the test
    :type data_fixture: dict[str, Any]
    """
    check_save_set_output(**data_fixture)
