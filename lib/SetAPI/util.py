"""
This module contains some utility functions for the SetAPI.
"""
import re


def check_reference(ref):
    """
    Returns True if ref looks like an actual object reference: xx/yy/zz or xx/yy
    Returns False otherwise.
    """
    obj_ref_regex = re.compile("^(?P<wsid>\d+)\/(?P<objid>\d+)(\/(?P<ver>\d+))?$")
    if ref is None or not obj_ref_regex.match(ref):
        return False
    return True
