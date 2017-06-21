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

def info_to_ref(info):
    return "{}/{}/{}".format(info[6], info[0], info[4])

class ReadsAlignmentSetAPITest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('SetAPI'):
            cls.cfg[nameval[0]] = nameval[1]
        authServiceUrl = cls.cfg.get('auth-service-url',
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
        ret = cls.wsClient.create_workspace({'workspace': wsName})
        cls.wsName = wsName

        foft = FakeObjectsForTests(os.environ['SDK_CALLBACK_URL'])

        [fake_genome] = foft.create_fake_genomes({
            "ws_name": wsName,
            "obj_names": ["fake_genome"]
        })
        cls.genome_ref = info_to_ref(fake_genome)
        fake_reads_list = foft.create_fake_reads({
            'ws_name': wsName,
            "obj_names": ["reads1", "reads2", "reads3"]
        })
        cls.alignment_refs = list()
        cls.reads_refs = list()
        for idx, reads_info in enumerate(fake_reads_list):
            reads_ref = info_to_ref(reads_info)
            cls.reads_refs.append(reads_ref)
            cls.alignment_refs.append(info_to_ref(foft.create_any_objects({
                "ws_name": wsName,
                "obj_names": ["reads_align_{}".format(idx)],
                "metadata": {
                    "genome_id": cls.genome_ref,
                    "read_sample_id": reads_ref
                }
            })[0]))

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_SetAPI_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def test_save_alignment_set(self):
        alignment_set_name = "test_alignment_set"
        alignment_items = list()
        for ref in self.alignment_refs:
            alignment_items.append({
                "label": "wt",
                "ref": ref
            })
        alignment_set = {
            "description": "test_alignments",
            "items": alignment_items
        }
        result = self.getImpl().save_reads_alignment_set_v1(self.getContext(), {
            "workspace": self.getWsName(),
            "output_object_name": alignment_set_name,
            "data": alignment_set
        })
        self.assertIsNotNone(result)
        self.assertIn("set_ref", result)
        self.assertIn("set_info", result)
