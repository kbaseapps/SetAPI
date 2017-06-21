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

        # Make a fake genome
        [fake_genome, fake_genome2] = foft.create_fake_genomes({
            "ws_name": wsName,
            "obj_names": ["fake_genome", "fake_genome2"]
        })
        cls.genome_refs = [info_to_ref(fake_genome), info_to_ref(fake_genome2)]

        # Make some fake reads objects
        fake_reads_list = foft.create_fake_reads({
            'ws_name': wsName,
            "obj_names": ["reads1", "reads2", "reads3"]
        })
        cls.alignment_refs = list()
        cls.reads_refs = list()

        # Make some fake alignments referencing those reads and genome
        for idx, reads_info in enumerate(fake_reads_list):
            reads_ref = info_to_ref(reads_info)
            cls.reads_refs.append(reads_ref)
            fake_alignment = {
                "file": {
                    "id": "not_a_real_handle"
                },
                "library_type": "fake",
                "read_sample_id": reads_ref,
                "condition": "fake",
                "genome_id": cls.genome_refs[0]
            }
            cls.alignment_refs.append(
                info_to_ref(
                    cls.wsClient.save_objects({
                        "workspace": wsName,
                        "objects": [{
                            "type": "KBaseRNASeq.RNASeqAlignment",
                            "data": fake_alignment,
                            "meta": dict(),
                            "name": "fake_alignment_{}".format(idx)
                        }]
                    })[0]
                )
            )

    def make_fake_alignment(self, name, reads_ref, genome_ref):
        """
        Makes a fake KBaseRNASeq.RNASeqAlignment object and returns a ref to it.
        """
        fake_alignment = {
            "file": {
                "id": "not_a_real_handle"
            },
            "library_type": "fake",
            "read_sample_id": reads_ref,
            "condition": "fake",
            "genome_id": genome_ref
        }
        return info_to_ref(
            self.wsClient.save_objects({
                "workspace": self.getWsName(),
                "objects": [{
                    "type": "KBaseRNASeq.RNASeqAlignment",
                    "data": fake_alignment,
                    "meta": dict(),
                    "name": name
                }]
            })[0]
        )

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
        })[0]
        self.assertIsNotNone(result)
        self.assertIn("set_ref", result)
        self.assertIn("set_info", result)
        self.assertEqual(result["set_ref"], info_to_ref(result["set_info"]))
        self.assertEqual(result["set_info"][1], alignment_set_name)
        self.assertIn("KBaseSets.ReadsAlignmentSet", result["set_info"][2])

    def test_save_alignment_set_mismatched_genomes(self):
        alignment_set_name = "alignment_set_bad_genomes"
        alignment_set = {
            "description": "this_better_fail",
            "items": [{
                "ref": self.make_fake_alignment("odd_alignment", self.reads_refs[0], self.genome_refs[1]),
                "label": "odd_alignment"
            }, {
                "ref": self.alignment_refs[1],
                "label": "wt"
            }]
        }
        with self.assertRaises(ValueError) as err:
            self.getImpl().save_reads_alignment_set_v1(self.getContext(), {
                "workspace": self.getWsName(),
                "output_object_name": alignment_set_name,
                "data": alignment_set
            })
            self.assertIn("All ReadsAlignments in the set must be aligned against the same genome reference", str(err.exception))

    def test_get_alignment_set(self):
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
        alignment_set_ref = self.getImpl().save_reads_alignment_set_v1(self.getContext(), {
            "workspace": self.getWsName(),
            "output_object_name": alignment_set_name,
            "data": alignment_set
        })[0]["set_ref"]

        fetched_set = self.getImpl().get_reads_alignment_set_v1(self.getContext(), {
            "ref": alignment_set_ref,
            "include_item_info": 0
        })[0]
        self.assertIsNotNone(fetched_set)
        self.assertIn("data", fetched_set)
        self.assertIn("info", fetched_set)
        self.assertEquals(len(fetched_set["data"]["items"]), 3)
        self.assertEquals(alignment_set_ref, info_to_ref(fetched_set["info"]))
        for item in fetched_set["data"]["items"]:
            self.assertNotIn("info", item)
            self.assertIn("ref", item)
            self.assertIn("label", item)

        fetched_set_with_info = self.getImpl().get_reads_alignment_set_v1(self.getContext(), {
            "ref": alignment_set_ref,
            "include_item_info": 1
        })[0]
        self.assertIsNotNone(fetched_set_with_info)
        self.assertIn("data", fetched_set_with_info)
        for item in fetched_set_with_info["data"]["items"]:
            self.assertIn("info", item)
            self.assertIn("ref", item)
            self.assertIn("label", item)
