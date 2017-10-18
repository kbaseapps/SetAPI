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

from biokbase.workspace.client import Workspace as workspaceService
from SetAPI.SetAPIImpl import SetAPI
from SetAPI.SetAPIServer import MethodContext
from SetAPI.generic.GenericSetNavigator import GenericSetNavigator

from DataPaletteService.DataPaletteServiceClient import DataPaletteService
from FakeObjectsForTests.FakeObjectsForTestsClient import FakeObjectsForTests
from SetAPI.authclient import KBaseAuth as _KBaseAuth

class SetAPITest(unittest.TestCase):
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
        cls.serviceWizardURL = cls.cfg['service-wizard']
        cls.dataPaletteServiceVersion = cls.cfg['datapaletteservice-version']

        # setup data at the class level for now (so that the code is run
        # once for all tests, not before each test case.  Not sure how to
        # do that outside this function..)
        suffix = int(time.time() * 1000)
        wsName = "test_SetAPI_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': wsName})
        cls.wsName = wsName

        foft = FakeObjectsForTests(os.environ['SDK_CALLBACK_URL'])
        [info1, info2] = foft.create_fake_reads({'ws_name': wsName, 
                                                 'obj_names': ['reads1', 'reads2']})
        cls.read1ref = str(info1[6]) + '/' + str(info1[0]) + '/' + str(info1[4])
        cls.read2ref = str(info2[6]) + '/' + str(info2[0]) + '/' + str(info2[4])

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

    def create_sets(self):
        if hasattr(self.__class__, 'setNames'):
            return

        workspace = self.getWsName()
        self.__class__.setNames = ['set_o_reads1', 'set_o_reads2', 'set_o_reads3']
        self.__class__.setRefs = []

        setAPI = self.getImpl()
        for s in self.setNames:

            set_data = {
                'description': 'my first reads',
                'items': [ {
                        'ref': self.read1ref,
                        'label':'reads1'
                    },{
                        'ref': self.read2ref,
                        'label':'reads2'
                    }
                ]
            }
            # test a save
            res = setAPI.save_reads_set_v1(self.getContext(), {
                    'data': set_data,
                    'output_object_name': s,
                    'workspace': workspace
                })[0]
            self.setRefs.append(res['set_ref'])

    # NOTE: According to Python unittest naming rules test method names should start from 'test'.
    def test_list_sets(self):

        workspace = self.getWsName()
        setAPI = self.getImpl()

        # make sure we can see an empty list of sets before WS has any
        res = setAPI.list_sets(self.getContext(), {
                'workspace': workspace,
                'include_set_item_info': 1
            })[0]
        self.assertEqual(len(res['sets']), 0)

        # create the test sets
        self.create_sets()

        res = setAPI.list_sets(self.getContext(), {
                'workspace': workspace,
                'include_set_item_info': 1
            })[0]
        self.assertTrue('sets' in res)
        self.assertEqual(len(res['sets']), len(self.setNames))
        for s in res['sets']:
            self.assertTrue('ref' in s)
            self.assertTrue('info' in s)
            self.assertTrue('items' in s)
            self.assertEqual(len(s['info']), 11)
            self.assertEqual(len(s['items']), 2)
            for item in s['items']:
                self.assertTrue('ref' in item)
                self.assertTrue('info' in item)
                self.assertEqual(len(item['info']), 11)

        res2 = setAPI.list_sets(self.getContext(), {
                'workspace':workspace
            })[0]
        self.assertTrue('sets' in res2)
        self.assertEqual(len(res2['sets']), len(self.setNames))
        for s in res2['sets']:
            self.assertTrue('ref' in s)
            self.assertTrue('info' in s)
            self.assertTrue('items' in s)
            self.assertEqual(len(s['info']), 11)
            self.assertEqual(len(s['items']), 2)
            for item in s['items']:
                self.assertTrue('ref' in item)
                self.assertTrue('info' not in item)

        res3 = setAPI.list_sets(self.getContext(), {
                    'workspace': workspace,
                    'include_set_item_ref_paths': 1
                })[0]

        if self.DEBUG:
            print('Result from list_items with ref_paths')
            pprint(res3)
            print('=====================================')

        self.assertTrue('sets' in res3)
        self.assertEqual(len(res3['sets']), len(self.setNames))
        for s in res3['sets']:
            self.assertTrue('ref' in s)
            self.assertTrue('info' in s)
            self.assertTrue('items' in s)
            self.assertEqual(len(s['info']), 11)
            self.assertEqual(len(s['items']), 2)
            for item in s['items']:
                self.assertTrue('ref' in item)
                self.assertTrue('info' not in item)
                self.assertTrue('ref_path' in item)
                self.assertEquals(item['ref_path'], s['ref'] + ';' + item['ref'])

        self.unit_test_get_set_items()

        set_obj_name = self.setNames[0]
        wsName2 = "test_SetAPI_" + str(int(time.time() * 1000)) + "_two"
        self.getWsClient().create_workspace({'workspace': wsName2})
        try:
            set_obj_ref = self.getWsName() + '/' + set_obj_name
            dps = DataPaletteService(self.serviceWizardURL, 
                                     token=self.getContext()['token'],
                                     service_ver=self.dataPaletteServiceVersion)
            dps.add_to_palette({'workspace': wsName2, 
                                'new_refs': [{'ref': set_obj_ref}]})
            ret = self.getImpl().list_sets(self.getContext(),
                                                {'workspace': wsName2, 
                                                 'include_set_item_info': 1,
                                                 'include_raw_data_palettes': 1})[0]
            set_list = ret['sets']
            self.assertEqual(1, len(set_list))
            set_info = set_list[0]
            info = set_info['info']
            self.assertEqual(self.getWsName(), info[7])
            self.assertEqual(set_obj_name, info[1])
            self.assertTrue('raw_data_palettes' in ret)
            self.assertEqual(1, len(ret['raw_data_palettes']))
            self.assertIn('info', ret['raw_data_palettes'][0])
            self.assertIn('ref', ret['raw_data_palettes'][0])
            self.assertTrue('raw_data_palette_refs' in ret)
            self.assertEqual(1, len(ret['raw_data_palette_refs']))
            
            set_list2 = self.getImpl().list_sets(self.getContext(),
                                                 {'workspaces': [workspace, wsName2], 
                                                  'include_set_item_info': 1,
                                                  'include_metadata': 1})[0]['sets']
            self.assertEqual(len(set_list2), len(self.setNames))
            self.assertTrue(len(set_list2) > 0)
            for set_obj in set_list2:
                self.assertIsNotNone(set_obj['info'][10])
                for item in set_obj['items']:
                    self.assertIsNotNone(item['info'][10])
        finally:
            self.getWsClient().delete_workspace({'workspace': wsName2})

    def test_bulk_list_sets(self):
        try:
            ids = []
            for ws_info in self.getWsClient().list_workspace_info({'perm': 'r', 'excludeGlobal': 1}):
                if ws_info[4] < 1000:
                    ids.append(str(ws_info[0]))
                else:
                    print("Workspace: " + ws_info[1] + ", size=" + str(ws_info[4]) + " (skipped)")
    
            print("Number of workspaces for bulk list_sets: " + str(len(ids)))
            if len(ids) > 0:
                ret = self.getImpl().list_sets(self.getContext(),
                                         {'workspaces': [ids[0]], 
                                          'include_set_item_info': 1})[0]
                self.assertTrue('raw_data_palettes' not in ret)
            GenericSetNavigator.DEBUG = True
            t1 = time.time()
            ret = self.getImpl().list_sets(self.getContext(),
                                           {'workspaces': ids, 
                                            'include_set_item_info': 1})[0]
            print("Objects found: " + str(len(ret['sets'])) + ", time=" + str(time.time() - t1))
        finally:
            GenericSetNavigator.DEBUG = False

    def unit_test_get_set_items(self):

        res = self.getImpl().get_set_items(self.getContext(), {
                                            'set_refs': [{'ref': self.setRefs[0]},
                                                         {'ref': self.setRefs[1]},
                                                         {'ref': self.setRefs[2]}],
                                            'include_set_item_ref_paths': 1
                                            })[0]
        if self.DEBUG:
            print('Result from get_set_items with ref_paths')
            pprint(res)
            print('========================================')

        self.assertEqual(len(res['sets']), 3)
        for s in res['sets']:
            self.assertTrue('ref' in s)
            self.assertTrue('info' in s)
            self.assertTrue('items' in s)
            self.assertEqual(len(s['info']), 11)
            self.assertEqual(len(s['items']), 2)
            for item in s['items']:
                self.assertTrue('ref' in item)
                self.assertTrue('info' in item)
                self.assertEqual(len(item['info']), 11)
                self.assertTrue('ref_path' in item)
                self.assertEquals(item["ref_path"], s["ref"] + ";" + item["ref"])