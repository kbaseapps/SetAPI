"""
This module contains some utility functions for the SetAPI.
"""
import re

def check_reference(ref):
    """
    Returns True if ref looks like an actual object reference: xx/yy/zz or xx/yy
    Returns False otherwise.
    """
    obj_ref_regex = re.compile("^((\d+)|[A-Za-z].*)\/((\d+)|[A-Za-z].*)(\/\d+)?$")
    # obj_ref_regex = re.compile("^(?P<wsid>\d+)\/(?P<objid>\d+)(\/(?P<ver>\d+))?$")
    if ref is None or not obj_ref_regex.match(ref):
        return False
    return True

def build_ws_obj_selector(ref, ref_path_to_set):
    if ref_path_to_set and len(ref_path_to_set) > 0:
        return {
            'ref': ';'.join(ref_path_to_set)
        }
    return {'ref': ref}

def populate_item_object_ref_paths(set_items, obj_selector):
    """
    Called when include_set_item_ref_paths is set.
    Add a field ref_path to each item in set
    """
    for set_item in set_items:
        set_item["ref_path"] = obj_selector['ref'] + ';' + set_item['ref']
    return set_items
