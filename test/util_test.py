from typing import Any
import pytest
from SetAPI.util import (
    check_reference,
    build_ws_obj_selector,
    populate_item_object_ref_paths,
    convert_workspace_param,
)

bad_upas = [
    None,
    "",
    "//",
    "://",
    " / / ",
    "1",
    "1/",
    "1//3",
    "1/2/",
    "1/2/3/",
    "1/2/3;",
    "1/2/3;4/5/",
    "1/2/foo",
    "1/bar",
    "1/bar/3",
    "1:this/that",
    "1;2;3",
    "://",
    ":this/that",
    "foo",
    "foo/2",
    "foo/2/3",
    "foo/bar/3",
    "foo/bar;baz/frobozz",
    "foo:1/2",
    "http://",
    "myws/myobj/myver",
    "myws/myobj/myver;otherws/otherobj/otherver",
    "no,commas,allowed",
    "some whitespace",
    "this:/that",
    "this:1/that",
    "ws:obj:ver",
    "x/y/z",
]


@pytest.mark.parametrize("upa", [pytest.param(upa) for upa in bad_upas])
def test_check_reference_fail(upa):
    assert check_reference(upa) is False


good_upas = [
    "1/2",
    "1/2/3",
    "bar/baz",
    "barb13/baz17710n",
    "foo:bar/baz",
    "user-name:_ws_.name/obj-name",
    "some-text:some_more.text/other-text_here.",
]


@pytest.mark.parametrize("upa", [pytest.param(upa) for upa in good_upas])
def test_check_reference_good_refs(upa) -> None:
    assert check_reference(upa) is True


GOOD_UPA = "123/45/6"
WS_ID_INT = 12345
WS_ID_STR = "12345"
WS_NAME = "some_string"


@pytest.mark.parametrize(
    "params_key",
    [
        pytest.param("workspace", id="workspace"),
        pytest.param("workspace_id", id="workspace_id"),
        pytest.param("ws_id", id="ws_id"),
    ],
)
@pytest.mark.parametrize(
    "args",
    [
        pytest.param(
            {
                "value": WS_ID_INT,
                "expected": {"id": WS_ID_INT},
            },
            id="ws_id_int",
        ),
        pytest.param(
            {
                "value": WS_ID_STR,
                "expected": {"id": WS_ID_INT},
            },
            id="ws_id_str",
        ),
        pytest.param(
            {
                "value": WS_NAME,
                "expected": {"workspace": WS_NAME},
            },
            id="ws_name",
        ),
    ],
)
def test_convert_workspace_param(
    params_key: str, args: dict[str, dict[str, int | str]]
) -> None:
    assert convert_workspace_param({params_key: args["value"]}) == args["expected"]


@pytest.mark.parametrize(
    "params_key",
    [
        pytest.param("workspace_name", id="workspace_name"),
        pytest.param("ws_name", id="ws_name"),
    ],
)
@pytest.mark.parametrize(
    "args",
    [
        pytest.param(
            {
                "value": WS_ID_INT,
                "expected": {"workspace": WS_ID_STR},
            },
            id="ws_id_int",
        ),
        pytest.param(
            {
                "value": WS_ID_STR,
                "expected": {"workspace": WS_ID_STR},
            },
            id="ws_id_str",
        ),
        pytest.param(
            {
                "value": WS_NAME,
                "expected": {"workspace": WS_NAME},
            },
            id="ws_name",
        ),
    ],
)
def test_convert_workspace_param_ws_name(
    params_key: str, args: dict[str, str | int | dict[str, int | str]]
) -> None:
    assert convert_workspace_param({params_key: args["value"]}) == args["expected"]


@pytest.mark.parametrize(
    "args",
    [
        pytest.param({}, id="empty_dict"),
        pytest.param(None, id="dict is None"),
        pytest.param({"this": "that"}, id="missing_param"),
    ],
)
def test_convert_workspace_param_fail(args: None | dict[str, str]) -> None:
    with pytest.raises(
        ValueError, match="No appropriate key found for workspace name or ID"
    ):
        convert_workspace_param(args)


@pytest.mark.parametrize(
    "args",
    [
        pytest.param(
            {
                "ref": GOOD_UPA,
                "ref_path_to_set": None,
                "expected": GOOD_UPA,
            },
            id="ref_path_to_set_none",
        ),
        pytest.param(
            {
                "ref": GOOD_UPA,
                "ref_path_to_set": [],
                "expected": GOOD_UPA,
            },
            id="ref_path_to_set_empty",
        ),
        pytest.param(
            {
                "ref": None,
                "ref_path_to_set": None,
                "expected": None,
            },
            id="ref_and_ref_path_none",
        ),
        pytest.param(
            {
                "ref": None,
                "ref_path_to_set": ["a/b/c"],
                "expected": "a/b/c",
            },
            id="ref_path_single_item",
        ),
        pytest.param(
            {
                "ref": "whatever",
                "ref_path_to_set": ["a/b/c", "d/e/f", "g/h/i"],
                "expected": "a/b/c;d/e/f;g/h/i",
            },
            id="ref_path_three_items",
        ),
    ],
)
def test_build_ws_obj_selector(args: dict[str, Any]) -> None:
    """Test that the correct workspace object selector is built.

    :param args: dict containing the arguments and expected result.
    :type args: dict[str, Any]
    """
    assert build_ws_obj_selector(args["ref"], args["ref_path_to_set"]) == {
        "ref": args["expected"]
    }


@pytest.mark.parametrize(
    "args",
    [
        pytest.param(
            {
                "set_items": [],
                "obj_selector": {"ref": "whatever"},
                "expected": [],
            },
            id="empty_list",
        ),
        pytest.param(
            {
                "set_items": [{"ref": "some_ref"}, {"ref": "some_other_ref"}],
                "obj_selector": {"ref": "whatever"},
                "expected": [
                    {"ref": "some_ref", "ref_path": "whatever;some_ref"},
                    {"ref": "some_other_ref", "ref_path": "whatever;some_other_ref"},
                ],
            },
            id="populated_list",
        ),
    ],
)
def test_populate_item_object_ref_paths(args: dict[str, Any]) -> None:
    """Test that the correct ref path is added to items in a list.

    :param args: dict containing arguments and expected result.
    :type args: dict[str, Any]
    """
    assert (
        populate_item_object_ref_paths(args["set_items"], args["obj_selector"])
        == args["expected"]
    )
