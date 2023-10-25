# -*- coding: utf-8 -*-
import os
import shutil
import time
import unittest
from configparser import ConfigParser
from os import environ
from pprint import pprint

from test import TEST_BASE_DIR
from SetAPI.SetAPIImpl import SetAPI
from SetAPI.SetAPIServer import MethodContext
from installed_clients.authclient import KBaseAuth
from installed_clients.FakeObjectsForTestsClient import FakeObjectsForTests
from installed_clients.WorkspaceClient import Workspace as workspaceService
from test import TEST_BASE_DIR
from test.util import (
    info_to_ref,
    make_fake_alignment,
    make_fake_sampleset,
    make_fake_annotation,
    make_fake_expression,
    make_fake_old_alignment_set,
    make_fake_old_expression_set
)


class ReadsAlignmentSetAPITest(unittest.TestCase):
    DEBUG = False

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
        auth_client = KBaseAuth(authServiceUrl)
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
            "ws_name": cls.wsName,
            "obj_names": ["fake_genome", "fake_genome2"]
        })
        cls.genome_refs = [info_to_ref(fake_genome), info_to_ref(fake_genome2)]

        # Make some fake reads objects
        fake_reads_list = foft.create_fake_reads({
            'ws_name': cls.wsName,
            "obj_names": ["reads1", "reads2", "reads3"]
        })
        cls.alignment_refs = []
        cls.reads_refs = []

        dummy_filename = "dummy.txt"
        cls.dummy_path = os.path.join(cls.cfg['scratch'], dummy_filename)
        shutil.copy(os.path.join(TEST_BASE_DIR, "data", dummy_filename), cls.dummy_path)

        # Make some fake alignments referencing those reads and genome
        for idx, reads_info in enumerate(fake_reads_list):
            reads_ref = info_to_ref(reads_info)
            cls.reads_refs.append(reads_ref)
            cls.alignment_refs.append(
                make_fake_alignment(
                    os.environ['SDK_CALLBACK_URL'],
                    cls.dummy_path,
                    "fake_alignment_{}".format(idx),
                    reads_ref,
                    cls.genome_refs[0],
                    cls.wsName, cls.wsClient
                )
            )

        # Make a fake RNASeqSampleSet
        cls.sampleset_ref = make_fake_sampleset("fake_sampleset", [], [], cls.wsName, cls.wsClient)

        # Finally, make a couple fake RNASeqAlignmentSts objects from those alignments
        cls.fake_rnaseq_alignment_set1 = make_fake_old_alignment_set(
            "fake_rnaseq_alignment_set1",
            cls.reads_refs,
            cls.genome_refs[0],
            cls.sampleset_ref,
            cls.alignment_refs,
            cls.wsName,
            cls.wsClient)
        cls.fake_rnaseq_alignment_set2 = make_fake_old_alignment_set(
            "fake_rnaseq_alignment_set2",
            cls.reads_refs,
            cls.genome_refs[0],
            cls.sampleset_ref,
            cls.alignment_refs,
            cls.wsName,
            cls.wsClient,
            include_sample_alignments=True
        )

        # Need a fake annotation to get the expression objects
        cls.annotation_ref = make_fake_annotation(
            os.environ['SDK_CALLBACK_URL'],
            cls.dummy_path,
            "fake_annotation",
            cls.wsName,
            cls.wsClient)

        # Now we can phony up some expression objects to build sets out of.
        # name, genome_ref, annotation_ref, alignment_ref, ws_name, ws_client
        cls.expression_refs = list()
        for idx, alignment_ref in enumerate(cls.alignment_refs):
            cls.expression_refs.append(make_fake_expression(
                os.environ['SDK_CALLBACK_URL'],
                cls.dummy_path,
                "fake_expression_{}".format(idx),
                cls.genome_refs[0],
                cls.annotation_ref,
                alignment_ref,
                cls.wsName,
                cls.wsClient
            ))

        # Make a fake RNASeq Expression Set object
        cls.fake_rnaseq_expression_set = make_fake_old_expression_set(
            "fake_rnaseq_expression_set",
            cls.genome_refs[0],
            cls.sampleset_ref,
            cls.alignment_refs,
            cls.fake_rnaseq_alignment_set1,
            cls.expression_refs,
            cls.wsName,
            cls.wsClient,
            True)

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
                "ref": make_fake_alignment(
                    os.environ['SDK_CALLBACK_URL'],
                    self.dummy_path,
                    "odd_alignment",
                    self.reads_refs[0], self.genome_refs[1],
                    self.getWsName(), self.getWsClient()
                ),
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
            self.assertIn("All ReadsAlignments in the set must be aligned against "
                          "the same genome reference", str(err.exception))

    def test_save_alignment_set_no_data(self):
        with self.assertRaises(ValueError) as err:
            self.getImpl().save_reads_alignment_set_v1(self.getContext(), {
                "workspace": self.getWsName(),
                "output_object_name": "foo",
                "data": None
            })
        self.assertIn('"data" parameter field required to save a ReadsAlignmentSet',
                      str(err.exception))

    def test_save_alignment_set_no_alignments(self):
        with self.assertRaises(ValueError) as err:
            self.getImpl().save_reads_alignment_set_v1(self.getContext(), {
                "workspace": self.getWsName(),
                "output_object_name": "foo",
                "data": {
                    "items": []
                }
            })
        self.assertIn("A ReadsAlignmentSet must contain at "
                      "least one ReadsAlignment reference.", str(err.exception))

    def test_get_old_alignment_set(self):
        for ref in [self.fake_rnaseq_alignment_set1, self.fake_rnaseq_alignment_set2]:
            fetched_set = self.getImpl().get_reads_alignment_set_v1(self.getContext(), {
                "ref": ref,
                "include_item_info": 0
            })[0]
            self.assertIsNotNone(fetched_set)
            self.assertIn("data", fetched_set)
            self.assertIn("info", fetched_set)
            self.assertEqual(len(fetched_set["data"]["items"]), 3)
            self.assertEqual(ref, info_to_ref(fetched_set["info"]))
            for item in fetched_set["data"]["items"]:
                self.assertNotIn("info", item)
                self.assertIn("ref", item)
                self.assertIn("label", item)

            fetched_set_with_info = self.getImpl().get_reads_alignment_set_v1(self.getContext(), {
                "ref": ref,
                "include_item_info": 1,
                "include_set_item_ref_paths": 1
            })[0]
            self.assertIsNotNone(fetched_set_with_info)
            self.assertIn("data", fetched_set_with_info)
            for item in fetched_set_with_info["data"]["items"]:
                self.assertIn("info", item)
                self.assertIn("ref", item)
                self.assertIn("label", item)
                self.assertIn("ref_path", item)
                self.assertEqual(item["ref_path"], ref + ";" + item["ref"])

    def test_get_old_alignment_set_ref_path_to_set(self):
        alignment_ref = self.fake_rnaseq_alignment_set1
        ref_path_to_set = [self.fake_rnaseq_expression_set, alignment_ref]

        fetched_set = self.getImpl().get_reads_alignment_set_v1(self.getContext(), {
            "ref": alignment_ref,
            "ref_path_to_set": ref_path_to_set,
            "include_item_info": 0,
            "include_set_item_ref_paths": 1
        })[0]
        self.assertIsNotNone(fetched_set)
        self.assertIn("data", fetched_set)
        self.assertIn("info", fetched_set)
        self.assertEqual(len(fetched_set["data"]["items"]), 3)
        self.assertEqual(alignment_ref, info_to_ref(fetched_set["info"]))
        for item in fetched_set["data"]["items"]:
            self.assertNotIn("info", item)
            self.assertIn("ref", item)
            self.assertIn("label", item)
            self.assertIn("ref_path", item)
            self.assertEqual(item["ref_path"], ";".join(ref_path_to_set) + ";" + item["ref"])

        if self.DEBUG:
            print('======  RNASeq Alignment with ref_path_to_set ========')
            pprint(fetched_set)
            print('======================================================')

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
        self.assertEqual(len(fetched_set["data"]["items"]), 3)
        self.assertEqual(alignment_set_ref, info_to_ref(fetched_set["info"]))
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

    def test_get_alignment_set_ref_path(self):
        alignment_set_name = "test_alignment_set_ref_path"
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
            "include_item_info": 0,
            "include_set_item_ref_paths": 1
        })[0]
        self.assertIsNotNone(fetched_set)
        self.assertIn("data", fetched_set)
        self.assertIn("info", fetched_set)
        self.assertEqual(len(fetched_set["data"]["items"]), 3)
        self.assertEqual(alignment_set_ref, info_to_ref(fetched_set["info"]))
        for item in fetched_set["data"]["items"]:
            self.assertNotIn("info", item)
            self.assertIn("ref", item)
            self.assertIn("label", item)
            self.assertIn("ref_path", item)
            self.assertEqual(item["ref_path"], alignment_set_ref + ";" + item["ref"])

    def test_get_alignment_set_bad_ref(self):
        with self.assertRaises(ValueError) as err:
            self.getImpl().get_reads_alignment_set_v1(self.getContext(), {
                "ref": "not_a_ref"
            })
        self.assertIn('"ref" parameter must be a valid workspace reference', str(err.exception))

    def test_get_alignment_set_bad_path(self):
        with self.assertRaises(Exception):
            self.getImpl().get_reads_alignment_set_v1(self.getContext(), {
                "ref": "1/2/3",
                "path_to_set": ["foo", "bar"]
            })

    def test_get_alignment_set_no_ref(self):
        with self.assertRaises(ValueError) as err:
            self.getImpl().get_reads_alignment_set_v1(self.getContext(), {
                "ref": None
            })
        self.assertIn('"ref" parameter field specifiying the reads alignment set is required',
                      str(err.exception))
