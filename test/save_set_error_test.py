"""General set saving error tests performed on most or all set types."""
from test.common_test import SET_ITEM_NAMES

import pytest
from SetAPI.error_messages import (
    list_required,
    no_dupes,
    no_items,
    param_required,
    same_ref,
)
from SetAPI.generic.constants import (
    DIFFERENTIAL_EXPRESSION_MATRIX,
    EXPRESSION,
    READS_ALIGNMENT,
    SET_ITEM_NAME_TO_SET_TYPE,
)
from SetAPI.generic.SetInterfaceV1 import ALLOWS_EMPTY_SETS
from SetAPI.SetAPIImpl import SetAPI

# keys are the set item name, values are the names of the fixtures with
# mismatched genome refs.
MISMATCHED_GENOME_REFS = {
    DIFFERENTIAL_EXPRESSION_MATRIX: "differential_expression_matrix_mismatched_genome_refs",
    READS_ALIGNMENT: "alignment_mismatched_genome_refs",
    EXPRESSION: "expression_mismatched_genome_refs",
}

FAKE_WS_ID = 123456789
KBASE_UPA = "123/45/6"


@pytest.mark.parametrize("ws_id", ["default_ws_id"], indirect=["ws_id"])
@pytest.mark.parametrize(
    ("set_item_name", "data_fixture"),
    list(MISMATCHED_GENOME_REFS.items()),
    indirect=["data_fixture"],
)
def test_save_set_mismatched_genomes(
    context: dict[str, str | list],
    set_api_client: SetAPI,
    set_item_name: str,
    data_fixture: list[str],
) -> None:
    """Check that objects with refs to different genomes cannot be setified.

    :param context: KBase context
    :type context: dict[str, str  |  list]
    :param set_api_client: SetAPI client
    :type set_api_client: SetAPI
    :param set_item_name: name of the set objects, to insert into "save_{set_item_name}_set"
    :type set_item_name: str
    :param data_fixture: the objects to be put in the set
    :type data_fixture: list[str]
    """
    # get the fixture corresponding to this set_item_name
    set_items = [{"label": "item", "ref": ref} for ref in data_fixture]
    save_method = getattr(set_api_client, f"save_{set_item_name}_set_v1")

    with pytest.raises(
        ValueError,
        match=same_ref(SET_ITEM_NAME_TO_SET_TYPE[set_item_name]),
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


@pytest.mark.parametrize("set_item_name", SET_ITEM_NAMES)
@pytest.mark.parametrize("param", ["output_object_name", "data"])
@pytest.mark.parametrize("value", ["missing", "", None])
def test_save_set_no_required_param(
    context: dict[str, str | list],
    set_api_client: SetAPI,
    set_item_name: str,
    param: str,
    value: str | None,
) -> None:
    """Check that a set cannot be created without one of the required fields.

    :param context: KBase context
    :type context: dict[str, str  |  list]
    :param set_api_client: SetAPI client
    :type set_api_client: SetAPI
    :param set_item_name: name of the objects in the set, e.g. "genome"
    :type set_item_name: str
    :param param: parameter to edit
    :type param: str
    :param value: value for the parameter
    :type value: str | None
    """
    save_method = getattr(set_api_client, f"save_{set_item_name}_set_v1")
    params = {
        "workspace_id": FAKE_WS_ID,
        "output_object_name": "foo",
        "data": {"items": [{"ref": val} for val in ["this", "that"]]},
    }
    if value is None or value == "":
        params[param] = value
    else:
        del params[param]

    with pytest.raises(
        ValueError,
        match=param_required(param),
    ):
        save_method(
            context,
            params,
        )


@pytest.mark.parametrize("set_item_name", SET_ITEM_NAMES)
@pytest.mark.parametrize("param", ["workspace", "workspace_id", "workspace_name"])
@pytest.mark.parametrize("value", ["missing", "", None])
def test_save_set_no_required_workspace_param(
    context: dict[str, str | list],
    set_api_client: SetAPI,
    set_item_name: str,
    param: str,
    value: str | None,
) -> None:
    """Check that a set cannot be created without a workspace identifier.

    :param context: KBase context
    :type context: dict[str, str  |  list]
    :param set_api_client: SetAPI client
    :type set_api_client: SetAPI
    :param set_item_name: name of the objects in the set, e.g. "genome"
    :type set_item_name: str
    :param param: parameter to edit
    :type param: str
    :param value: value for the parameter
    :type value: str | None
    """
    save_method = getattr(set_api_client, f"save_{set_item_name}_set_v1")
    params = {
        "output_object_name": "foo",
        "data": {"items": [{"ref": val} for val in ["this", "that"]]},
    }

    if value is None or value == "":
        params[param] = value

    with pytest.raises(
        ValueError,
        match=param_required('workspace" or "workspace_id" or "workspace_name'),
    ):
        save_method(
            context,
            params,
        )


@pytest.mark.parametrize("set_item_name", SET_ITEM_NAMES)
def test_save_set_no_items_list(
    context: dict[str, str | list],
    set_api_client: SetAPI,
    set_item_name: str,
) -> None:
    """Check that a set cannot be created without an "items" key under the "data" parameter.

    :param context: context
    :type context: dict[str, str  |  list]
    :param set_api_client: SetAPI client
    :type set_api_client: SetAPI
    :param set_item_name: name of the objects in the set, e.g. "genome"
    :type set_item_name: str
    """
    save_method = getattr(set_api_client, f"save_{set_item_name}_set_v1")
    with pytest.raises(
        ValueError,
        match=list_required("items"),
    ):
        save_method(
            context,
            {
                "workspace_id": FAKE_WS_ID,
                "output_object_name": "foo",
                "data": {"some_key": "some_value"},
            },
        )


@pytest.mark.parametrize("set_item_name", SET_ITEM_NAMES)
def test_save_set_no_objects(
    context: dict[str, str | list],
    set_api_client: SetAPI,
    set_item_name: str,
) -> None:
    """For classes that don't allow empty sets to be created.

    :param context: context
    :type context: dict[str, str  |  list]
    :param set_api_client: SetAPI client
    :type set_api_client: SetAPI
    :param set_item_name: name of the objects in the set, e.g. "genome"
    :type set_item_name: str
    """
    if set_item_name in ALLOWS_EMPTY_SETS:
        pytest.skip(f"Can create empty sets containing {set_item_name} objects")

    save_method = getattr(set_api_client, f"save_{set_item_name}_set_v1")
    kbase_set_type = SET_ITEM_NAME_TO_SET_TYPE[set_item_name]

    with pytest.raises(
        ValueError,
        match=no_items(kbase_set_type),
    ):
        save_method(
            context,
            {
                "workspace_id": FAKE_WS_ID,
                "output_object_name": "foo",
                "data": {"items": []},
            },
        )


@pytest.mark.parametrize("set_item_name", SET_ITEM_NAMES)
def test_save_set_with_dupes(
    context: dict[str, str | list],
    set_api_client: SetAPI,
    set_item_name: str,
) -> None:
    """Ensure a set cannot be saved with duplicate objects in it.

    :param context: KBase context
    :type context: dict[str, str  |  list]
    :param set_api_client: SetAPI client
    :type set_api_client: SetAPI
    :param set_item_name: name of the objects in the set, e.g. "genome"
    :type set_item_name: str
    """
    save_method = getattr(set_api_client, f"save_{set_item_name}_set_v1")
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
