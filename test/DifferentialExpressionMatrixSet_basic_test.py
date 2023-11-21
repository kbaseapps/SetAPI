"""Basic DifferentialExpressionMatrixSet tests."""
import pytest
from installed_clients.baseclient import ServerError
from SetAPI.SetAPIImpl import SetAPI
from SetAPI.util import info_to_ref


def test_save_diff_exp_matrix_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    diff_exp_matrix_genome_refs: list[str],
) -> None:
    set_name = "test_diff_exp_matrix_set"
    set_items = [{"label": "foo", "ref": ref} for ref in diff_exp_matrix_genome_refs]
    matrix_set = {"description": "test_matrix_set", "items": set_items}
    result = set_api_client.save_differential_expression_matrix_set_v1(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": set_name,
            "data": matrix_set,
        },
    )[0]
    assert result is not None
    assert "set_ref" in result
    assert "set_info" in result
    assert result["set_ref"] == info_to_ref(result["set_info"])
    assert result["set_info"][1] == set_name
    assert "KBaseSets.DifferentialExpressionMatrixSet" in result["set_info"][2]


def test_save_diff_exp_matrix_set_no_genome(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    diff_exp_matrix_no_genome_refs: list[str],
) -> None:
    set_name = "test_de_matrix_set_no_genome"
    set_items = [{"label": "foo", "ref": ref} for ref in diff_exp_matrix_no_genome_refs]
    matrix_set = {"description": "test_matrix_set", "items": set_items}
    result = set_api_client.save_differential_expression_matrix_set_v1(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": set_name,
            "data": matrix_set,
        },
    )[0]
    assert result is not None
    assert "set_ref" in result
    assert "set_info" in result
    assert result["set_ref"] == info_to_ref(result["set_info"])
    assert result["set_info"][1] == set_name
    assert "KBaseSets.DifferentialExpressionMatrixSet" in result["set_info"][2]


def test_save_dem_set_mismatched_genomes(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    diff_exp_matrix_mismatched_genome_refs: list[str],
) -> None:
    set_name = "dem_set_bad_genomes"
    set_description = "this_better_fail"
    set_items = [
        {"label": "dem", "ref": ref} for ref in diff_exp_matrix_mismatched_genome_refs
    ]
    matrix_set = {
        "description": set_description,
        "items": set_items,
    }
    with pytest.raises(
        ValueError,
        match="All Differential Expression Matrix objects in the set must use the same genome reference.",
    ):
        set_api_client.save_differential_expression_matrix_set_v1(
            context,
            {
                "workspace_id": ws_id,
                "output_object_name": set_name,
                "data": matrix_set,
            },
        )


def test_save_dem_set_no_data(
    set_api_client: SetAPI, context: dict[str, str | list], ws_id: int
) -> None:
    with pytest.raises(
        ValueError,
        match='"data" parameter field required to save a DifferentialExpressionMatrixSet',
    ):
        set_api_client.save_differential_expression_matrix_set_v1(
            context,
            {
                "workspace_id": ws_id,
                "output_object_name": "foo",
                "data": None,
            },
        )


def test_save_dem_set_no_dem(
    set_api_client: SetAPI, context: dict[str, str | list], ws_id: int
) -> None:
    with pytest.raises(
        ValueError,
        match="A DifferentialExpressionMatrixSet must contain at least one DifferentialExpressionMatrix object reference.",
    ):
        set_api_client.save_differential_expression_matrix_set_v1(
            context,
            {
                "workspace_id": ws_id,
                "output_object_name": "foo",
                "data": {"items": []},
            },
        )


def test_get_dem_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    diff_exp_matrix_no_genome_refs: list[str],
) -> None:
    set_name = "test_expression_set"
    set_items = [{"label": "wt", "ref": ref} for ref in diff_exp_matrix_no_genome_refs]
    dem_set = {"description": "test_test_diffExprMatrixSet", "items": set_items}
    dem_set_ref = set_api_client.save_differential_expression_matrix_set_v1(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": set_name,
            "data": dem_set,
        },
    )[0]["set_ref"]

    fetched_set = set_api_client.get_differential_expression_matrix_set_v1(
        context, {"ref": dem_set_ref, "include_item_info": 0}
    )[0]
    assert fetched_set is not None
    assert "data" in fetched_set
    assert "info" in fetched_set
    assert len(fetched_set["data"]["items"]) == len(diff_exp_matrix_no_genome_refs)
    assert dem_set_ref == info_to_ref(fetched_set["info"])
    for item in fetched_set["data"]["items"]:
        assert "info" not in item
        assert "ref" in item
        assert "ref_path" not in item
        assert "label" in item

    fetched_set_with_info = set_api_client.get_differential_expression_matrix_set_v1(
        context, {"ref": dem_set_ref, "include_item_info": 1}
    )[0]
    assert fetched_set_with_info is not None
    assert "data" in fetched_set_with_info
    for item in fetched_set_with_info["data"]["items"]:
        assert "info" in item
        assert "ref" in item
        assert "label" in item


def test_get_dem_set_ref_path(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    diff_exp_matrix_no_genome_refs: list[str],
) -> None:
    set_name = "test_diff_expression_set_ref_path"
    set_items = [{"label": "wt", "ref": ref} for ref in diff_exp_matrix_no_genome_refs]
    dem_set = {"description": "test_diffExprMatrixSet_ref_path", "items": set_items}
    dem_set_ref = set_api_client.save_differential_expression_matrix_set_v1(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": set_name,
            "data": dem_set,
        },
    )[0]["set_ref"]

    fetched_set_with_ref_path = (
        set_api_client.get_differential_expression_matrix_set_v1(
            context,
            {
                "ref": dem_set_ref,
                "include_item_info": 0,
                "include_set_item_ref_paths": 1,
            },
        )[0]
    )
    assert fetched_set_with_ref_path is not None
    assert "data" in fetched_set_with_ref_path
    assert "info" in fetched_set_with_ref_path
    assert len(fetched_set_with_ref_path["data"]["items"]) == len(
        diff_exp_matrix_no_genome_refs
    )
    assert dem_set_ref == info_to_ref(fetched_set_with_ref_path["info"])
    for item in fetched_set_with_ref_path["data"]["items"]:
        assert "info" not in item
        assert "ref" in item
        assert "label" in item
        assert "ref_path" in item
        assert item["ref_path"] == dem_set_ref + ";" + item["ref"]


def test_get_dem_set_bad_ref(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    with pytest.raises(
        ValueError, match='"ref" parameter must be a valid workspace reference'
    ):
        set_api_client.get_differential_expression_matrix_set_v1(
            context, {"ref": "not_a_ref"}
        )


def test_get_dem_set_bad_path(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    with pytest.raises(
        ServerError, match="JSONRPCError: -32500. Object 2 cannot be accessed: "
    ):
        set_api_client.get_differential_expression_matrix_set_v1(
            context, {"ref": "1/2/3", "path_to_set": ["foo", "bar"]}
        )


def test_get_dem_set_no_ref(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    with pytest.raises(
        ValueError,
        match='"ref" parameter field specifiying the DifferentialExpressionMatrix set is required',
    ):
        set_api_client.get_differential_expression_matrix_set_v1(context, {"ref": None})
