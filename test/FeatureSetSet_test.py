# -*- coding: utf-8 -*-
import unittest
import os
import time

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from biokbase.workspace.client import Workspace as workspaceService
from SetAPI.SetAPIImpl import SetAPI
from SetAPI.SetAPIServer import MethodContext

from FakeObjectsForTests.FakeObjectsForTestsClient import FakeObjectsForTests
from SetAPI.authclient import KBaseAuth as _KBaseAuth

from util import (
    info_to_ref,
    make_fake_feature_set
)


class FeatureSetSetAPITest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('SetAPI'):
            cls.cfg[nameval[0]] = nameval[1]
        authServiceUrl = cls.cfg.get("auth-service-url",
                                     "https://kbase.us/services/authorization/Sessions/Login")
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'SetAPI',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL, token=token)
        cls.serviceImpl = SetAPI(cls.cfg)

        # setup data at the class level for now (so that the code is run
        # once for all tests, not before each test case.  Not sure how to
        # do that outside this function..)
        suffix = int(time.time() * 1000)
        wsName = "test_SetAPI_" + str(suffix)
        cls.wsClient.create_workspace({'workspace': wsName})
        cls.wsName = wsName

        foft = FakeObjectsForTests(os.environ['SDK_CALLBACK_URL'])

        # Make fake genomes
        [fake_genome, fake_genome2] = foft.create_fake_genomes({
            "ws_name": wsName,
            "obj_names": ["fake_genome", "fake_genome2"]
        })
        cls.genome_refs = [info_to_ref(fake_genome), info_to_ref(fake_genome2)]

        # Make some fake feature sets
        cls.featureset_refs = [make_fake_feature_set(
            "feature_set_{}".format(i),
            cls.genome_refs[0],
            wsName,
            cls.wsClient) for i in range(3)]

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        return self.__class__.wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def test_save_feature_set_set(self):
        pass

    def test_save_feature_set_set_mismatched_genomes(self):
        pass

    def test_save_feature_set_set_no_data(self):
        pass

    def test_get_feature_set_set(self):
        pass

    def test_get_feature_set_set_bad_ref(self):
        with self.assertRaises(ValueError) as err:
            self.getImpl().get_feature_set_set_v1(self.getContext(), {
                "ref": "not_a_ref"
            })
        self.assertIn('"ref" parameter must be a valid workspace reference', str(err.exception))

    def test_get_feature_set_set_bad_path(self):
        with self.assertRaises(Exception):
            self.getImpl().get_feature_set_set_v1(self.getContext(), {
                "ref": "1/2/3",
                "path_to_set": ["foo", "bar"]
            })

    def test_get_feature_set_set_no_ref(self):
        with self.assertRaises(ValueError) as err:
            self.getImpl().get_feature_set_set_v1(self.getContext(), {
                "ref": None
            })
        self.assertIn('"ref" parameter field specifiying the FeatureSet set is required',
                      str(err.exception))
