"""Tests for the SampleSetSearch."""
from copy import deepcopy
from typing import Any

import pytest
from SetAPI.SetAPIImpl import SetAPI

SAMPLE_SET_REF = "45700/57/1"


def compare_samples(s1: dict[str, Any], s2: dict[str, Any]) -> None:
    assert s1["num_found"] == s2["num_found"]
    assert s1["start"] == s2["start"]
    assert s1["samples"] == s2["samples"]


def test_param_error_conditions(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    # test without ref argument
    with pytest.raises(
        ValueError, match="Argument 'ref' must be specified, 'ref' = 'None'"
    ):
        set_api_client.sample_set_to_samples_info(context, {"start": 0, "limit": 10})


def test_param_error_conditions_empty_params(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    with pytest.raises(
        ValueError, match="Argument 'ref' must be specified, 'ref' = 'None'"
    ):
        set_api_client.sample_set_to_samples_info(context, {})


@pytest.mark.skip("only particular users have permission to search")
def test_sample_set_to_sample_info(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    samples_test_data: dict[str, Any],
) -> None:
    # test defaults of "start" and "limit" variables
    ret = set_api_client.sample_set_to_samples_info(
        context,
        {
            "ref": SAMPLE_SET_REF,
        },
    )[0]
    compare_samples(ret, samples_test_data)


@pytest.mark.skip("only particular users have permission to search")
def test_query_search(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    samples_test_data: dict[str, Any],
) -> None:
    ret = set_api_client.sample_set_to_samples_info(
        context,
        {"ref": SAMPLE_SET_REF, "start": 0, "limit": 10, "query": "Georgia"},
    )[0]

    compare_to = deepcopy(samples_test_data)
    # get the samples with state_province 'Georgia' only
    compare_to["samples"] = [
        s
        for s in compare_to["samples"]
        if s.get("state_province") and s["state_province"][0] == "Georgia"
    ]
    compare_to["num_found"] = len(compare_to["samples"])
    compare_samples(ret, compare_to)


@pytest.mark.skip("only particular users have permission to search")
def test_prefix_query_search(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    samples_test_data: dict[str, Any],
) -> None:
    ret = set_api_client.sample_set_to_samples_info(
        context, {"ref": SAMPLE_SET_REF, "query": "Germa"}
    )[0]

    # get the samples with country 'Germany' only
    compare_to = deepcopy(samples_test_data)
    compare_to["samples"] = [
        s
        for s in compare_to["samples"]
        if s.get("country") and s["country"][0] == "Germany"
    ]
    compare_to["num_found"] = len(compare_to["samples"])
    compare_samples(ret, compare_to)


@pytest.mark.skip("only particular users have permission to search")
def test_prefix_query_search_2(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    samples_test_data: dict[str, Any],
) -> None:
    ret = set_api_client.sample_set_to_samples_info(
        context, {"ref": SAMPLE_SET_REF, "query": "Ge"}
    )[0]

    # get the samples with country 'Germany' or state 'Georgia'
    compare_to = deepcopy(samples_test_data)
    compare_to["samples"] = [
        s
        for s in compare_to["samples"]
        if (s.get("country") and s["country"][0] == "Germany")
        or (s.get("state_province") and s["state_province"][0] == "Georgia")
    ]
    compare_to["num_found"] = len(compare_to["samples"])
    compare_samples(ret, compare_to)
