"""Fixtures and global settings for the tests."""
import os
import time
from configparser import ConfigParser
from test import TEST_BASE_DIR
from typing import Any

from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.authclient import KBaseAuth
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.FakeObjectsForTestsClient import FakeObjectsForTests
from installed_clients.WorkspaceClient import Workspace
from SetAPI.SetAPIImpl import SetAPI
from SetAPI.SetAPIServer import MethodContext

CONFIG_FILE = os.environ.get(
    "KB_DEPLOYMENT_CONFIG",
    os.path.join(TEST_BASE_DIR, "./deploy.cfg")
)

TOKEN = os.environ.get("KB_AUTH_TOKEN", None)
SDK_CALLBACK_URL = os.environ["SDK_CALLBACK_URL"]
INFO_LENGTH = 11

def get_test_config() -> dict[str, Any]:
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

    # retrieve a token from the auth client
    auth_client = KBaseAuth(
        cfg_dict.get(
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

    # set up the SetAPI implementation
    set_api_client = SetAPI(cfg_dict)

    # create a workspace for the tests
    ws_name = f"test_SetAPI_{int(time.time() * 1000)}"
    ws_url = cfg_dict["workspace-url"]
    ws_client = Workspace(ws_url, token=TOKEN)
    ws_client.create_workspace({"workspace": ws_name})

    return {
        "config": cfg_dict,
        "ctx": ctx,
        "set_api_client": set_api_client,
        "ws_client": ws_client,
        "ws_name": ws_name,
        "au": AssemblyUtil(SDK_CALLBACK_URL),
        "dfu": DataFileUtil(SDK_CALLBACK_URL),
        "foft": FakeObjectsForTests(SDK_CALLBACK_URL),
    }
