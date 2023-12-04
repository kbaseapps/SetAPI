import pytest
from typing import Callable, Any
from test.util import (
    INFO_LENGTH,
    info_to_name,
    info_to_ref,
    info_to_type,
    info_to_usermeta,
)


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
    assert second_item.get("ref", None) == expected_item_data["ref"]
    assert second_item.get("label", None) == expected_item_data["label"]


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


FAKE_WS_ID = 123456789


def check_save_set_mismatched_genomes(
    context: dict[str, str | list],
    save_method: Callable,
    set_items: list[dict[str, str]],
    set_items_type: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=f"All {set_items_type} objects in the set must use the same genome reference.",
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


def check_save_set_no_data(
    context: dict[str, str | list],
    save_method: Callable,
    set_items_type: str,
) -> None:
    """Check that a set cannot be created without a "data" parameter.

    :param context: KBase context
    :type context: dict[str, str  |  list]
    :param save_method: which method we're using
    :type save_method: Callable
    :param set_items_type: type of item in the set
    :type set_items_type: str
    """
    with pytest.raises(
        ValueError,
        match=f'The "data" parameter is required to save {set_items_type}Sets',
    ):
        save_method(
            context,
            {
                "workspace_id": FAKE_WS_ID,
                "output_object_name": "foo",
                "data": None,
            },
        )


def check_save_set_no_items_list(
    context: dict[str, str | list],
    save_method: Callable,
    set_items_type: str,
) -> None:
    """Check that a set cannot be created without an "items" key under the "data" parameter.

    :param context: context
    :type context: dict[str, str  |  list]
    :param save_method: SetAPI save method being tested
    :type save_method: Callable
    :param set_items_type: string with the item type
    :type set_items_type: str
    """
    with pytest.raises(
        ValueError,
        match=f'An "items" list must be defined in the "data" parameter to save {set_items_type}Sets',
    ):
        save_method(
            context,
            {
                "workspace_id": FAKE_WS_ID,
                "output_object_name": "foo",
                "data": {},
            },
        )


def check_save_set_no_objects(
    context: dict[str, str | list],
    save_method: Callable,
    set_items_type: str,
) -> None:
    """For classes that don't allow empty sets to be created.

    :param context: context
    :type context: dict[str, str  |  list]
    :param save_method: SetAPI save method being tested
    :type save_method: Callable
    :param set_items_type: string with the item type
    :type set_items_type: str
    """
    with pytest.raises(
        ValueError,
        match=f"{set_items_type}Sets must contain at least one {set_items_type} object reference.",
    ):
        save_method(
            context,
            {
                "workspace_id": FAKE_WS_ID,
                "output_object_name": "foo",
                "data": {"items": []},
            },
        )


def check_get_set_bad_ref(
    context: dict[str, str | list],
    get_method: Callable,
) -> None:
    with pytest.raises(
        ValueError, match='The "ref" parameter must be a valid workspace reference'
    ):
        get_method(context, {"ref": "not_a_ref"})


def check_get_set_bad_path(
    context: dict[str, str | list],
    get_method: Callable,
) -> None:
    with pytest.raises(
        ValueError,
        match='The "ref_path" parameter must contain valid workspace references',
    ):
        get_method(context, {"ref": "1/2/3", "ref_path_to_set": ["foo", "bar"]})


def check_get_set_no_ref(
    context: dict[str, str | list],
    get_method: Callable,
    set_items_type: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=f'The "ref" parameter specifying the {set_items_type}Set is required',
    ):
        get_method(context, {"ref": None})
