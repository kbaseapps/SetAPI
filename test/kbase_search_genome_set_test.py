"""Tests for KBaseSearch.GenomeSets."""
from test.common_test import (
    check_save_set_output,
    is_info_object,
)
from typing import Any

import pytest
from SetAPI.generic.constants import (
    GENOME_SEARCH_SET,
)
from SetAPI.SetAPIImpl import SetAPI


@pytest.mark.parametrize("ws_id", ["default_ws_id"], indirect=True)
def test_save_kbasesearch_genome(
    kbase_search_genome_set: dict[str, Any],
    genome_refs: list[str],
    set_api_client: SetAPI,
    context: dict[str, Any],
    ws_id: int,
) -> None:
    """Test the setting and getting of KBaseSearch.GenomeSets."""
    res = kbase_search_genome_set["obj"]
    check_save_set_output(
        kbase_search_genome_set["obj"],
        set_name=kbase_search_genome_set["set_name"],
        kbase_set_type=GENOME_SEARCH_SET,
    )

    # test get of that object
    d1 = set_api_client.get_genome_set_v1(context, {"ref": res["set_ref"]})[0]

    assert "data" in d1
    assert "info" in d1
    is_info_object(
        d1["info"],
        kbase_search_genome_set["set_name"],
        kbase_search_genome_set["kbase_set_type"],
    )
    assert d1["data"]["description"] == kbase_search_genome_set["set_description"]
    assert len(d1["data"]["elements"]) == kbase_search_genome_set["n_items"]

    elements = d1["data"]["elements"]
    for ref in genome_refs:
        assert ref in elements

    genome_2 = elements.get(genome_refs[1])
    assert "ref" in genome_2
    assert genome_2.get("ref") == genome_refs[1]
    assert genome_2["metadata"] == {"some": "thing", "or": "other"}
