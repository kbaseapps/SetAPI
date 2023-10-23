import os
import time
from configparser import ConfigParser

from SetAPI.SetAPIImpl import SetAPI
from SetAPI.SetAPIServer import MethodContext
from installed_clients.authclient import KBaseAuth
from installed_clients.WorkspaceClient import Workspace

CONFIG_FILE = "./deploy.cfg"

def parse_config():
    config_file = os.environ.get("KB_DEPLOYMENT_CONFIG", CONFIG_FILE)
    print(f"Retrieving config from {config_file}")
    cfg_dict = {}
    config = ConfigParser()
    config.read(config_file)
    for nameval in config.items("SetAPI"):
        cfg_dict[nameval[0]] = nameval[1]
    return cfg_dict

def get_test_config():
    conf = parse_config()

    # retrieve a token from the auth client
    auth_client = KBaseAuth(
        conf.get(
            'auth-service-url',
            "https://kbase.us/services/authorization/Sessions/Login"))
    token = os.environ.get('KB_AUTH_TOKEN', None)

    # set up the context
    ctx = MethodContext(None)
    ctx.update({
        'token': token,
        'user_id': auth_client.get_user(token),
        'provenance': [{
            'service': 'SetAPI',
            'method': 'please_never_use_it_in_production',
            'method_params': []
        }],
        'authenticated': 1
    })

    # set up the SetAPI implementation
    impl = SetAPI(conf)

    # create a workspace for the tests
    suffix = int(time.time() * 1000)
    ws_name = "test_SetAPI_" + str(suffix)
    ws_url = conf['workspace-url']
    ws_client = Workspace(ws_url, token=token)
    ws_client.create_workspace({'workspace': ws_name})

    return {
        "cfg": conf,
        "ctx": ctx,
        "serviceImpl": impl,
        "wsClient": ws_client,
        "wsName": ws_name,
        "wsURL": ws_url,
    }
