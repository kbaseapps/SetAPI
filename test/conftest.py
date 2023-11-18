"""Fixtures and global settings for the tests."""
import json
import os
import shutil
import time
from configparser import ConfigParser
from test import TEST_BASE_DIR
from test.util import log_this, make_genome_refs, make_reads_refs
from typing import Any

import pytest
from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.authclient import KBaseAuth
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.FakeObjectsForTestsClient import FakeObjectsForTests
from installed_clients.WorkspaceClient import Workspace
from SetAPI.SetAPIImpl import SetAPI
from SetAPI.SetAPIServer import MethodContext

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
def test_workspace(
    config: dict[str, str], context: dict[str, str | list]
) -> dict[str, Any]:
    """Set up the workspace-related variables.

    These are generated in one fixture function and then split up by other
    fixtures for ease of accessing the products by variable name.

    :param config: SetAPI config
    :type config: dict[str, str]
    :param context: context object
    :type context: dict[str, str|list]
    :yield: dict containing ws name, ws ID, and a workspace client.
    :rtype: dict[str, Any]
    """
    ws_name = f"test_SetAPI_{int(time.time() * 1000)}"
    ws_client = Workspace(config["workspace-url"], token=TOKEN)
    # create a workspace
    result = ws_client.create_workspace({"workspace": ws_name})
    yield {"ws_client": ws_client, "ws_name": ws_name, "ws_id": result[0]}
    # delete the test workspace
    deletion = ws_client.delete_workspace({"workspace": ws_name})
    log_this(
        config,
        "ws_results",
        {
            "ws_create": result,
            "config": config,
            "context": context,
            "ws_delete": deletion,
        },
    )


@pytest.fixture(scope="session", autouse=True)
def ws_id(test_workspace: dict[str, Any]) -> int:
    return test_workspace["ws_id"]


@pytest.fixture(scope="session", autouse=True)
def ws_name(test_workspace: dict[str, Any]) -> str:
    return test_workspace["ws_name"]


@pytest.fixture(scope="session", autouse=True)
def set_api_client(config: dict[str, str]) -> SetAPI:
    # set up the SetAPI implementation
    return SetAPI(config)


@pytest.fixture(scope="session")
def clients(test_workspace: dict[str, Any]) -> dict[str, Any]:
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
        "ws": test_workspace["ws_client"],
    }


@pytest.fixture(scope="session")
def scratch_dir(config: dict[str, str]) -> str:
    scratch_dir = config["scratch"]
    shutil.copytree(
        os.path.join(TEST_BASE_DIR, "data"), scratch_dir, dirs_exist_ok=True
    )
    return scratch_dir


@pytest.fixture(scope="session")
def genome_refs(clients: dict[str, Any], ws_id: str) -> list[str]:
    return make_genome_refs(clients["foft"], ws_id)


@pytest.fixture(scope="session")
def reads_refs(clients: dict[str, Any], ws_id: str) -> list[str]:
    return make_reads_refs(clients["foft"], ws_id)


@pytest.fixture(scope="session")
def samples_test_data() -> dict[str, Any]:
    with open(
        os.path.join(TEST_BASE_DIR, "data", "sample_set_search_compare.json")
    ) as f:
        return json.load(f)
