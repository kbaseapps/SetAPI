"""Basic GenomeSet tests."""
from test.util import INFO_LENGTH

from SetAPI.SetAPIImpl import SetAPI

N_GENOME_REFS = 2


def test_basic_save_and_get(
    genome_refs: list[str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> None:
    set_name = "set_of_genomes"
    set_description = "my first genome set"

    # create the set object
    set_data = {
        "description": set_description,
        "items": [
            {"ref": genome_refs[0], "label": "genome1"},
            {"ref": genome_refs[1], "label": "genome2"},
        ],
    }

    # test a save
    res = set_api_client.save_genome_set_v1(
        context,
        {
            "data": set_data,
            "output_object_name": set_name,
            "workspace_id": ws_id,
        },
    )[0]
    assert "set_ref" in res
    assert "set_info" in res
    assert len(res["set_info"]) == INFO_LENGTH

    assert res["set_info"][1] == set_name
    assert "item_count" in res["set_info"][10]
    assert res["set_info"][10]["item_count"] == str(N_GENOME_REFS)

    # test get of that object
    d1 = set_api_client.get_genome_set_v1(context, {"ref": res["set_ref"]})[0]
    assert "data" in d1
    assert "info" in d1
    assert len(d1["info"]) == INFO_LENGTH
    assert "item_count" in d1["info"][10]
    assert d1["info"][10]["item_count"] == str(N_GENOME_REFS)

    assert d1["data"]["description"] == set_description
    assert len(d1["data"]["items"]) == N_GENOME_REFS

    item2 = d1["data"]["items"][1]
    assert "info" not in item2
    assert "ref" in item2
    assert "label" in item2
    assert item2["label"] == "genome2"
    assert item2["ref"] == genome_refs[1]

    # test the call to make sure we get info for each item
    d2 = set_api_client.get_reads_set_v1(
        context,
        {
            "ref": res["set_ref"],
            "include_item_info": 1,
            "include_set_item_ref_paths": 1,
        },
    )[0]
    assert "data" in d2
    assert "info" in d2
    assert len(d2["info"]) == INFO_LENGTH
    assert "item_count" in d2["info"][10]
    assert d2["info"][10]["item_count"] == str(N_GENOME_REFS)

    assert d2["data"]["description"] == set_description
    assert len(d2["data"]["items"]) == N_GENOME_REFS

    item2 = d2["data"]["items"][1]
    assert "info" in item2
    assert len(item2["info"]), INFO_LENGTH
    assert "ref" in item2
    assert item2["ref"] == genome_refs[1]

    assert "ref_path" in item2
    assert item2["ref_path"] == res["set_ref"] + ";" + item2["ref"]


def test_save_and_get_kbasesearch_genome(
    genome_refs: list[str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> None:
    set_name = "set_of_kbasesearch_genomes"

    # create the set object
    set_data = {
        "description": "my kbasesearch genome set",
        "elements": {
            genome_refs[0]: {
                "ref": genome_refs[0],
                "metadata": {"test_metadata": "metadata"},
            },
            genome_refs[1]: {
                "ref": genome_refs[1],
                "metadata": {"test_metadata": "metadata"},
            },
        },
    }

    # test a save
    res = set_api_client.save_genome_set_v1(
        context,
        {
            "data": set_data,
            "output_object_name": set_name,
            "workspace_id": ws_id,
            "save_search_set": True,
        },
    )[0]

    assert "set_ref" in res
    assert "set_info" in res
    assert len(res["set_info"]) == INFO_LENGTH

    assert res["set_info"][1] == set_name
    assert "KBaseSearch.GenomeSet" in res["set_info"][2]

    # test get of that object
    d1 = set_api_client.get_genome_set_v1(context, {"ref": res["set_ref"]})[0]
    assert "data" in d1
    assert "info" in d1
    assert len(d1["info"]) == INFO_LENGTH
    assert "KBaseSearch.GenomeSet" in res["set_info"][2]

    assert d1["data"]["description"] == "my kbasesearch genome set"
    assert len(d1["data"]["elements"]) == N_GENOME_REFS

    elements = d1["data"]["elements"]
    assert genome_refs[0] in elements
    assert genome_refs[1] in elements

    genome_2 = elements.get(genome_refs[1])
    assert "ref" in genome_2
    assert genome_2.get("ref") == genome_refs[1]
    assert genome_2["metadata"]["test_metadata"] == "metadata"


def test_save_and_get_of_empty_set(
    set_api_client: SetAPI, context: dict[str, str | list], ws_id: int
) -> None:
    set_name = "nada_set"
    set_description = "nothing to see here"

    # create the set object
    set_data = {"description": set_description, "items": []}
    # test a save
    res = set_api_client.save_genome_set_v1(
        context,
        {
            "data": set_data,
            "output_object_name": set_name,
            "workspace_id": ws_id,
        },
    )[0]
    assert "set_ref" in res
    assert "set_info" in res
    assert len(res["set_info"]) == INFO_LENGTH

    assert res["set_info"][1] == set_name
    assert "item_count" in res["set_info"][10]
    assert res["set_info"][10]["item_count"] == "0"

    # test get of that object
    d1 = set_api_client.get_genome_set_v1(context, {"ref": res["set_ref"]})[0]
    assert "data" in d1
    assert "info" in d1
    assert len(d1["info"]) == INFO_LENGTH
    assert "item_count" in d1["info"][10]
    assert d1["info"][10]["item_count"] == "0"

    assert d1["data"]["description"] == set_description
    assert len(d1["data"]["items"]) == 0

    d2 = set_api_client.get_genome_set_v1(
        context, {"ref": res["set_ref"], "include_item_info": 1}
    )[0]

    assert "data" in d2
    assert "info" in d2
    assert len(d2["info"]) == INFO_LENGTH
    assert "item_count" in d2["info"][10]
    assert d2["info"][10]["item_count"] == "0"

    assert d2["data"]["description"] == set_description
    assert len(d2["data"]["items"]) == 0
