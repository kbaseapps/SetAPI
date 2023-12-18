"""Generic SetInterface tests.

See SetAPIImpl_test.py, get_set_error_test.py, and save_set_error_test.py for the majority of the SetAPI tests.
This file is for tests that can only be run against the SetInterfaceV1 class.
"""
from typing import Any

import pytest
from SetAPI.generic.SetInterfaceV1 import SetInterfaceV1


@pytest.mark.parametrize("set_item_name", [None, "", "piggy"])
def test_save_set_invalid_type(
    clients: dict[str, Any],
    set_item_name: str,
) -> None:
    """Testing a situation where an invalid set_item_name has magicked itself into existence.

    This cannot be tested through the API as there is no way to
    generate this kind of combination.

    :param clients: dict of relevant clients
    :type clients: dict[str, Any]
    """
    set_interface = SetInterfaceV1(clients["ws"])
    with pytest.raises(
        ValueError,
        match="invalid set item name",
    ):
        set_interface.save_set(
            set_item_name,
            {},
            {"workspace": "blah", "data": "ugh", "output_object_name": "meh"},
        )
