"""General set retrieval error tests to be performed on most or all set types."""
from test.common_test import KBASE_UPA, SET_ITEM_NAMES

import pytest
from SetAPI.error_messages import (
    include_params_valid,
    param_required,
    ref_must_be_valid,
    ref_path_must_be_valid,
)
from SetAPI.generic.constants import (
    INC_ITEM_INFO,
    INC_ITEM_REF_PATHS,
)
from SetAPI.SetAPIImpl import SetAPI


@pytest.mark.parametrize("set_item_name", SET_ITEM_NAMES)
def test_get_set_bad_ref(
    context: dict[str, str | list], set_api_client: SetAPI, set_item_name: str
) -> None:
    """Check that the client throws an error with a dodgy ref."""
    get_method = getattr(set_api_client, f"get_{set_item_name}_set_v1")
    with pytest.raises(ValueError, match=ref_must_be_valid()):
        get_method(context, {"ref": "not_a_ref"})


@pytest.mark.parametrize("set_item_name", SET_ITEM_NAMES)
def test_get_set_bad_path(
    context: dict[str, str | list], set_api_client: SetAPI, set_item_name: str
) -> None:
    """Check that the client throws an error with a dodgy ref_path."""
    get_method = getattr(set_api_client, f"get_{set_item_name}_set_v1")
    with pytest.raises(
        ValueError,
        match=ref_path_must_be_valid(),
    ):
        get_method(context, {"ref": KBASE_UPA, "ref_path_to_set": ["foo", "bar"]})


@pytest.mark.parametrize("set_item_name", SET_ITEM_NAMES)
@pytest.mark.parametrize("none_type", ["", None])
def test_get_set_no_ref(
    context: dict[str, str | list],
    set_api_client: SetAPI,
    set_item_name: str,
    none_type: None | str,
) -> None:
    """Check that the client throws an error with no ref supplied."""
    get_method = getattr(set_api_client, f"get_{set_item_name}_set_v1")
    with pytest.raises(
        ValueError,
        match=param_required("ref"),
    ):
        get_method(context, {"ref": none_type})


@pytest.mark.parametrize("set_item_name", SET_ITEM_NAMES)
@pytest.mark.parametrize("inc_arg", [INC_ITEM_INFO, INC_ITEM_REF_PATHS])
def test_get_set_invalid_args(
    context: dict[str, str | list],
    set_api_client: SetAPI,
    set_item_name: str,
    inc_arg: str,
) -> None:
    """Check that the client throws an error with incorrect get args."""
    get_method = getattr(set_api_client, f"get_{set_item_name}_set_v1")
    with pytest.raises(ValueError, match=include_params_valid(inc_arg)):
        get_method(context, {"ref": KBASE_UPA, inc_arg: 666})
