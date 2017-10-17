# -*- coding: utf-8 -*-
import unittest
import os
import time
from pprint import pprint

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
    make_fake_alignment,
    make_fake_annotation,
    make_fake_expression,
    make_fake_sampleset,
    make_fake_old_alignment_set,
    make_fake_old_expression_set
)
import shutil

class ExpressionSetAPITest(unittest.TestCase):
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
        dummy_filename = "dummy.txt"
        cls.dummy_path = os.path.join(cls.cfg['scratch'], dummy_filename)
        shutil.copy(os.path.join("data", dummy_filename), cls.dummy_path)

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
                    wsName,
                    cls.wsClient)
            )

        # Need a fake annotation to get the expression objects
        cls.annotation_ref = make_fake_annotation(
            os.environ['SDK_CALLBACK_URL'],
            cls.dummy_path,
            "fake_annotation",
            wsName,
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
                wsName,
                cls.wsClient
            ))

        # Make a fake RNASeq Alignment Set object
        # Make a fake RNASeqSampleSet
        cls.sampleset_ref = make_fake_sampleset("fake_sampleset", [], [], wsName, cls.wsClient)

        # Finally, make a couple fake RNASeqAlignmentSts objects from those alignments
        cls.fake_rnaseq_alignment_set = make_fake_old_alignment_set(
            "fake_rnaseq_alignment_set",
            cls.reads_refs,
            cls.genome_refs[0],
            cls.sampleset_ref,
            cls.alignment_refs,
            wsName,
            cls.wsClient)

        # Make a fake RNASeq Expression Set object
        cls.fake_rnaseq_expression_set = make_fake_old_expression_set(
                                                    "fake_rnaseq_expression_set",
                                                    cls.genome_refs[0],
                                                    cls.sampleset_ref,
                                                    cls.alignment_refs,
                                                    cls.fake_rnaseq_alignment_set,
                                                    cls.expression_refs,
                                                    wsName,
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

    def test_save_expression_set(self):
        expression_set_name = "test_expression_set"
        expression_items = list()
        for ref in self.expression_refs:
            expression_items.append({
                "label": "foo",
                "ref": ref
            })
        expression_set = {
            "description": "test_expressions",
            "items": expression_items
        }
        result = self.getImpl().save_expression_set_v1(self.getContext(), {
            "workspace": self.getWsName(),
            "output_object_name": expression_set_name,
            "data": expression_set
        })[0]
        self.assertIsNotNone(result)
        self.assertIn("set_ref", result)
        self.assertIn("set_info", result)
        self.assertEqual(result["set_ref"], info_to_ref(result["set_info"]))
        self.assertEqual(result["set_info"][1], expression_set_name)
        self.assertIn("KBaseSets.ExpressionSet", result["set_info"][2])

    def test_save_expression_set_mismatched_genomes(self):
        expression_set_name = "expression_set_bad_genomes"
        expression_set = {
            "description": "this_better_fail",
            "items": [{
                "ref": make_fake_expression(
                    os.environ['SDK_CALLBACK_URL'],
                    self.dummy_path,
                    "odd_expression",
                    self.genome_refs[1],
                    self.annotation_ref,
                    self.alignment_refs[0],
                    self.getWsName(),
                    self.getWsClient()
                ),
                "label": "odd_alignment"
            }, {
                "ref": self.alignment_refs[1],
                "label": "not_so_odd"
            }]
        }
        with self.assertRaises(ValueError) as err:
            self.getImpl().save_expression_set_v1(self.getContext(), {
                "workspace": self.getWsName(),
                "output_object_name": expression_set_name,
                "data": expression_set
            })
            self.assertIn("All Expression objects in the set must use "
                          "the same genome reference.", str(err.exception))

    def test_save_expression_set_no_data(self):
        with self.assertRaises(ValueError) as err:
            self.getImpl().save_expression_set_v1(self.getContext(), {
                "workspace": self.getWsName(),
                "output_object_name": "foo",
                "data": None
            })
        self.assertIn('"data" parameter field required to save an ExpressionSet',
                      str(err.exception))

    def test_save_expression_set_no_expressions(self):
        with self.assertRaises(ValueError) as err:
            self.getImpl().save_expression_set_v1(self.getContext(), {
                "workspace": self.getWsName(),
                "output_object_name": "foo",
                "data": {
                    "items": []
                }
            })
        self.assertIn("An ExpressionSet must contain at "
                      "least one Expression object reference.", str(err.exception))

    def test_get_expression_set(self):
        expression_set_name = "test_expression_set"
        expression_items = list()
        for ref in self.expression_refs:
            expression_items.append({
                "label": "wt",
                "ref": ref
            })
        expression_set = {
            "description": "test_alignments",
            "items": expression_items
        }
        expression_set_ref = self.getImpl().save_expression_set_v1(self.getContext(), {
            "workspace": self.getWsName(),
            "output_object_name": expression_set_name,
            "data": expression_set
        })[0]["set_ref"]

        fetched_set = self.getImpl().get_expression_set_v1(self.getContext(), {
            "ref": expression_set_ref,
            "include_item_info": 0
        })[0]
        self.assertIsNotNone(fetched_set)
        self.assertIn("data", fetched_set)
        self.assertIn("info", fetched_set)
        self.assertEquals(len(fetched_set["data"]["items"]), 3)
        self.assertEquals(expression_set_ref, info_to_ref(fetched_set["info"]))
        for item in fetched_set["data"]["items"]:
            self.assertNotIn("info", item)
            self.assertNotIn("ref_path", item)
            self.assertIn("ref", item)
            self.assertIn("label", item)

        fetched_set_with_info = self.getImpl().get_expression_set_v1(self.getContext(), {
            "ref": expression_set_ref,
            "include_item_info": 1
        })[0]
        self.assertIsNotNone(fetched_set_with_info)
        self.assertIn("data", fetched_set_with_info)
        for item in fetched_set_with_info["data"]["items"]:
            self.assertIn("info", item)
            self.assertIn("ref", item)
            self.assertIn("label", item)
            self.assertNotIn("ref_path", item)

    def test_get_expression_set_ref_path(self):
        expression_set_name = "test_expression_set_ref_path"
        expression_items = list()
        for ref in self.expression_refs:
            expression_items.append({
                "label": "wt",
                "ref": ref
            })
        expression_set = {
            "description": "test_alignments",
            "items": expression_items
        }
        expression_set_ref = self.getImpl().save_expression_set_v1(self.getContext(), {
            "workspace": self.getWsName(),
            "output_object_name": expression_set_name,
            "data": expression_set
        })[0]["set_ref"]

        fetched_set_with_info = self.getImpl().get_expression_set_v1(self.getContext(), {
            "ref": expression_set_ref,
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
            self.assertEquals(item["ref_path"], expression_set_ref + ";" + item["ref"])

    # NOTE: Comment the following line to run the test
    @unittest.skip("skipped test_get_expression_set_ref_path")
    def test_get_narrative_expression_set_ref_path(self):

        appdev_kbasesets_expression_set_ref = '5264/38/2'

        fetched_set_with_ref_path = self.getImpl().get_expression_set_v1(self.getContext(), {
            "ref": appdev_kbasesets_expression_set_ref,
            "include_item_info": 0,
            "include_set_item_ref_paths": 1
        })[0]

        for item in fetched_set_with_ref_path["data"]["items"]:
            self.assertIn("ref", item)
            self.assertIn("label", item)
            self.assertIn("ref_path", item)
            self.assertEquals(item["ref_path"],
                              appdev_kbasesets_expression_set_ref + ";" + item["ref"])

        print("INPUT: Appdev KBasesets.ExpressionSet: " + appdev_kbasesets_expression_set_ref)
        pprint(fetched_set_with_ref_path)
        print("==========================")

        appdev_rnaseq_expression_set_ref = '4389/45/1'

        fetched_set_with_ref_path = self.getImpl().get_expression_set_v1(self.getContext(), {
            "ref": appdev_rnaseq_expression_set_ref,
            "include_item_info": 0,
            "include_set_item_ref_paths": 1
        })[0]

        print("=============  FETCHED SET RNASEQ  ===============")
        pprint(fetched_set_with_ref_path)
        print("============  END FETCHED SET RNASEQ  ============")

    def test_get_created_rnaseq_expression_set_ref_path(self):

        created_expression_set_ref = self.fake_rnaseq_expression_set

        fetched_set_with_ref_path = self.getImpl().get_expression_set_v1(self.getContext(), {
            "ref": created_expression_set_ref,
            "include_item_info": 0,
            "include_set_item_ref_paths": 1
        })[0]

        for item in fetched_set_with_ref_path["data"]["items"]:
            self.assertIn("ref", item)
            self.assertIn("label", item)
            self.assertIn("ref_path", item)
            self.assertEquals(item["ref_path"],
                              created_expression_set_ref + ";" + item["ref"])

        print("INPUT: CREATED KBasesets.ExpressionSet: " + created_expression_set_ref)
        pprint(fetched_set_with_ref_path)
        print("==========================")

    def test_get_expression_set_bad_ref(self):
        with self.assertRaises(ValueError) as err:
            self.getImpl().get_expression_set_v1(self.getContext(), {
                "ref": "not_a_ref"
            })
        self.assertIn('"ref" parameter must be a valid workspace reference', str(err.exception))

    def test_get_expression_set_bad_path(self):
        with self.assertRaises(Exception):
            self.getImpl().get_expression_set_v1(self.getContext(), {
                "ref": "1/2/3",
                "path_to_set": ["foo", "bar"]
            })

    def test_get_expression_set_no_ref(self):
        with self.assertRaises(ValueError) as err:
            self.getImpl().get_expression_set_v1(self.getContext(), {
                "ref": None
            })
        self.assertIn('"ref" parameter field specifiying the expression set is required',
                      str(err.exception))

