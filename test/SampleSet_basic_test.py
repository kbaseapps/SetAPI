"""Basic tests of the SampleSet API."""
from test.conftest import INFO_LENGTH
from test.util import info_to_ref, log_this
from typing import Any

import pytest
from SetAPI.SetAPIImpl import SetAPI

N_READS = 3
DESCRIPTION = "first pass at testing something or other"
DEBUG = False

@pytest.fixture(scope="module")
def create_sampleset_params(ws_name: str) -> dict[str]:
    return {
        "ws_id": ws_name,
        "sampleset_desc": DESCRIPTION,
        "domain": "euk",
        "platform": "Illumina",
        "source": "NCBI",
        "Library_type": "SingleEnd",
        "publication_id": "none",
        "string external_source_date": "not sure",
    }


@pytest.fixture(scope="session")
def conditions() -> list[str]:
    return ["WT", "Cond1", "HY"]


@pytest.fixture(scope="module")
def condition_set_ref(
    clients: dict[str, Any], ws_id: int, conditions: list[str]
) -> str:
    # create a condition set
    condition_set_object_name = "test_Condition_Set"
    condition_set_data = {
        "conditions": {
            conditions[0]: ["0", "0"],
            conditions[1]: ["0", "0"],
            conditions[2]: ["0", "0"],
        },
        "factors": [
            {
                "factor": "Time series design",
                "factor_ont_id": "Custom:Term",
                "factor_ont_ref": "KbaseOntologies/Custom",
                "unit": "Hour",
                "unit_ont_id": "Custom:Unit",
                "unit_ont_ref": "KbaseOntologies/Custom",
            },
            {
                "factor": "Treatment with Sirolimus",
                "factor_ont_id": "Custom:Term",
                "factor_ont_ref": "KbaseOntologies/Custom",
                "unit": "nanogram per milliliter",
                "unit_ont_id": "Custom:Unit",
                "unit_ont_ref": "KbaseOntologies/Custom",
            },
        ],
        "ontology_mapping_method": "User Curation",
    }
    save_object_params = {
        "id": ws_id,
        "objects": [
            {
                "type": "KBaseExperiments.ConditionSet",
                "data": condition_set_data,
                "name": condition_set_object_name,
            }
        ],
    }

    dfu_oi = clients["dfu"].save_objects(save_object_params)[0]
    return info_to_ref(dfu_oi)


def test_basic_save_and_get(
    create_sampleset_params: dict[str, str],
    reads_refs: list[str],
    conditions: list[str],
    config: dict[str, str],
    set_api_client: SetAPI,
    ctx: dict[str, str | list],
    ws_name: str,
) -> None:
    set_name = "micromonas_rnaseq_test1_sampleset"

    # create the set object
    create_ss_params = {
        **create_sampleset_params,
        "sampleset_id": set_name,
        "sample_n_conditions": [
            {"sample_id": [reads_refs[0]], "condition": conditions[0]},
            {
                "sample_id": [reads_refs[1], reads_refs[2]],
                "condition": conditions[1],
            },
        ],
    }

    # test a save
    res = set_api_client.create_sample_set(ctx, create_ss_params)[0]
    if DEBUG:
        log_this(config, "create_sample_set", res)

    assert "set_ref" in res
    assert "set_info" in res
    assert len(res["set_info"]) == INFO_LENGTH

    assert res["set_info"][1] == set_name
    assert "num_samples" in res["set_info"][10]
    assert res["set_info"][10]["num_samples"] == str(N_READS)

    # test get of that object
    d1 = set_api_client.get_reads_set_v1(ctx, {"ref": ws_name + "/" + set_name})[0]
    assert "data" in d1
    assert "info" in d1
    assert len(d1["info"]) == INFO_LENGTH
    assert "item_count" in d1["info"][10]
    assert d1["info"][10]["item_count"] == N_READS

    assert d1["data"]["description"] == DESCRIPTION
    assert len(d1["data"]["items"]) == N_READS

    item2 = d1["data"]["items"][1]
    assert "info" not in item2
    assert "ref" in item2
    assert "label" in item2
    assert item2["label"] == conditions[1]
    assert item2["ref"] == reads_refs[1]

    item3 = d1["data"]["items"][2]
    assert "info" not in item3
    assert "ref" in item3
    assert "label" in item3
    assert item3["label"] == conditions[1]
    assert item3["ref"] == reads_refs[2]

    # test the call to make sure we get info for each item
    d2 = set_api_client.get_reads_set_v1(
        ctx,
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
    assert d2["info"][10]["item_count"] == N_READS

    assert d2["data"]["description"] == DESCRIPTION
    assert len(d2["data"]["items"]) == N_READS

    item2 = d2["data"]["items"][1]
    assert "info" in item2
    assert len(item2["info"]), INFO_LENGTH
    assert "ref" in item2
    assert item2["ref"] == reads_refs[1]

    assert "ref_path" in item2
    assert item2["ref_path"] == res["set_ref"] + ";" + item2["ref"]


def test_basic_save_and_get_condition_in_list(
    create_sampleset_params: dict[str, str],
    reads_refs: list[str],
    conditions: list[str],
    config: dict[str, str],
    ws_name: str,
    set_api_client: SetAPI,
    ctx: dict[str, str | list],
) -> None:
    set_name = "micromonas_rnaseq_test1_sampleset"

    # create the set object
    create_ss_params = {
        **create_sampleset_params,
        "sampleset_id": set_name,
        "sample_n_conditions": [
            {"sample_id": [reads_refs[0]], "condition": [conditions[0]]},
            {
                "sample_id": [reads_refs[1], reads_refs[2]],
                "condition": [conditions[1]],
            },
        ],
    }

    # test a save
    res = set_api_client.create_sample_set(ctx, create_ss_params)[0]

    if DEBUG:
        log_this(config, "create_sample_set_with_conditions", res)

    assert "set_ref" in res
    assert "set_info" in res
    assert len(res["set_info"]) == INFO_LENGTH

    assert res["set_info"][1] == set_name
    assert "num_samples" in res["set_info"][10]
    assert res["set_info"][10]["num_samples"] == str(N_READS)

    # test get of that object
    d1 = set_api_client.get_reads_set_v1(ctx, {"ref": ws_name + "/" + set_name})[0]
    assert "data" in d1
    assert "info" in d1
    assert len(d1["info"]) == INFO_LENGTH
    assert "item_count" in d1["info"][10]
    assert d1["info"][10]["item_count"] == N_READS

    assert d1["data"]["description"] == DESCRIPTION
    assert len(d1["data"]["items"]) == N_READS

    item2 = d1["data"]["items"][1]
    assert "info" not in item2
    assert "ref" in item2
    assert "label" in item2
    assert item2["label"] == conditions[1]
    assert item2["ref"] == reads_refs[1]

    item3 = d1["data"]["items"][2]
    assert "info" not in item3
    assert "ref" in item3
    assert "label" in item3
    assert item3["label"] == conditions[1]
    assert item3["ref"] == reads_refs[2]

    # test the call to make sure we get info for each item
    d2 = set_api_client.get_reads_set_v1(
        ctx,
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
    assert d2["info"][10]["item_count"] == N_READS

    assert d2["data"]["description"] == DESCRIPTION
    assert len(d2["data"]["items"]) == N_READS

    item2 = d2["data"]["items"][1]
    assert "info" in item2
    assert len(item2["info"]), INFO_LENGTH
    assert "ref" in item2
    assert item2["ref"] == reads_refs[1]

    assert "ref_path" in item2
    assert item2["ref_path"] == res["set_ref"] + ";" + item2["ref"]


@pytest.mark.skip("conditionset_ref not supported")
def test_unmatched_conditions(
    create_sampleset_params: dict[str, str],
    reads_refs: list[str],
    conditions: list[str],
    condition_set_ref: str,
    set_api_client: SetAPI,
    ctx: dict[str, str | list],
) -> None:
    # create the set object with unmatching conditions
    create_ss_params = {
        **create_sampleset_params,
        "sampleset_id": "some name",
        "sample_n_conditions": [
            {"sample_id": [reads_refs[0]], "condition": "unmatching_condition"},
            {
                "sample_id": [reads_refs[1], reads_refs[2]],
                "condition": conditions[1],
            },
        ],
        "conditionset_ref": condition_set_ref,
    }

    # test a save
    with pytest.raises(ValueError, match="ERROR: Given conditions"):
        set_api_client.create_sample_set(ctx, create_ss_params)


def test_non_list_string_conditions(
    create_sampleset_params: dict[str, str],
    reads_refs: list[str],
    set_api_client: SetAPI,
    ctx: dict[str, str | list],
) -> None:
    digital_condition = 10
    # create the set object with unmatching conditions
    create_ss_params = {
        **create_sampleset_params,
        "sampleset_id": "some name",
        "sample_n_conditions": [
            {"sample_id": [reads_refs[0]], "condition": digital_condition}
        ],
    }

    # test a save
    with pytest.raises(
        ValueError, match="ERROR: condition should be either a list or a string"
    ):
        set_api_client.create_sample_set(ctx, create_ss_params)
