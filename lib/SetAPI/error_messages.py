"""Functions to construct common error messages."""


def data_required(set_items_type: str) -> str:
    return f'The "data" parameter is required to save {set_items_type}Sets'


def include_params_valid(param_name) -> str:
    return f'The "{param_name}" parameter can only be set to 0 or 1'


def items_list_required(set_items_type: str) -> str:
    return f'An "items" list must be defined in the "data" parameter to save {set_items_type}Sets'


def no_items(set_items_type: str) -> str:
    return f"{set_items_type}Sets must contain at least one {set_items_type} object reference."


def ref_required(set_items_type: str) -> str:
    return f'The "ref" parameter specifying the {set_items_type}Set is required'


def ref_must_be_valid() -> str:
    return 'The "ref" parameter must be a valid workspace reference'


def ref_path_must_be_valid() -> str:
    return 'The "ref_path" parameter must contain valid workspace references'


def same_ref(set_items_type: str) -> str:
    return (
        f"All {set_items_type} objects in the set must use the same genome reference."
    )
