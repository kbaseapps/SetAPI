# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser
from os import environ
from pprint import pprint

from SetAPI.SetAPIImpl import SetAPI
from SetAPI.SetAPIServer import MethodContext
from installed_clients.authclient import KBaseAuth
from installed_clients.FakeObjectsForTestsClient import FakeObjectsForTests
from installed_clients.WorkspaceClient import Workspace as workspaceService
from test.util import make_fake_sampleset


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
        ret = cls.wsClient.create_workspace({'workspace': wsName})
        cls.wsName = wsName

        foft = FakeObjectsForTests(os.environ['SDK_CALLBACK_URL'])
        [info1, info2, info3] = foft.create_fake_reads({'ws_name': cls.wsName,
                                                        'obj_names': ['reads1', 'reads2',
                                                                      'reads3']})
        cls.read1ref = str(info1[6]) + '/' + str(info1[0]) + '/' + str(info1[4])
        cls.read2ref = str(info2[6]) + '/' + str(info2[0]) + '/' + str(info2[4])
        cls.read3ref = str(info3[6]) + '/' + str(info3[0]) + '/' + str(info3[4])

        cls.fake_sampleset_ref = make_fake_sampleset(
            "test_sampleset",
            [cls.read1ref, cls.read2ref, cls.read3ref],
            ['wt', 'cond1', 'cond2'],
            cls.wsName,
            cls.wsClient
        )

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
        setObjName = 'set_o_reads'

        # create the set object
        set_data = {
            'description':'my first reads',
            'items': [ {
                    'ref': self.read1ref,
                    'label':'reads1'
                },{
                    'ref': self.read2ref,
                    'label':'reads2'
                }, {
                    'ref': self.read3ref
                }
            ]
        }

        # test a save
        setAPI = self.getImpl()
        res = setAPI.save_reads_set_v1(self.getContext(), {
                'data':set_data,
                'output_object_name':setObjName,
                'workspace': workspace
            })[0]
        self.assertTrue('set_ref' in res)
        self.assertTrue('set_info' in res)
        self.assertEqual(len(res['set_info']), 11)

        self.assertEqual(res['set_info'][1], setObjName)
        self.assertTrue('item_count' in res['set_info'][10])
        self.assertEqual(res['set_info'][10]['item_count'], '3')


        # test get of that object
        d1 = setAPI.get_reads_set_v1(self.getContext(), {
                'ref': workspace + '/' + setObjName
            })[0]
        self.assertTrue('data' in d1)
        self.assertTrue('info' in d1)
        self.assertEqual(len(d1['info']), 11)
        self.assertTrue('item_count' in d1['info'][10])
        self.assertEqual(d1['info'][10]['item_count'], '3')

        self.assertEqual(d1['data']['description'], 'my first reads')
        self.assertEqual(len(d1['data']['items']), 3)

        item2 = d1['data']['items'][1]
        self.assertTrue('info' not in item2)
        self.assertTrue('ref' in item2)
        self.assertTrue('label' in item2)
        self.assertEqual(item2['label'],'reads2')
        self.assertEqual(item2['ref'],self.read2ref)

        item3 = d1['data']['items'][2]
        self.assertTrue('info' not in item3)
        self.assertTrue('ref' in item3)
        self.assertTrue('label' in item3)
        self.assertEqual(item3['label'],'')
        self.assertEqual(item3['ref'],self.read3ref)

        # test the call to make sure we get info for each item
        d2 = setAPI.get_reads_set_v1(self.getContext(), {
                'ref':res['set_ref'],
                'include_item_info':1,
                'include_set_item_ref_paths': 1
            })[0]
        self.assertTrue('data' in d2)
        self.assertTrue('info' in d2)
        self.assertEqual(len(d2['info']), 11)
        self.assertTrue('item_count' in d2['info'][10])
        self.assertEqual(d2['info'][10]['item_count'], '3')

        self.assertEqual(d2['data']['description'], 'my first reads')
        self.assertEqual(len(d2['data']['items']), 3)

        item2 = d2['data']['items'][1]
        self.assertTrue('info' in item2)
        self.assertTrue(len(item2['info']), 11)
        self.assertTrue('ref' in item2)
        self.assertEqual(item2['ref'],self.read2ref)

        self.assertTrue('ref_path' in item2)
        self.assertEqual(item2['ref_path'], res['set_ref'] + ';' + item2['ref'])
        pprint(d2)

    # NOTE: Comment the following line to run the test
    @unittest.skip("skipped test_save_and_get_of_emtpy_set")
    def test_save_and_get_of_empty_set(self):

        workspace = self.getWsName()
        setObjName = 'nada_set'

        # create the set object
        set_data = {
            'description':'nothing to see here',
            'items': [
            ]
        }

        # test a save
        setAPI = self.getImpl()
        res = setAPI.save_reads_set_v1(self.getContext(), {
                'data':set_data,
                'output_object_name':setObjName,
                'workspace': workspace
            })[0]
        self.assertTrue('set_ref' in res)
        self.assertTrue('set_info' in res)
        self.assertEqual(len(res['set_info']), 11)

        self.assertEqual(res['set_info'][1], setObjName)
        self.assertTrue('item_count' in res['set_info'][10])
        self.assertEqual(res['set_info'][10]['item_count'], '0')


        # test get of that object
        d1 = setAPI.get_reads_set_v1(self.getContext(), {
                'ref': workspace + '/' + setObjName
            })[0]
        self.assertTrue('data' in d1)
        self.assertTrue('info' in d1)
        self.assertEqual(len(d1['info']), 11)
        self.assertTrue('item_count' in d1['info'][10])
        self.assertEqual(d1['info'][10]['item_count'], '0')

        self.assertEqual(d1['data']['description'], 'nothing to see here')
        self.assertEqual(len(d1['data']['items']), 0)

        d2 = setAPI.get_reads_set_v1(self.getContext(), {
                'ref':res['set_ref'],
                'include_item_info':1
            })[0]

        self.assertTrue('data' in d2)
        self.assertTrue('info' in d2)
        self.assertEqual(len(d2['info']), 11)
        self.assertTrue('item_count' in d2['info'][10])
        self.assertEqual(d2['info'][10]['item_count'], '0')

        self.assertEqual(d2['data']['description'], 'nothing to see here')
        self.assertEqual(len(d2['data']['items']), 0)

    def test_get_sampleset_as_readsset(self):
        param_set = [{
            "ref": self.fake_sampleset_ref
        }, {
            "ref": self.fake_sampleset_ref,
            "include_item_info": 0
        }, {
            "ref": self.fake_sampleset_ref,
            "include_item_info": 1
        }]
        for params in param_set:
            res = self.getImpl().get_reads_set_v1(self.getContext(), params)[0]
            self.assertIn('data', res)
            self.assertIn('items', res['data'])
            self.assertIn('info', res)
            self.assertEqual(len(res['info']), 11)
            self.assertIn('item_count', res['info'][10])
            self.assertEqual(res['info'][10]['item_count'], 3)
            for item in res['data']['items']:
                self.assertIn('ref', item)
                if params.get("include_item_info", 0) == 1:
                    self.assertIn('info', item)
                    self.assertEqual(len(item['info']), 11)
                else:
                    self.assertNotIn('info', item)

    def test_get_reads_set_bad_ref(self):
        with self.assertRaises(ValueError) as err:
            self.getImpl().get_reads_set_v1(self.getContext(), {'ref': 'not_a_ref'})
        self.assertEqual('"ref" parameter must be a valid workspace reference', str(err.exception))

    def test_get_reads_set_bad_type(self):
        with self.assertRaises(ValueError) as err:
            self.getImpl().get_reads_set_v1(self.getContext(), {'ref': self.read1ref})
        self.assertIn('is invalid for get_reads_set_v1', str(err.exception))
