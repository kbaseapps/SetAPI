"""Basic tests of the SampleSet API."""
from test.util import info_to_name, log_this, INFO_LENGTH
from copy import deepcopy

import pytest
from SetAPI.SetAPIImpl import SetAPI
from SetAPI.generic.constants import INC_ITEM_INFO, INC_ITEM_REF_PATHS

DESCRIPTION = "first pass at testing something or other"
DEBUG = False


@pytest.fixture(scope="module")
def create_sampleset_params(ws_id: int, ws_name: str) -> dict[str, int | str]:
    return {
        "ws_id": ws_id,
        "ws_name": ws_name,
        "sampleset_desc": DESCRIPTION,
        "domain": "euk",
        "platform": "Illumina",
        "source": "NCBI",
        "Library_type": "SingleEnd",
        "publication_id": "none",
        "string external_source_date": "not sure",
    }


def test_basic_save_and_get(
    create_sampleset_params: dict[str, int | str],
    reads_refs: list[str],
    conditions: list[str],
    config: dict[str, str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_name: str,
) -> None:
    set_name = "micromonas_rnaseq_test1_sampleset"
    n_items = 3  # three different reads_refs used
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
    res = set_api_client.create_sample_set(context, create_ss_params)[0]
    if DEBUG:
        log_this(config, "create_sample_set", res)

    assert "set_ref" in res
    assert "set_info" in res
    assert len(res["set_info"]) == INFO_LENGTH

    assert res["set_info"][1] == set_name
    assert "num_samples" in res["set_info"][10]
    assert res["set_info"][10]["num_samples"] == str(n_items)

    # test get of that object
    d1 = set_api_client.get_reads_set_v1(context, {"ref": ws_name + "/" + set_name})[0]
    assert "data" in d1
    assert "info" in d1
    assert len(d1["info"]) == INFO_LENGTH
    assert "item_count" in d1["info"][10]
    assert d1["info"][10]["item_count"] == n_items

    assert d1["data"]["description"] == DESCRIPTION
    assert len(d1["data"]["items"]) == n_items

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

    # same call, but use the set ref
    d1_via_set_ref = set_api_client.get_reads_set_v1(context, {"ref": res["set_ref"]})[
        0
    ]
    assert d1 == d1_via_set_ref

    # test the call to make sure we get info for each item
    d2 = set_api_client.get_reads_set_v1(
        context,
        {
            "ref": res["set_ref"],
            INC_ITEM_INFO: 1,
            INC_ITEM_REF_PATHS: 1,
        },
    )[0]
    assert "data" in d2
    assert "info" in d2
    assert len(d2["info"]) == INFO_LENGTH
    assert "item_count" in d2["info"][10]
    assert d2["info"][10]["item_count"] == n_items

    assert d2["data"]["description"] == DESCRIPTION
    assert len(d2["data"]["items"]) == n_items

    item2 = d2["data"]["items"][1]
    assert "info" in item2
    assert len(item2["info"]), INFO_LENGTH
    assert "ref" in item2
    assert item2["ref"] == reads_refs[1]

    assert "ref_path" in item2
    assert item2["ref_path"] == res["set_ref"] + ";" + item2["ref"]


def test_create_sample_set_workspace_param(
    create_sampleset_params: dict[str, str],
    reads_refs: list[str],
    conditions: list[str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    ws_name: str,
) -> None:
    """Check that we can use either a workspace ID or the workspace name as the 'ws_id' param."""
    set_name = "test_workspace_param_sampleset"
    ss_params = {
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
    for param in ["ws_id", "ws_name"]:
        del ss_params[param]

    # workspace ID string in ws_id field
    sampleset_ws_id = set_api_client.create_sample_set(
        context, {**deepcopy(ss_params), **{"ws_id": str(ws_id)}}
    )[0]
    assert sampleset_ws_id["set_info"][6] == ws_id
    assert info_to_name(sampleset_ws_id["set_info"]) == set_name
    sampleset_obj_id = sampleset_ws_id["set_info"][0]
    sampleset_ver_id = sampleset_ws_id["set_info"][4]

    # workspace ID as integers in ws_id field
    # this will create a new version of the previous sampleset
    sampleset_int_ws_id = set_api_client.create_sample_set(
        context, {**deepcopy(ss_params), **{"ws_id": int(ws_id)}}
    )[0]
    assert sampleset_int_ws_id["set_info"][6] == sampleset_ws_id["set_info"][6]
    assert info_to_name(sampleset_int_ws_id["set_info"]) == set_name
    assert sampleset_int_ws_id["set_info"][0] == sampleset_obj_id
    assert sampleset_int_ws_id["set_info"][4] == sampleset_ver_id + 1

    # workspace name in ws_id field
    # version 3 of the sampleset
    sampleset_ws_name = set_api_client.create_sample_set(
        context, {**deepcopy(ss_params), **{"ws_id": ws_name}}
    )[0]
    assert sampleset_ws_name["set_info"][6] == sampleset_ws_id["set_info"][6]
    assert info_to_name(sampleset_ws_name["set_info"]) == set_name
    assert sampleset_ws_name["set_info"][0] == sampleset_obj_id
    assert sampleset_ws_name["set_info"][4] == sampleset_ver_id + 2


def test_basic_save_and_get_condition_in_list(
    create_sampleset_params: dict[str, str],
    reads_refs: list[str],
    conditions: list[str],
    config: dict[str, str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
) -> None:
    set_name = "micromonas_rnaseq_test1_sampleset"
    n_items = 3  # 3 reads_refs used

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
    res = set_api_client.create_sample_set(context, create_ss_params)[0]

    if DEBUG:
        log_this(config, "create_sample_set_with_conditions", res)

    assert "set_ref" in res
    assert "set_info" in res
    assert len(res["set_info"]) == INFO_LENGTH

    assert res["set_info"][1] == set_name
    assert "num_samples" in res["set_info"][10]
    assert res["set_info"][10]["num_samples"] == str(n_items)

    # test get of that object
    d1 = set_api_client.get_reads_set_v1(context, {"ref": res["set_ref"]})[0]
    assert "data" in d1
    assert "info" in d1
    assert len(d1["info"]) == INFO_LENGTH
    assert "item_count" in d1["info"][10]
    assert d1["info"][10]["item_count"] == n_items

    assert d1["data"]["description"] == DESCRIPTION
    assert len(d1["data"]["items"]) == n_items

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
        context,
        {
            "ref": res["set_ref"],
            INC_ITEM_INFO: 1,
            INC_ITEM_REF_PATHS: 1,
        },
    )[0]
    assert "data" in d2
    assert "info" in d2
    assert len(d2["info"]) == INFO_LENGTH
    assert "item_count" in d2["info"][10]
    assert d2["info"][10]["item_count"] == n_items

    assert d2["data"]["description"] == DESCRIPTION
    assert len(d2["data"]["items"]) == n_items

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
    context: dict[str, str | list],
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
        set_api_client.create_sample_set(context, create_ss_params)


def test_non_list_string_conditions(
    create_sampleset_params: dict[str, str],
    reads_refs: list[str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
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
        set_api_client.create_sample_set(context, create_ss_params)
