"""Fixtures and global settings for the tests."""
import json
import os
import shutil
import time
from configparser import ConfigParser
from test import TEST_BASE_DIR
from test.util import (
    log_this,
    make_fake_alignment,
    make_fake_annotation,
    make_fake_expression,
    make_fake_rnaseq_alignment_set,
    make_fake_rnaseq_expression_set,
    make_fake_sampleset,
    make_fake_feature_set,
    make_fake_diff_exp_matrix,
)
from typing import Any
from collections.abc import Generator

import pytest
from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.authclient import KBaseAuth
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.FakeObjectsForTestsClient import FakeObjectsForTests
from installed_clients.WorkspaceClient import Workspace
from SetAPI.SetAPIImpl import SetAPI
from SetAPI.SetAPIServer import MethodContext
from SetAPI.util import info_to_ref

CONFIG_FILE = os.environ.get(
    "KB_DEPLOYMENT_CONFIG", os.path.join(TEST_BASE_DIR, "./deploy.cfg")
)

TOKEN = os.environ.get("KB_AUTH_TOKEN", None)
SDK_CALLBACK_URL = os.environ["SDK_CALLBACK_URL"]


@pytest.fixture(scope="session")
def config() -> dict[str, str]:
    """Parses the configuration file and retrieves the values
    under the SetAPI header.

    :return: dictionary of key-value pairs
    :rtype: dict[str, Any]
    """
    print(f"Retrieving config from {CONFIG_FILE}")
    cfg_dict = {}
    config_parser = ConfigParser()
    config_parser.read(CONFIG_FILE)
    for nameval in config_parser.items("SetAPI"):
        cfg_dict[nameval[0]] = nameval[1]

    return cfg_dict


@pytest.fixture(scope="session")
def context(config: dict[str, str]) -> dict[str, str | list]:
    """Generate the context that is sent with API requests.

    :param config: SetAPI config
    :type config: dict[str, str]
    :return: context data structure
    :rtype: dict[str, str | list]
    """
    # retrieve a token from the auth client
    auth_client = KBaseAuth(
        config.get(
            "auth-service-url", "https://kbase.us/services/authorization/Sessions/Login"
        )
    )

    # set up the context
    context = MethodContext(None)
    context.update(
        {
            "token": TOKEN,
            "user_id": auth_client.get_user(TOKEN),
            "provenance": [
                {
                    "service": "SetAPI",
                    "method": "please_never_use_it_in_production",
                    "method_params": [],
                }
            ],
            "authenticated": 1,
        }
    )
    return context


@pytest.fixture(scope="session")
def test_workspaces(
    config: dict[str, str], context: dict[str, str | list]
) -> Generator[dict[str, Any], Any, Any]:
    """Set up the workspace-related variables.

    These are generated in one fixture function and then split up by other
    fixtures for ease of accessing the products by variable name.

    :param config: SetAPI config
    :type config: dict[str, str]
    :param context: context object
    :type context: dict[str, str|list]
    :yield: dict containing a workspace client, and ws name and ws ID for the default and list all sets workspaces.
    :rtype: dict[str, Any]
    """
    ws_name = f"test_SetAPI_{int(time.time() * 1000)}"
    list_all_sets_ws_name = f"list_all_sets_{ws_name}"
    ws_client = Workspace(config["workspace-url"], token=TOKEN)
    # create workspaces for the tests
    default_ws_info = ws_client.create_workspace({"workspace": ws_name})
    list_all_sets_ws_info = ws_client.create_workspace(
        {"workspace": list_all_sets_ws_name}
    )

    ws_id = default_ws_info[0]
    list_all_sets_ws_id = list_all_sets_ws_info[0]
    yield {
        "ws_client": ws_client,
        "ws_name": ws_name,
        "ws_id": ws_id,
        "list_all_sets_ws_name": list_all_sets_ws_name,
        "list_all_sets_ws_id": list_all_sets_ws_id,
    }

    # check what is in the workspaces
    all_objs_default = ws_client.list_objects({"ids": [ws_id], "includeMetadata": 1})
    all_objs_list_all_sets = ws_client.list_objects({"ids": [list_all_sets_ws_id]})

    # delete the test workspaces
    ws_client.delete_workspace({"workspace": ws_name})
    ws_client.delete_workspace({"workspace": list_all_sets_ws_name})

    log_this(
        config,
        "ws_results",
        {
            "config": config,
            "context": context,
            "ws_default_create": default_ws_info,
            "ws_list_all_sets_create": list_all_sets_ws_info,
            "list_objs_default": all_objs_default,
            "list_objs_list_all_sets": all_objs_list_all_sets,
        },
    )


@pytest.fixture(scope="session", autouse=True)
def ws_id(test_workspaces: dict[str, Any]) -> int:
    return test_workspaces["ws_id"]


@pytest.fixture(scope="session", autouse=True)
def ws_name(test_workspaces: dict[str, Any]) -> str:
    return test_workspaces["ws_name"]


@pytest.fixture(scope="session")
def list_all_sets_ws_name(test_workspaces: dict[str, Any]) -> int:
    return test_workspaces["list_all_sets_ws_name"]


@pytest.fixture(scope="session")
def list_all_sets_ws_id(test_workspaces: dict[str, Any]) -> int:
    return test_workspaces["list_all_sets_ws_id"]


@pytest.fixture(scope="session", autouse=True)
def set_api_client(config: dict[str, str]) -> SetAPI:
    # set up the SetAPI implementation
    return SetAPI(config)


@pytest.fixture(scope="session", autouse=True)
def clients(test_workspaces: dict[str, Any]) -> dict[str, Any]:
    """Set up other clients needed during the tests.
    The workspace client is included here because the WS needs to be
    set up before any of the other clients can be used -- otherwise,
    they will attempt to access a workspace that does not exist.

    :param test_workspace: output of the test_workspace fixture
    :type test_workspace: dict[str, Any]
    :return: dictionary of clients used in the tests
    :rtype: dict[str, Any]
    """
    return {
        "au": AssemblyUtil(SDK_CALLBACK_URL),
        "dfu": DataFileUtil(SDK_CALLBACK_URL),
        "foft": FakeObjectsForTests(SDK_CALLBACK_URL),
        "ws": test_workspaces["ws_client"],
    }


@pytest.fixture(scope="session")
def scratch_dir(config: dict[str, str]) -> str:
    """Calculate the path to the scratch directory and create it if it doesn't exist.

    :param config: config
    :type config: dict[str, str]
    :return: absolute path to the scratch directory
    :rtype: str
    """
    scratch_dir = config["scratch"]
    shutil.copytree(
        os.path.join(TEST_BASE_DIR, "data"), scratch_dir, dirs_exist_ok=True
    )
    return scratch_dir


@pytest.fixture(scope="session")
def samples_test_data() -> dict[str, Any]:
    """Read and return the samples test data.

    :return: samples test data in all its glory
    :rtype: dict[str, Any]
    """
    with open(
        os.path.join(TEST_BASE_DIR, "data", "sample_set_search_compare.json")
    ) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def dummy_shock_file_handle(clients: dict[str, Any], scratch_dir: str) -> str:
    """Upload a (tiny!) file to shock and return the resulting file.

    :param clients: clients dictionary
    :type clients: dict[str, Any]
    :param scratch_dir: scratch directory containing the dummy file
    :type scratch_dir: str
    :return: shock handle for the uploaded file
    :rtype: str
    """
    # "dummy.txt" lives in the test/data/ directory and is copied to the scratch dir during test set up
    dummy_file_info = clients["dfu"].file_to_shock(
        {"file_path": os.path.join(scratch_dir, "dummy.txt"), "make_handle": 1}
    )
    return dummy_file_info["handle"]


@pytest.fixture(scope="session")
def alignment_refs(
    clients: dict[str, Any],
    ws_id: int,
    genome_refs: list[str],
    reads_refs: list[str],
    dummy_shock_file_handle: str,
) -> list[str]:
    """Create some KBase alignment objects and return the refs.

    :param clients: clients dictionary
    :type clients: dict[str, Any]
    :param ws_id: workspace ID
    :type ws_id: int
    :param genome_refs: genome refs (see fixture)
    :type genome_refs: list[str]
    :param reads_refs: reads refs (see fixture)
    :type reads_refs: list[str]
    :param dummy_shock_file_handle: handle for dummy upload file
    :type dummy_shock_file_handle: str
    :return: list of KBase UPAs
    :rtype: list[str]
    """
    return [
        make_fake_alignment(
            dummy_shock_file_handle,
            f"fake_alignment_{idx}",
            reads_ref,
            genome_refs[0],
            ws_id,
            clients["ws"],
        )
        for idx, reads_ref in enumerate(reads_refs)
    ]


@pytest.fixture(scope="session")
def alignment_mismatched_genome_refs(
    clients: dict[str, Any],
    ws_id: int,
    genome_refs: list[str],
    reads_refs: list[str],
    dummy_shock_file_handle: str,
) -> list[str]:
    """Create some KBase alignment objects where the alignments use different genomes and return the refs.

    :param clients: clients dictionary
    :type clients: dict[str, Any]
    :param ws_id: workspace ID
    :type ws_id: int
    :param genome_refs: genome refs (see fixture)
    :type genome_refs: list[str]
    :param reads_refs: reads refs (see fixture)
    :type reads_refs: list[str]
    :param dummy_shock_file_handle: handle for dummy upload file
    :type dummy_shock_file_handle: str
    :return: list of KBase UPAs
    :rtype: list[str]
    """
    return [
        make_fake_alignment(
            dummy_shock_file_handle,
            f"mismatched_alignment_{idx}",
            reads_refs[0],
            genome_ref,
            ws_id,
            clients["ws"],
        )
        for idx, genome_ref in enumerate(genome_refs)
    ]


@pytest.fixture(scope="session")
def annotation_ref(
    clients: dict[str, Any],
    ws_id: int,
    dummy_shock_file_handle: str,
) -> str:
    """Create a KBase annotation object and return the ref.

    :param clients: clients dictionary
    :type clients: dict[str, Any]
    :param ws_id: workspace ID
    :type ws_id: int
    :param dummy_shock_file_handle: dummy upload file
    :type dummy_shock_file_handle: str
    :return: KBase UPA
    :rtype: str
    """
    return make_fake_annotation(
        dummy_shock_file_handle,
        "fake_annotation",
        ws_id,
        clients["ws"],
    )


@pytest.fixture(scope="session")
def assembly_refs(clients: dict[str, Any], ws_id: int, scratch_dir: str) -> list[str]:
    """Create KBase assembly objects and return the refs.

    :param clients: clients dictionary
    :type client: dict[str, Any]
    :param ws_id: workspace ID
    :type ws_id: int
    :param scratch_dir: scratch directory containing the seq.fna file
    :type scratch_dir: str
    :return: list of KBase UPAs
    :rtype: list[str]
    """

    # use the seq.fna file that was copied to the scratch dir
    fna_path = os.path.join(scratch_dir, "seq.fna")
    assembly_refs = [
        clients["au"].save_assembly_from_fasta2(
            {
                "file": {"path": fna_path},
                "workspace_id": ws_id,
                "assembly_name": f"assembly_obj_{n}",
            }
        )
        for n in range(2)
    ]

    return [assembly_ref["upa"] for assembly_ref in assembly_refs]


@pytest.fixture(scope="session")
def conditions() -> list[str]:
    """Some fantastical conditions that exist only in the realm of make-believe.

    :return: list of conditions
    :rtype: list[str]
    """
    return ["WT", "Cond1", "HY"]


@pytest.fixture(scope="session")
def condition_set_ref(
    clients: dict[str, Any], ws_id: int, conditions: list[str]
) -> str:
    """Make a reference to a condition set.

    :param clients: clients dict
    :type clients: dict[str, Any]
    :param ws_id: workspace ID
    :type ws_id: int
    :param conditions: list of conditions (see conditions fixture)
    :type conditions: list[str]
    :return: KBase UPA
    :rtype: str
    """
    # create a condition set
    condition_set_object_name = "test_Condition_Set"
    common_factor_data = {
        "factor_ont_id": "Custom:Term",
        "factor_ont_ref": "KbaseOntologies/Custom",
        "unit_ont_id": "Custom:Unit",
        "unit_ont_ref": "KbaseOntologies/Custom",
    }
    condition_set_data = {
        "conditions": {conditions[ix]: ["0", "0"] for ix in range(2)},
        "factors": [
            {"factor": "Time series design", "unit": "Hour", **common_factor_data},
            {
                "factor": "Treatment with Sirolimus",
                "unit": "nanogram per milliliter",
                **common_factor_data,
            },
        ],
        "ontology_mapping_method": "User Curation",
    }

    saved_condition_set_info = clients["dfu"].save_objects(
        {
            "id": ws_id,
            "objects": [
                {
                    "type": "KBaseExperiments.ConditionSet",
                    "data": condition_set_data,
                    "name": condition_set_object_name,
                }
            ],
        }
    )[0]
    return info_to_ref(saved_condition_set_info)


@pytest.fixture(scope="session")
def diff_exp_matrix_genome_refs(
    clients: dict[str, Any], ws_id: int, genome_refs: list[str]
) -> list[str]:
    """Create some differential expression matrix objects with genome refs and return the refs.

    :param clients: clients dictionary, including the fake objects for tests client
    :type client: dict[str, Any]
    :param ws_id: workspace ID
    :type ws_id: int
    :param genome_refs: genome refs (see genome_refs fixture)
    :type genome_refs: list[str]
    :return: list of KBase UPAs for the objects
    :rtype: list[str]
    """
    return [
        make_fake_diff_exp_matrix(
            f"fake_mat_genome_{i}",
            ws_id,
            clients["ws"],
            genome_ref=genome_refs[0],
        )
        for i in range(2)
    ]


@pytest.fixture(scope="session")
def diff_exp_matrix_mismatched_genome_refs(
    clients: dict[str, Any], ws_id: int, genome_refs: list[str]
) -> list[str]:
    """Create some DEM objects with genome refs, where the two DEMs have different ref genomes, and return the refs.

    :param clients: clients dictionary
    :type client: dict[str, Any]
    :param ws_id: workspace ID
    :type ws_id: int
    :param genome_refs: genome refs (see genome_refs fixture)
    :type genome_refs: list[str]
    :return: list of KBase UPAs for the objects
    :rtype: list[str]
    """
    return [
        make_fake_diff_exp_matrix(
            f"fake_mat_genome_{ix}",
            ws_id,
            clients["ws"],
            genome_ref=genome_ref,
        )
        for ix, genome_ref in enumerate(genome_refs)
    ]


@pytest.fixture(scope="session")
def diff_exp_matrix_no_genome_refs(clients, ws_id):
    """Create differential expression matrix objects without genome refs and return the refs.

    :param clients: clients dictionary, including the fake objects for tests client
    :type client: dict[str, Any]
    :param ws_id: workspace ID
    :type ws_id: int
    :return: list of KBase UPAs for the objects
    :rtype: list[str]
    """
    return [
        make_fake_diff_exp_matrix(f"fake_mat_no_genome_{i}", ws_id, clients["ws"])
        for i in range(3)
    ]


@pytest.fixture(scope="session")
def expression_refs(
    clients: dict[str, Any],
    ws_id: int,
    dummy_shock_file_handle: str,
    genome_refs: list[str],
    alignment_refs: list[str],
    annotation_ref: str,
) -> list[str]:
    """Create some expression objects and return the refs.

    :param clients: clients dictionary
    :type clients: dict[str, Any]
    :param ws_id: workspace ID
    :type ws_id: int
    :param dummy_shock_file_handle: handle for the dummy upload file
    :type dummy_shock_file_handle: str
    :param genome_refs: genome refs (see fixture)
    :type genome_refs: list[str]
    :param alignment_refs: alignment refs (see fixture)
    :type alignment_refs: list[str]
    :param annotation_ref: annotation ref (see fixture)
    :type annotation_ref: str
    :return: list of KBase UPAs for the created expression objects
    :rtype: list[str]
    """
    return [
        make_fake_expression(
            dummy_shock_file_handle,
            f"fake_expression_{idx}",
            genome_refs[0],
            annotation_ref,
            alignment_ref,
            ws_id,
            clients["ws"],
        )
        for idx, alignment_ref in enumerate(alignment_refs)
    ]


@pytest.fixture(scope="session")
def expression_mismatched_genome_refs(
    clients: dict[str, Any],
    ws_id: int,
    dummy_shock_file_handle: str,
    genome_refs: list[str],
    alignment_refs: list[str],
    annotation_ref: str,
) -> list[str]:
    """Create some expression objects where the genome object differs between expressions and return the refs.

    :param clients: clients dictionary
    :type clients: dict[str, Any]
    :param ws_id: workspace ID
    :type ws_id: int
    :param dummy_shock_file_handle: handle for the dummy upload file
    :type dummy_shock_file_handle: str
    :param genome_refs: genome refs (see fixture)
    :type genome_refs: list[str]
    :param alignment_refs: alignment refs (see fixture)
    :type alignment_refs: list[str]
    :param annotation_ref: annotation ref (see fixture)
    :type annotation_ref: str
    :return: list of KBase UPAs for the created expression objects
    :rtype: list[str]
    """
    return [
        make_fake_expression(
            dummy_shock_file_handle,
            f"mismatched_expression_{idx}",
            genome_ref,
            annotation_ref,
            alignment_refs[idx],
            ws_id,
            clients["ws"],
        )
        for idx, genome_ref in enumerate(genome_refs)
    ]


@pytest.fixture(scope="session")
def featureset_refs(
    clients: dict[str, Any], ws_id: int, genome_refs: list[str]
) -> list[str]:
    """Create some featuresets and return the refs.

    :param clients: clients dictionary
    :type client: dict[str, Any]
    :param ws_id: workspace ID
    :type ws_id: int
    :param genome_refs: genome refs (see genome_refs fixture)
    :type genome_refs: list[str]
    :return: list of KBase UPAs for the objects
    :rtype: list[str]
    """
    return [
        make_fake_feature_set(f"feature_set_{i}", genome_refs[0], ws_id, clients["ws"])
        for i in range(3)
    ]


@pytest.fixture(scope="session")
def genome_refs(clients: dict[str, Any], ws_id: int) -> list[str]:
    """Create some genomes and return the refs.

    :param clients: clients dictionary, including the fake objects for tests client
    :type client: dict[str, Any]
    :param ws_id: workspace ID
    :type ws_id: int
    :return: list of KBase UPAs for the objects
    :rtype: list[str]
    """
    genome_info = clients["foft"].create_fake_genomes(
        {"ws_id": ws_id, "obj_names": [f"genome_obj_{n}" for n in range(3)]}
    )
    return [info_to_ref(info) for info in genome_info]


@pytest.fixture(scope="session")
def reads_refs(clients: dict[str, Any], ws_id: int) -> list[str]:
    """Create some reads and return the refs.

    :param clients: clients dictionary, including the fake objects for tests client
    :type client: dict[str, Any]
    :param ws_id: workspace ID
    :type ws_id: int
    :return: list of KBase UPAs for the objects
    :rtype: list[str]
    """
    fake_reads_list = clients["foft"].create_fake_reads(
        {"ws_id": ws_id, "obj_names": [f"reads{n}" for n in range(4)]}
    )
    return [info_to_ref(info) for info in fake_reads_list]


@pytest.fixture(scope="session")
def rnaseq_alignment_sets(
    clients: dict[str, Any],
    ws_id: int,
    genome_refs: list[str],
    reads_refs: list[str],
    alignment_refs: list[str],
    sampleset_ref: str,
) -> list[str]:
    """Create some fun RNASeq alignment sets and return the refs.

    :param clients: clients dictionary
    :type clients: dict[str, Any]
    :param ws_id: workspace ID
    :type ws_id: int
    :param genome_refs: genome refs (see fixture)
    :type genome_refs: list[str]
    :param reads_refs: reads refs (see fixture)
    :type reads_refs: list[str]
    :param alignment_refs: alignment refs (see fixture)
    :type alignment_refs: list[str]
    :param sampleset_ref: sampleset ref (see fixture)
    :type sampleset_ref: str
    :return: list of KBase UPAs
    :rtype: list[str]
    """
    return [
        make_fake_rnaseq_alignment_set(
            f"fake_rnaseq_alignment_set_{i}",
            reads_refs,
            genome_refs[0],
            sampleset_ref,
            alignment_refs,
            ws_id,
            clients["ws"],
        )
        for i in range(2)
    ]


@pytest.fixture(scope="session")
def rnaseq_expression_set(
    clients: dict[str, Any],
    ws_id: int,
    genome_refs: list[str],
    sampleset_ref: str,
    alignment_refs: list[str],
    expression_refs: list[str],
    rnaseq_alignment_sets: list[str],
) -> str:
    """Create an RNASeq Expression Set and return the ref.

    :param clients: clients dictionary
    :type clients: dict[str, Any]
    :param ws_id: workspace ID
    :type ws_id: int
    :param genome_refs: genome refs (see fixture)
    :type genome_refs: list[str]
    :param sampleset_ref: sampleset ref (see fixture)
    :type sampleset_ref: str
    :param alignment_refs: alignment refs (see fixture)
    :type alignment_refs: list[str]
    :param expression_refs: expression refs (see fixture)
    :type expression_refs: list[str]
    :param rnaseq_alignment_sets: RNASeq alignment refs (see fixture)
    :type rnaseq_alignment_sets: list[str]
    :return: KBase UPA
    :rtype: str
    """
    return make_fake_rnaseq_expression_set(
        "fake_rnaseq_expression_set",
        genome_refs[0],
        sampleset_ref,
        alignment_refs,
        rnaseq_alignment_sets[0],
        expression_refs,
        ws_id,
        clients["ws"],
        True,
    )


@pytest.fixture(scope="session")
def sampleset_ref(clients: dict[str, Any], ws_id: int, reads_refs: list[str]) -> str:
    """Create a sampleset and return the reference.

    :param clients: clients dictionary
    :type clients: dict[str, Any]
    :param ws_id: workspace ID
    :type ws_id: int
    :param reads_refs: reads refs (see fixture)
    :type reads_refs: list[str]
    :return: KBase UPA for the object
    :rtype: str
    """
    return make_fake_sampleset(
        "test_sampleset",
        reads_refs,
        [f"cond_{n}" for n in range(len(reads_refs))],
        ws_id,
        clients["ws"],
    )
