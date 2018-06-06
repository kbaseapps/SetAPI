# -*- coding: utf-8 -*-
import unittest
import os
import json
import time
import requests
import shutil

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint

from Workspace.WorkspaceClient import Workspace as workspaceService
from SetAPI.SetAPIImpl import SetAPI
from SetAPI.SetAPIServer import MethodContext

from FakeObjectsForTests.FakeObjectsForTestsClient import FakeObjectsForTests
from SetAPI.authclient import KBaseAuth as _KBaseAuth
from util import make_fake_sampleset
from DataFileUtil.DataFileUtilClient import DataFileUtil


class SetAPITest(unittest.TestCase):

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
        cls.dfu = DataFileUtil(os.environ['SDK_CALLBACK_URL'])

        # setup data at the class level for now (so that the code is run
        # once for all tests, not before each test case.  Not sure how to
        # do that outside this function..)
        suffix = int(time.time() * 1000)
        wsName = "test_SetAPI_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': wsName})
        cls.wsName = wsName

        foft = FakeObjectsForTests(os.environ['SDK_CALLBACK_URL'])
        [info1, info2, info3] = foft.create_fake_reads({'ws_name': wsName,
                                                        'obj_names': ['reads1', 'reads2',
                                                                      'reads3']})
        cls.read1ref = str(info1[6]) + '/' + str(info1[0]) + '/' + str(info1[4])
        cls.read2ref = str(info2[6]) + '/' + str(info2[0]) + '/' + str(info2[4])
        cls.read3ref = str(info3[6]) + '/' + str(info3[0]) + '/' + str(info3[4])

        cls.prepare_data()

    @classmethod
    def prepare_data(cls):
        # conditions
        cls.condition_1 = 'WT'
        cls.condition_2 = 'Cond1'

        # create a conditition set
        workspace_id = cls.dfu.ws_name_to_id(cls.wsName)
        condition_set_object_name = 'test_Condition_Set'
        condition_set_data = {
                            'conditions': {cls.condition_1: ['0', '0'],
                                           cls.condition_2: ['0', '0']},
                            'factors': [
                                        {
                                            "factor": "Time series design",
                                            "factor_ont_id": "Custom:Term",
                                            "factor_ont_ref": "KbaseOntologies/Custom",
                                            "unit": "Hour",
                                            "unit_ont_id": "Custom:Unit",
                                            "unit_ont_ref": "KbaseOntologies/Custom"
                                        },
                                        {
                                            "factor": "Treatment with Sirolimus",
                                            "factor_ont_id": "Custom:Term",
                                            "factor_ont_ref": "KbaseOntologies/Custom",
                                            "unit": "nanogram per milliliter",
                                            "unit_ont_id": "Custom:Unit",
                                            "unit_ont_ref": "KbaseOntologies/Custom"
                                        }
                                    ],
                            "ontology_mapping_method": "User Curation"}
        save_object_params = {
            'id': workspace_id,
            'objects': [{'type': 'KBaseExperiments.ConditionSet',
                         'data': condition_set_data,
                         'name': condition_set_object_name}]
        }

        dfu_oi = cls.dfu.save_objects(save_object_params)[0]
        cls.condition_set_ref = str(dfu_oi[6]) + '/' + str(dfu_oi[0]) + '/' + str(dfu_oi[4])

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

    # NOTE: According to Python unittest naming rules test method names should start from 'test'.
    def test_basic_save_and_get(self):

        workspace = self.getWsName()
        setObjName = 'micromonas_rnaseq_test1_sampleset'

        # create the set object
        create_ss_params = {
                "ws_id": workspace,
                "sampleset_id": setObjName,
                "sampleset_desc": "first pass at testing algae GFFs from NCBI",
                "domain": "euk",
                "platform": "Illumina",
                "sample_n_conditions": [
                    {"sample_id": [self.read1ref], "condition": self.condition_1},
                    {"sample_id": [self.read2ref, self.read3ref], "condition": self.condition_2},
                ],
                "source": "NCBI",
                "Library_type": "SingleEnd",
                "publication_id": "none",
                "string external_source_date": "not sure",
                "conditionset_ref":  self.condition_set_ref
               }

        # test a save
        setAPI = self.getImpl()
        res = setAPI.create_sample_set(self.getContext(), create_ss_params)[0]

        print('======  Returned val from create_sample_set  ======')
        pprint(res)

        self.assertTrue('set_ref' in res)
        self.assertTrue('set_info' in res)
        self.assertEqual(len(res['set_info']), 11)

        self.assertEqual(res['set_info'][1], setObjName)
        self.assertTrue('num_samples' in res['set_info'][10])
        self.assertEqual(res['set_info'][10]['num_samples'], '3')

        # test get of that object
        d1 = setAPI.get_reads_set_v1(self.getContext(), {
                'ref': workspace + '/' + setObjName
            })[0]
        self.assertTrue('data' in d1)
        self.assertTrue('info' in d1)
        self.assertEqual(len(d1['info']), 11)
        self.assertTrue('item_count' in d1['info'][10])
        self.assertEqual(d1['info'][10]['item_count'], 3)

        self.assertEqual(d1['data']['description'], 'first pass at testing algae GFFs from NCBI')
        self.assertEqual(len(d1['data']['items']), 3)

        item2 = d1['data']['items'][1]
        self.assertTrue('info' not in item2)
        self.assertTrue('ref' in item2)
        self.assertTrue('label' in item2)
        self.assertEqual(item2['label'], self.condition_2)
        self.assertEqual(item2['ref'], self.read2ref)

        item3 = d1['data']['items'][2]
        self.assertTrue('info' not in item3)
        self.assertTrue('ref' in item3)
        self.assertTrue('label' in item3)
        self.assertEqual(item3['label'], self.condition_2)
        self.assertEqual(item3['ref'], self.read3ref)

        # test the call to make sure we get info for each item
        d2 = setAPI.get_reads_set_v1(self.getContext(), {
                'ref': res['set_ref'],
                'include_item_info': 1,
                'include_set_item_ref_paths': 1
            })[0]
        self.assertTrue('data' in d2)
        self.assertTrue('info' in d2)
        self.assertEqual(len(d2['info']), 11)
        self.assertTrue('item_count' in d2['info'][10])
        self.assertEqual(d2['info'][10]['item_count'], 3)

        self.assertEqual(d2['data']['description'], 'first pass at testing algae GFFs from NCBI')
        self.assertEqual(len(d2['data']['items']), 3)

        item2 = d2['data']['items'][1]
        self.assertTrue('info' in item2)
        self.assertTrue(len(item2['info']), 11)
        self.assertTrue('ref' in item2)
        self.assertEqual(item2['ref'],self.read2ref)

        self.assertTrue('ref_path' in item2)
        self.assertEqual(item2['ref_path'], res['set_ref'] + ';' + item2['ref'])

        pprint(d2)

    def test_unmatched_conditions(self):

        workspace = self.getWsName()
        setObjName = 'micromonas_rnaseq_test1_sampleset'

        unmatching_condition = 'unmatching_condition'
        # create the set object
        create_ss_params = {
                "ws_id": workspace,
                "sampleset_id": setObjName,
                "sampleset_desc": "first pass at testing algae GFFs from NCBI",
                "domain": "euk",
                "platform": "Illumina",
                "sample_n_conditions": [
                    {"sample_id": [self.read1ref], "condition": unmatching_condition},
                    {"sample_id": [self.read2ref, self.read3ref], "condition": self.condition_2},
                ],
                "source": "NCBI",
                "Library_type": "SingleEnd",
                "publication_id": "none",
                "string external_source_date": "not sure",
                "conditionset_ref":  self.condition_set_ref
               }

        # test a save
        setAPI = self.getImpl()

        with self.assertRaisesRegexp(
                ValueError, 'ERROR: Given conditoins'):
            setAPI.create_sample_set(self.getContext(), create_ss_params)
