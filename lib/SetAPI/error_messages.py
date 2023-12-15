"""Functions to construct common error messages."""

import re

SET_TYPE_REGEX = r"^.*?\.(.*?)Set(-.+)?$"


def get_set_items_type_from_kbase_set_type(kbase_set_type: str) -> str:
    """Work out the set item type from the KBase set type.

    For example, if the set type is "KBaseSets.AssemblySet", this function
    will return "Assembly".

    :param kbase_set_type: KBase set type (without version info)
    :type kbase_set_type: str
    :raises ValueError: if the set type doesn't conform to the expected regex
    :return: object type within the set
    :rtype: str
    """
    match = re.search(SET_TYPE_REGEX, kbase_set_type)
    if match:
        return match.group(1)
    err_msg = f"Unexpected KBase set type: {kbase_set_type}"
    raise ValueError(err_msg)


def include_params_valid(param_name: str) -> str:
    """Valid parameter message for the "include_..." params.

    :param param_name: parameter name
    :type param_name: str
    :return: full error message
    :rtype: str
    """
    return f'The "{param_name}" parameter can only be set to 0 or 1.'


def list_required(list_type: str = "items") -> str:
    """List required message for either "items" or "elements".

    :param list_type: list key, defaults to "items"
    :type list_type: str, optional
    :return: full error message
    :rtype: str
    """
    return (
        f'An "{list_type}" list must be defined in the "data" parameter to save a set.'
    )


def no_dupes() -> str:
    """I don't want no dupes, a dupe is a datum that can't get no love from me.

    :return: full error message
    :rtype: str
    """
    return "Please ensure there are no duplicate refs in the set."


def no_items(kbase_set_type: str) -> str:
    """For sets that require at least one object.

    :param kbase_set_type: type of the set, e.g. KBaseSets.ReadsSet
    :type kbase_set_type: str
    :return: full error message
    :rtype: str
    """
    set_items_type = get_set_items_type_from_kbase_set_type(kbase_set_type)
    return f"{set_items_type}Sets must contain at least one {set_items_type} object reference."


def param_required(param_name: str) -> str:
    """Param required error message.

    :param param_name: param name
    :type param_name: str
    :return: full error message
    :rtype: str
    """
    return f'The "{param_name}" parameter is required.'


def ref_must_be_valid() -> str:
    """Valid ref required.

    :return: full error message
    :rtype: str
    """
    return 'The "ref" parameter must be a valid workspace reference.'


def ref_path_must_be_valid() -> str:
    """Valid ref path required.

    :return: full error message
    :rtype: str
    """
    return 'The "ref_path" parameter must contain valid workspace references.'


def same_ref(kbase_set_type: str) -> str:
    """Same genome reference for all set members.

    :param kbase_set_type: KBase set type (without version info)
    :type kbase_set_type: str
    :return: full error message
    :rtype: str
    """
    set_items_type = get_set_items_type_from_kbase_set_type(kbase_set_type)
    return (
        f"All {set_items_type} objects in the set must use the same genome reference."
    )
