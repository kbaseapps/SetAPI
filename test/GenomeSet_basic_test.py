"""Basic GenomeSet tests."""
from test.common_test import check_get_set, check_save_set_output, is_info_object
from typing import Any

import pytest
from SetAPI.generic.constants import INC_ITEM_INFO, INC_ITEM_REF_PATHS, REF_PATH_TO_SET
from SetAPI.genome.GenomeSetInterfaceV1 import GenomeSetInterfaceV1
from SetAPI.SetAPIImpl import SetAPI

API_CLASS = GenomeSetInterfaceV1
SET_TYPE = "genome"


def save_genome_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    set_name: str,
    set_data: dict[str, Any],
    kwargs: None | dict[str, Any] = None,
) -> dict[str, Any]:
    """Given a set_name and set_data, save a genome set."""
    if not kwargs:
        kwargs = {}
    return set_api_client.save_genome_set_v1(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": set_name,
            "data": set_data,
            **kwargs,
        },
    )[0]


@pytest.fixture(scope="module")
def genome_set(
    genome_refs: list[str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> dict[str, int | str | dict[str, Any]]:
    """A set with name, description, and items populated."""
    set_name = "test_genome_set"
    set_description = "test_genomes"
    set_items = [{"label": "some_label", "ref": ref} for ref in genome_refs]
    set_data = {
        "description": set_description,
        "items": set_items,
    }

    result = save_genome_set(set_api_client, context, ws_id, set_name, set_data)

    return {
        "obj": result,
        "set_name": set_name,
        "set_type": API_CLASS.set_type(),
        "set_description": set_description,
        "n_items": len(genome_refs),
        "second_set_item": set_items[1],
    }


@pytest.fixture(scope="module")
def kbase_search_genome_set(
    genome_refs: list[str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> dict[str, Any]:
    """Set of KBaseSearch genomes."""
    set_name = "test_search_genome_set"
    set_description = "test_search_genomes"
    set_items = {
        ref: {"ref": ref, "metadata": {"some": "thing", "or": "other"}}
        for ref in genome_refs
    }
    set_data = {"description": set_description, "elements": set_items}
    result = save_genome_set(
        set_api_client, context, ws_id, set_name, set_data, {"save_search_set": True}
    )
    print("result")
    print(result)
    return {
        "obj": result,
        "set_name": set_name,
        "set_type": "KBaseSearch.GenomeSet",
        "set_description": set_description,
        "n_items": len(genome_refs),
        "second_set_item": set_items[genome_refs[1]],
        "is_fake_set": True,
    }


@pytest.fixture(scope="module")
def empty_genome_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> dict[str, int | str | dict[str, Any]]:
    """A set with no description and an empty items list."""
    set_name = "empty_genome_set"
    # omit the set description and make the set items an empty list
    set_data = {
        "items": [],
    }

    result = save_genome_set(set_api_client, context, ws_id, set_name, set_data)

    return {
        "obj": result,
        "set_name": set_name,
        "set_type": API_CLASS.set_type(),
        # the class fills in the missing description field
        "set_description": "",
        "n_items": 0,
    }


def test_save_genome_set(genome_set) -> None:
    check_save_set_output(**genome_set)


def test_save_empty_genome_set(empty_genome_set) -> None:
    check_save_set_output(**empty_genome_set)


def test_save_kbasesearch_genome(
    kbase_search_genome_set: dict[str, Any],
    genome_refs: list[str],
    set_api_client: SetAPI,
    context: dict[str, Any],
) -> None:
    res = kbase_search_genome_set["obj"]
    check_save_set_output(
        kbase_search_genome_set["obj"],
        set_name=kbase_search_genome_set["set_name"],
        set_type=kbase_search_genome_set["set_type"],
    )

    # test get of that object
    d1 = set_api_client.get_genome_set_v1(context, {"ref": res["set_ref"]})[0]
    assert "data" in d1
    assert "info" in d1
    is_info_object(
        d1["info"],
        kbase_search_genome_set["set_name"],
        kbase_search_genome_set["set_type"],
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


@pytest.mark.parametrize(
    "ref_args",
    [
        pytest.param("__SET_REF__", id="set_ref"),
        pytest.param("__WS_NAME__SET_NAME__", id="ws_name_set_name"),
    ],
)
@pytest.mark.parametrize(
    "get_method_args",
    [
        pytest.param({}, id="empty"),
        pytest.param({INC_ITEM_INFO: 1}, id="inc_item_info"),
        pytest.param(
            {INC_ITEM_REF_PATHS: 1},
            id="inc_ref_path",
        ),
        pytest.param(
            {
                INC_ITEM_INFO: 1,
                INC_ITEM_REF_PATHS: 1,
            },
            id="inc_item_info_ref_path",
        ),
        pytest.param(
            {INC_ITEM_INFO: 1, INC_ITEM_REF_PATHS: 1, REF_PATH_TO_SET: ["YES"]},
            id="inc_item_info_ref_path_w_ref_path",
        ),
        pytest.param(
            {
                INC_ITEM_INFO: 0,
                INC_ITEM_REF_PATHS: 0,
            },
            id="no_incs",
        ),
    ],
)
def test_get_genome_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_name: str,
    ref_args: str,
    get_method_args: dict[str, str | int],
    genome_set: dict[str, Any],
    empty_genome_set: dict[str, Any],
) -> None:
    for saved_set in [genome_set, empty_genome_set]:
        check_get_set(
            set_to_get=saved_set,
            set_type=SET_TYPE,
            set_api_client=set_api_client,
            context=context,
            ws_name=ws_name,
            ref_args=ref_args,
            get_method_args=get_method_args,
        )
