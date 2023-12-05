"""General tests to be performed on most or all classes."""
from collections.abc import Callable
from test.util import (
    INFO_LENGTH,
    info_to_name,
    info_to_ref,
    info_to_type,
    info_to_usermeta,
)
from typing import Any

import pytest
from SetAPI.assembly.AssemblySetInterfaceV1 import AssemblySetInterfaceV1
from SetAPI.differentialexpressionmatrix.DifferentialExpressionMatrixSetInterfaceV1 import (
    DifferentialExpressionMatrixSetInterfaceV1,
)
from SetAPI.error_messages import (
    include_params_valid,
    list_required,
    no_dupes,
    no_items,
    param_required,
    ref_must_be_valid,
    ref_path_must_be_valid,
    same_ref,
)
from SetAPI.expression.ExpressionSetInterfaceV1 import ExpressionSetInterfaceV1
from SetAPI.featureset.FeatureSetSetInterfaceV1 import FeatureSetSetInterfaceV1
from SetAPI.generic.constants import INC_ITEM_INFO, INC_ITEM_REF_PATHS
from SetAPI.genome.GenomeSetInterfaceV1 import GenomeSetInterfaceV1
from SetAPI.reads.ReadsSetInterfaceV1 import ReadsSetInterfaceV1
from SetAPI.readsalignment.ReadsAlignmentSetInterfaceV1 import (
    ReadsAlignmentSetInterfaceV1,
)
from SetAPI.SetAPIImpl import SetAPI

SET_TYPE_TO_CLASS = {
    "assembly": AssemblySetInterfaceV1,
    "differential_expression_matrix": DifferentialExpressionMatrixSetInterfaceV1,
    "expression": ExpressionSetInterfaceV1,
    "feature_set": FeatureSetSetInterfaceV1,
    "genome": GenomeSetInterfaceV1,
    "reads": ReadsSetInterfaceV1,
    "reads_alignment": ReadsAlignmentSetInterfaceV1,
}
SET_TYPES = list(SET_TYPE_TO_CLASS.keys())
FAKE_WS_ID = 123456789
KBASE_UPA = "1/2/3"


def is_info_object(
    obj: list[str | int | dict[str, str]],
    obj_name: str | None = None,
    obj_type: str | None = None,
    obj_description: str | None = None,
    n_items: int | None = None,
    is_fake_set: bool = False,
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
    :param obj_type: expected object type, defaults to None
    :type obj_type: str | None, optional
    :param obj_description: expected description in the user metadata, defaults to None
    :type obj_description: str | None, optional
    :param n_items: how many items are expected in the user metadata, defaults to None
    :type n_items: int | None, optional
    :param is_fake_set: whether or not the current set was created by the SetAPI, defaults to False
    :type is_fake_set: bool, optional
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
    if obj_type:
        assert obj_type in info_to_type(obj)
    if obj_description is not None and not is_fake_set:
        assert "description" in info_to_usermeta(obj)
        assert info_to_usermeta(obj)["description"] == obj_description
    if n_items is not None and not is_fake_set:
        assert "item_count" in info_to_usermeta(obj)
        assert info_to_usermeta(obj)["item_count"] == str(n_items)


def check_save_set_output(
    obj: dict[str, Any],
    set_name: str,
    set_type: str | None = None,
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
    :param set_type: the type of the set, defaults to None
    :type set_type: str | None, optional
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
    is_info_object(obj["set_info"], set_name, set_type, set_description, n_items)


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
    set_type: str | None = None,
    set_description: str | None = None,
    n_items: int | None = None,
    second_set_item: dict[str, str] | None = None,
    include_item_info: int = 0,
    include_set_item_ref_paths: int = 0,
    ref_path_to_set: list[str] | None = None,
    is_fake_set: bool = False,
) -> None:
    """Checks the output of a get_set command.

    :param obj: API output to check
    :type obj: dict[str, Any]
    :param ref: reference used to access the set
    :type ref: str
    :param set_name: set name
    :type set_name: str
    :param set_type: set type, defaults to None
    :type set_type: str | None, optional
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
    :param is_fake_set: whether or not the current set was created by the SetAPI, defaults to False
    :type is_fake_set: bool, optional
    :param kwargs: leftover params - not used
    :type kwargs: dict[str, Any], optional
    """
    assert obj is not None
    assert "data" in obj
    assert "info" in obj
    is_info_object(
        obj["info"], set_name, set_type, set_description, n_items, is_fake_set
    )

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


def check_save_set_mismatched_genomes(
    context: dict[str, str | list],
    set_api_client: SetAPI,
    set_type: str,
    set_items: list[dict[str, str]],
    set_items_type: str,
) -> None:
    save_method = getattr(set_api_client, f"save_{set_type}_set_v1")
    with pytest.raises(
        ValueError,
        match=same_ref(set_items_type),
    ):
        save_method(
            context,
            {
                "workspace_id": FAKE_WS_ID,
                "output_object_name": "foo",
                "data": {
                    "description": "mismatched genome alert!",
                    "items": set_items,
                },
            },
        )


@pytest.mark.parametrize("set_type", SET_TYPES)
def test_save_set_no_data(
    context: dict[str, str | list],
    set_api_client: SetAPI,
    set_type: str,
) -> None:
    """Check that a set cannot be created without a "data" parameter.

    :param context: KBase context
    :type context: dict[str, str  |  list]
    :param save_method: which method we're using
    :type save_method: Callable
    :param set_items_type: type of item in the set
    :type set_items_type: str
    """
    save_method = getattr(set_api_client, f"save_{set_type}_set_v1")
    with pytest.raises(
        ValueError,
        match=param_required("data"),
    ):
        save_method(
            context,
            {
                "workspace_id": FAKE_WS_ID,
                "output_object_name": "foo",
                "data": None,
            },
        )


@pytest.mark.parametrize("set_type", SET_TYPES)
def test_save_set_no_items_list(
    context: dict[str, str | list],
    set_api_client: SetAPI,
    set_type: str,
) -> None:
    """Check that a set cannot be created without an "items" key under the "data" parameter.

    :param context: context
    :type context: dict[str, str  |  list]
    :param save_method: SetAPI save method being tested
    :type save_method: Callable
    :param set_items_type: string with the item type
    :type set_items_type: str
    """
    save_method = getattr(set_api_client, f"save_{set_type}_set_v1")
    with pytest.raises(
        ValueError,
        match=list_required("items"),
    ):
        save_method(
            context,
            {
                "workspace_id": FAKE_WS_ID,
                "output_object_name": "foo",
                "data": {},
            },
        )


@pytest.mark.parametrize("set_type", SET_TYPES)
def test_save_set_no_objects(
    context: dict[str, str | list],
    set_api_client: SetAPI,
    set_type: str,
) -> None:
    """For classes that don't allow empty sets to be created.

    :param context: context
    :type context: dict[str, str  |  list]
    :param save_method: SetAPI save method being tested
    :type save_method: Callable
    :param set_items_type: string with the item type
    :type set_items_type: str
    """
    klass = SET_TYPE_TO_CLASS[set_type]
    if klass.allows_empty_set():
        pytest.skip(f"{klass} allows the creation of empty sets")

    save_method = getattr(set_api_client, f"save_{set_type}_set_v1")
    set_items_type = SET_TYPE_TO_CLASS[set_type].set_items_type()

    with pytest.raises(
        ValueError,
        match=no_items(set_items_type),
    ):
        save_method(
            context,
            {
                "workspace_id": FAKE_WS_ID,
                "output_object_name": "foo",
                "data": {"items": []},
            },
        )


@pytest.mark.parametrize("set_type", SET_TYPES)
def test_save_set_with_dupes(
    context: dict[str, str | list],
    set_api_client: SetAPI,
    set_type: str,
):
    save_method = getattr(set_api_client, f"save_{set_type}_set_v1")
    # create a set with two identical refs
    with pytest.raises(ValueError, match=no_dupes()):
        save_method(
            context,
            {
                "workspace_id": FAKE_WS_ID,
                "output_object_name": "foo",
                "data": {
                    "items": [{"ref": KBASE_UPA}, {"ref": "4/5/6"}, {"ref": KBASE_UPA}]
                },
            },
        )


@pytest.mark.parametrize("set_type", SET_TYPES)
def test_get_set_bad_ref(
    context: dict[str, str | list], set_api_client: SetAPI, set_type: str
) -> None:
    """Check that the client throws an error with a dodgy ref."""
    get_method = getattr(set_api_client, f"get_{set_type}_set_v1")
    with pytest.raises(ValueError, match=ref_must_be_valid()):
        get_method(context, {"ref": "not_a_ref"})


@pytest.mark.parametrize("set_type", SET_TYPES)
def test_get_set_bad_path(
    context: dict[str, str | list], set_api_client: SetAPI, set_type: str
) -> None:
    """Check that the client throws an error with a dodgy ref_path."""
    get_method = getattr(set_api_client, f"get_{set_type}_set_v1")
    with pytest.raises(
        ValueError,
        match=ref_path_must_be_valid(),
    ):
        get_method(context, {"ref": KBASE_UPA, "ref_path_to_set": ["foo", "bar"]})


@pytest.mark.parametrize("set_type", SET_TYPES)
@pytest.mark.parametrize("none_type", ["", None])
def test_get_set_no_ref(
    context: dict[str, str | list],
    set_api_client: SetAPI,
    set_type: str,
    none_type: None | str,
) -> None:
    """Check that the client throws an error with no ref supplied."""
    get_method = getattr(set_api_client, f"get_{set_type}_set_v1")
    with pytest.raises(
        ValueError,
        match=param_required("ref"),
    ):
        get_method(context, {"ref": none_type})


@pytest.mark.parametrize("set_type", SET_TYPES)
@pytest.mark.parametrize("inc_arg", [INC_ITEM_INFO, INC_ITEM_REF_PATHS])
def test_get_set_invalid_args(
    context: dict[str, str | list],
    set_api_client: SetAPI,
    set_type: str,
    inc_arg: str,
) -> None:
    """Check that the client throws an error with incorrect get args."""
    get_method = getattr(set_api_client, f"get_{set_type}_set_v1")
    with pytest.raises(ValueError, match=include_params_valid(inc_arg)):
        get_method(context, {"ref": KBASE_UPA, inc_arg: 666})
