"""Fixtures and global settings for the tests."""
import os
import time
from configparser import ConfigParser
from test import TEST_BASE_DIR
from test.util import make_reads_refs, make_genome_refs
from typing import Any

import pytest
from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.authclient import KBaseAuth
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.FakeObjectsForTestsClient import FakeObjectsForTests
from installed_clients.WorkspaceClient import Workspace
from SetAPI.SetAPIImpl import SetAPI
from SetAPI.SetAPIServer import MethodContext
import json

CONFIG_FILE = os.environ.get(
    "KB_DEPLOYMENT_CONFIG", os.path.join(TEST_BASE_DIR, "./deploy.cfg")
)

TOKEN = os.environ.get("KB_AUTH_TOKEN", None)
SDK_CALLBACK_URL = os.environ["SDK_CALLBACK_URL"]
INFO_LENGTH = 11


@pytest.fixture(scope="session")
def config() -> dict[str, str]:
    """Generate various useful values and variables for testing.

    Parses the configuration file and retrieves the values
    under the SetAPI header. Combines these values with
    environment variables to create a workspace, a token, a
    context, a config, and more!

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
def ctx(config: dict[str, str]) -> dict[str, str | list]:
    # retrieve a token from the auth client
    auth_client = KBaseAuth(
        config.get(
            "auth-service-url", "https://kbase.us/services/authorization/Sessions/Login"
        )
    )

    # set up the context
    ctx = MethodContext(None)
    ctx.update(
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
    return ctx


@pytest.fixture(scope="session")
def test_workspace(
    config: dict[str, str], ctx: dict[str, str | list]
) -> dict[str, Any]:
    ws_name = f"test_SetAPI_{int(time.time() * 1000)}"
    ws_client = Workspace(config["workspace-url"], token=TOKEN)
    # create a workspace
    result = ws_client.create_workspace({"workspace": ws_name})
    output_file = f"{config['scratch']}/create_ws_result"
    import json

    with open(output_file, "w") as f:
        f.write(
            json.dumps(
                {"ws_create": result, "config": config, "ctx": ctx},
                indent=2,
                sort_keys=True,
            )
        )
    return {"ws_client": ws_client, "ws_name": ws_name, "ws_id": result[0]}


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
    return {
        "au": AssemblyUtil(SDK_CALLBACK_URL),
        "dfu": DataFileUtil(SDK_CALLBACK_URL),
        "foft": FakeObjectsForTests(SDK_CALLBACK_URL),
        "ws": test_workspace["ws_client"],
    }


@pytest.fixture(scope="session")
def reads_refs(clients: dict[str, Any], ws_name: str) -> list[str]:
    return make_reads_refs(clients["foft"], ws_name)


@pytest.fixture(scope="session")
def genome_refs(clients: dict[str, Any], ws_name: str) -> list[str]:
    return make_genome_refs(clients["foft"], ws_name)


@pytest.fixture(scope="session")
def samples_test_data() -> dict[str, Any]:
    with open(
        os.path.join(TEST_BASE_DIR, "data", "sample_set_search_compare.json")
    ) as f:
        return json.load(f)
