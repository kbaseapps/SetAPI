"""Basic ReadsAlignmentSet tests."""
from test.util import log_this

import pytest
from installed_clients.baseclient import ServerError
from SetAPI.SetAPIImpl import SetAPI
from SetAPI.util import info_to_ref

DEBUG = False
SET_TYPE = "KBaseSets.ReadsAlignmentSet"


def test_save_alignment_set(
    alignment_refs: list[str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> None:
    alignment_set_name = "test_alignment_set"
    alignment_set_description = "test_alignments"
    alignment_items = [{"label": "wt", "ref": ref} for ref in alignment_refs]
    alignment_set = {"description": alignment_set_description, "items": alignment_items}
    result = set_api_client.save_reads_alignment_set_v1(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": alignment_set_name,
            "data": alignment_set,
        },
    )[0]
    assert result is not None
    assert "set_ref" in result
    assert "set_info" in result
    assert result["set_ref"] == info_to_ref(result["set_info"])
    assert result["set_info"][1] == alignment_set_name
    assert "KBaseSets.ReadsAlignmentSet" in result["set_info"][2]


def test_save_alignment_set_mismatched_genomes(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    alignment_mismatched_genome_refs: list[str],
) -> None:
    set_name = "alignment_set_mismatched_genomes"
    set_description = "this_better_fail"
    set_items = [
        {"label": "al", "ref": ref} for ref in alignment_mismatched_genome_refs
    ]
    alignment_set = {
        "description": set_description,
        "items": set_items,
    }

    with pytest.raises(
        ValueError,
        match="All ReadsAlignments in the set must be aligned against "
        "the same genome reference",
    ):
        set_api_client.save_reads_alignment_set_v1(
            context,
            {
                "workspace_id": ws_id,
                "output_object_name": set_name,
                "data": alignment_set,
            },
        )


def test_save_alignment_set_no_data(
    set_api_client: SetAPI, context: dict[str, str | list], ws_id: int
) -> None:
    with pytest.raises(
        ValueError,
        match='"data" parameter field required to save a ReadsAlignmentSet',
    ):
        set_api_client.save_reads_alignment_set_v1(
            context,
            {
                "workspace_id": ws_id,
                "output_object_name": "foo",
                "data": None,
            },
        )


def test_save_alignment_set_no_alignments(
    set_api_client: SetAPI, context: dict[str, str | list], ws_id: int
) -> None:
    with pytest.raises(
        ValueError,
        match="A ReadsAlignmentSet must contain at least one ReadsAlignment reference.",
    ):
        set_api_client.save_reads_alignment_set_v1(
            context,
            {
                "workspace_id": ws_id,
                "output_object_name": "foo",
                "data": {"items": []},
            },
        )


def test_get_old_alignment_set(
    rnaseq_alignment_sets: list[str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    reads_refs: list[str],
) -> None:
    n_items = len(reads_refs)
    for ref in rnaseq_alignment_sets:
        fetched_set = set_api_client.get_reads_alignment_set_v1(
            context, {"ref": ref, "include_item_info": 0}
        )[0]
        assert fetched_set is not None
        assert "data" in fetched_set
        assert "info" in fetched_set
        assert len(fetched_set["data"]["items"]) == n_items
        assert ref == info_to_ref(fetched_set["info"])
        for item in fetched_set["data"]["items"]:
            assert "info" not in item
            assert "ref" in item
            assert "label" in item

        fetched_set_with_info = set_api_client.get_reads_alignment_set_v1(
            context,
            {
                "ref": ref,
                "include_item_info": 1,
                "include_set_item_ref_paths": 1,
            },
        )[0]
        assert fetched_set_with_info is not None
        assert "data" in fetched_set_with_info
        for item in fetched_set_with_info["data"]["items"]:
            assert "info" in item
            assert "ref" in item
            assert "label" in item
            assert "ref_path" in item
            assert item["ref_path"] == ref + ";" + item["ref"]


def test_get_old_alignment_set_ref_path_to_set(
    config: dict[str, str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    rnaseq_alignment_sets: list[str],
    rnaseq_expression_set: str,
    reads_refs: list[str],
) -> None:
    alignment_ref = rnaseq_alignment_sets[0]
    ref_path_to_set = [rnaseq_expression_set, alignment_ref]
    n_items = len(reads_refs)

    fetched_set = set_api_client.get_reads_alignment_set_v1(
        context,
        {
            "ref": alignment_ref,
            "ref_path_to_set": ref_path_to_set,
            "include_item_info": 0,
            "include_set_item_ref_paths": 1,
        },
    )[0]
    assert fetched_set is not None
    assert "data" in fetched_set
    assert "info" in fetched_set
    assert len(fetched_set["data"]["items"]) == n_items
    assert alignment_ref == info_to_ref(fetched_set["info"])
    for item in fetched_set["data"]["items"]:
        assert "info" not in item
        assert "ref" in item
        assert "label" in item
        assert "ref_path" in item
        assert item["ref_path"] == ";".join(ref_path_to_set) + ";" + item["ref"]

    if DEBUG:
        log_this(config, "RNASeq_Alignment_with_ref_path_to_set", fetched_set)


def test_get_alignment_set(
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
    alignment_refs: list[str],
) -> None:
    alignment_set_name = "test_alignment_set"
    alignment_items = [{"label": "wt", "ref": ref} for ref in alignment_refs]
    n_items = len(alignment_refs)
    alignment_set = {"description": "test_alignments", "items": alignment_items}
    alignment_set_ref = set_api_client.save_reads_alignment_set_v1(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": alignment_set_name,
            "data": alignment_set,
        },
    )[0]["set_ref"]

    fetched_set = set_api_client.get_reads_alignment_set_v1(
        context, {"ref": alignment_set_ref, "include_item_info": 0}
    )[0]
    assert fetched_set is not None
    assert "data" in fetched_set
    assert "info" in fetched_set
    assert len(fetched_set["data"]["items"]) == n_items
    assert alignment_set_ref == info_to_ref(fetched_set["info"])
    for item in fetched_set["data"]["items"]:
        assert "info" not in item
        assert "ref" in item
        assert "label" in item

    fetched_set_with_info = set_api_client.get_reads_alignment_set_v1(
        context, {"ref": alignment_set_ref, "include_item_info": 1}
    )[0]
    assert fetched_set_with_info is not None
    assert "data" in fetched_set_with_info
    for item in fetched_set_with_info["data"]["items"]:
        assert "info" in item
        assert "ref" in item
        assert "label" in item


def test_get_alignment_set_ref_path(
    alignment_refs: list[str],
    set_api_client: SetAPI,
    context: dict[str, str | list],
    ws_id: int,
) -> None:
    alignment_set_name = "test_alignment_set_ref_path"
    alignment_items = [{"label": "wt", "ref": ref} for ref in alignment_refs]
    n_items = len(alignment_refs)
    alignment_set = {"description": "test_alignments", "items": alignment_items}
    alignment_set_ref = set_api_client.save_reads_alignment_set_v1(
        context,
        {
            "workspace_id": ws_id,
            "output_object_name": alignment_set_name,
            "data": alignment_set,
        },
    )[0]["set_ref"]

    fetched_set = set_api_client.get_reads_alignment_set_v1(
        context,
        {
            "ref": alignment_set_ref,
            "include_item_info": 0,
            "include_set_item_ref_paths": 1,
        },
    )[0]
    assert fetched_set is not None
    assert "data" in fetched_set
    assert "info" in fetched_set
    assert len(fetched_set["data"]["items"]) == n_items
    assert alignment_set_ref == info_to_ref(fetched_set["info"])
    for item in fetched_set["data"]["items"]:
        assert "info" not in item
        assert "ref" in item
        assert "label" in item
        assert "ref_path" in item
        assert item["ref_path"] == alignment_set_ref + ";" + item["ref"]


def test_get_alignment_set_bad_ref(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    with pytest.raises(
        ValueError, match='"ref" parameter must be a valid workspace reference'
    ):
        set_api_client.get_reads_alignment_set_v1(context, {"ref": "not_a_ref"})


def test_get_alignment_set_bad_path(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    with pytest.raises(
        ServerError, match="JSONRPCError: -32500. Object 2 cannot be accessed:"
    ):
        set_api_client.get_reads_alignment_set_v1(
            context, {"ref": "1/2/3", "path_to_set": ["foo", "bar"]}
        )


def test_get_alignment_set_no_ref(
    set_api_client: SetAPI, context: dict[str, str | list]
) -> None:
    with pytest.raises(
        ValueError,
        match='"ref" parameter field specifiying the reads alignment set is required',
    ):
        set_api_client.get_reads_alignment_set_v1(context, {"ref": None})
