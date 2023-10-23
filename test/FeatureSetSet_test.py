# -*- coding: utf-8 -*-
import os
import time
import unittest
from test.test_config import get_test_config
from os import environ

from SetAPI.SetAPIImpl import SetAPI
from SetAPI.SetAPIServer import MethodContext
from installed_clients.authclient import KBaseAuth
from installed_clients.FakeObjectsForTestsClient import FakeObjectsForTests
from installed_clients.WorkspaceClient import Workspace as workspaceService
from test.util import (
    info_to_ref,
    make_fake_feature_set
)


class FeatureSetSetAPITest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        attributes = get_test_config()
        for attr in ['cfg', 'ctx', 'serviceImpl', 'wsClient', 'wsName', 'wsURL']:
            setattr(cls, attr, attributes[attr])

        foft = FakeObjectsForTests(os.environ['SDK_CALLBACK_URL'])

        # Make fake genomes
        [fake_genome, fake_genome2] = foft.create_fake_genomes({
            "ws_name": cls.wsName,
            "obj_names": ["fake_genome", "fake_genome2"]
        })
        cls.genome_refs = [info_to_ref(fake_genome), info_to_ref(fake_genome2)]

        # Make some fake feature sets
        cls.featureset_refs = [make_fake_feature_set(
            "feature_set_{}".format(i),
            cls.genome_refs[0],
            cls.wsName,
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
        set_name = "test_feature_set_set"
        set_items = list()
        for ref in self.featureset_refs:
            set_items.append({
                "label": "foo",
                "ref": ref
            })
        expression_set = {
            "description": "test_expressions",
            "items": set_items
        }
        result = self.getImpl().save_feature_set_set_v1(self.getContext(), {
            "workspace": self.getWsName(),
            "output_object_name": set_name,
            "data": expression_set
        })[0]
        self.assertIsNotNone(result)
        self.assertIn("set_ref", result)
        self.assertIn("set_info", result)
        self.assertEqual(result["set_ref"], info_to_ref(result["set_info"]))
        self.assertEqual(result["set_info"][1], set_name)
        self.assertIn("KBaseSets.FeatureSetSet", result["set_info"][2])

    def test_save_feature_set_set_no_data(self):
        with self.assertRaises(ValueError) as err:
            self.getImpl().save_feature_set_set_v1(self.getContext(), {
                "workspace": self.getWsName(),
                "output_object_name": "foo",
                "data": None
            })
        self.assertIn('"data" parameter field required to save a FeatureSetSet',
                      str(err.exception))

    @unittest.skip("Currently allow empty FeatureSetSets")
    def test_save_feature_set_set_empty(self):
        with self.assertRaises(ValueError) as err:
            self.getImpl().save_feature_set_set_v1(self.getContext(), {
                "workspace": self.getWsName(),
                "output_object_name": "foo",
                "data": {
                    "description": "empty_set",
                    "items": []
                }
            })
        self.assertIn("At least one FeatureSet is required to save a FeatureSetSet.",
                      str(err.exception))

    def test_get_feature_set_set(self):
        set_name = "test_featureset_set2"
        set_items = list()
        for ref in self.featureset_refs:
            set_items.append({
                "label": "wt",
                "ref": ref
            })
        featureset_set = {
            "description": "test_alignments",
            "items": set_items
        }
        featureset_set_ref = self.getImpl().save_feature_set_set_v1(self.getContext(), {
            "workspace": self.getWsName(),
            "output_object_name": set_name,
            "data": featureset_set
        })[0]["set_ref"]

        fetched_set = self.getImpl().get_feature_set_set_v1(self.getContext(), {
            "ref": featureset_set_ref,
            "include_item_info": 0
        })[0]
        self.assertIsNotNone(fetched_set)
        self.assertIn("data", fetched_set)
        self.assertIn("info", fetched_set)
        self.assertEqual(len(fetched_set["data"]["items"]), 3)
        self.assertEqual(featureset_set_ref, info_to_ref(fetched_set["info"]))
        for item in fetched_set["data"]["items"]:
            self.assertNotIn("info", item)
            self.assertNotIn("ref_path", item)
            self.assertIn("ref", item)
            self.assertIn("label", item)

        fetched_set_with_info = self.getImpl().get_feature_set_set_v1(self.getContext(), {
            "ref": featureset_set_ref,
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
            self.assertEqual(item["ref_path"], featureset_set_ref + ";" + item["ref"])

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
