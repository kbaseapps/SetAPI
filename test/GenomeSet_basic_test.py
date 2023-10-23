# -*- coding: utf-8 -*-
import os
import time
import unittest
from test.test_config import get_test_config
from os import environ
from pprint import pprint

from SetAPI.SetAPIImpl import SetAPI
from SetAPI.SetAPIServer import MethodContext
from installed_clients.authclient import KBaseAuth
from installed_clients.FakeObjectsForTestsClient import FakeObjectsForTests
from installed_clients.WorkspaceClient import Workspace as workspaceService


class SetAPITest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        cls.cfg = get_test_config()
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
        [info1, info2] = foft.create_fake_genomes({'ws_name': wsName,
                                                   'obj_names': ['genome_obj_1',
                                                                 'genome_obj_2']})
        cls.genome1ref = str(info1[6]) + '/' + str(info1[0]) + '/' + str(info1[4])
        cls.genome2ref = str(info2[6]) + '/' + str(info2[0]) + '/' + str(info2[4])


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
        setObjName = 'set_of_genomes'

        # create the set object
        set_data = {
            'description':'my first genome set',
            'items': [ {
                    'ref': self.genome1ref,
                    'label':'genome1'
                },{
                    'ref': self.genome2ref,
                    'label':'genome2'
                }
            ]
        }

        # test a save
        setAPI = self.getImpl()
        res = setAPI.save_genome_set_v1(self.getContext(), {
                'data':set_data,
                'output_object_name':setObjName,
                'workspace': workspace
            })[0]
        self.assertTrue('set_ref' in res)
        self.assertTrue('set_info' in res)
        self.assertEqual(len(res['set_info']), 11)

        self.assertEqual(res['set_info'][1], setObjName)
        self.assertTrue('item_count' in res['set_info'][10])
        self.assertEqual(res['set_info'][10]['item_count'], '2')

        # test get of that object
        d1 = setAPI.get_genome_set_v1(self.getContext(), {
                'ref': workspace + '/' + setObjName
            })[0]
        self.assertTrue('data' in d1)
        self.assertTrue('info' in d1)
        self.assertEqual(len(d1['info']), 11)
        self.assertTrue('item_count' in d1['info'][10])
        self.assertEqual(d1['info'][10]['item_count'], '2')

        self.assertEqual(d1['data']['description'], 'my first genome set')
        self.assertEqual(len(d1['data']['items']), 2)

        item2 = d1['data']['items'][1]
        self.assertTrue('info' not in item2)
        self.assertTrue('ref' in item2)
        self.assertTrue('label' in item2)
        self.assertEqual(item2['label'],'genome2')
        self.assertEqual(item2['ref'],self.genome2ref)

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
        self.assertEqual(d2['info'][10]['item_count'], '2')

        self.assertEqual(d2['data']['description'], 'my first genome set')
        self.assertEqual(len(d2['data']['items']), 2)

        item2 = d2['data']['items'][1]
        self.assertTrue('info' in item2)
        self.assertTrue(len(item2['info']), 11)
        self.assertTrue('ref' in item2)
        self.assertEqual(item2['ref'],self.genome2ref)

        self.assertTrue('ref_path' in item2)
        self.assertEqual(item2['ref_path'], res['set_ref'] + ';' + item2['ref'])
        pprint(d2)

    def test_save_and_get_kbasesearch_genome(self):

        workspace = self.getWsName()
        setObjName = 'set_of_kbasesearch_genomes'

        # create the set object
        set_data = {
            'description': 'my kbasesearch genome set',
            'elements': {
                self.genome1ref: {
                    'ref': self.genome1ref,
                    'metadata': {'test_metadata': 'metadata'}
                },
                self.genome2ref: {
                    'ref': self.genome2ref,
                    'metadata': {'test_metadata': 'metadata'}
                }
            }
        }

        # test a save
        setAPI = self.getImpl()
        res = setAPI.save_genome_set_v1(self.getContext(), {
                'data': set_data,
                'output_object_name': setObjName,
                'workspace': workspace,
                'save_search_set': True
            })[0]

        self.assertTrue('set_ref' in res)
        self.assertTrue('set_info' in res)
        self.assertEqual(len(res['set_info']), 11)

        self.assertEqual(res['set_info'][1], setObjName)
        self.assertTrue('KBaseSearch.GenomeSet' in res['set_info'][2])

        # test get of that object
        d1 = setAPI.get_genome_set_v1(self.getContext(), {
                'ref': workspace + '/' + setObjName
            })[0]
        self.assertTrue('data' in d1)
        self.assertTrue('info' in d1)
        self.assertEqual(len(d1['info']), 11)
        self.assertTrue('KBaseSearch.GenomeSet' in res['set_info'][2])

        self.assertEqual(d1['data']['description'], 'my kbasesearch genome set')
        self.assertEqual(len(d1['data']['elements']), 2)

        elements = d1['data']['elements']
        self.assertTrue(self.genome1ref in elements)
        self.assertTrue(self.genome2ref in elements)

        genome_2 = elements.get(self.genome2ref)
        self.assertTrue('ref' in genome_2)
        self.assertEqual(genome_2.get('ref'), self.genome2ref)
        self.assertEqual(genome_2['metadata']['test_metadata'], 'metadata')

    # NOTE: Comment the following line to run the test
    @unittest.skip("skipped test_save_and_get_of_emtpy_set")
    def test_save_and_get_of_emtpy_set(self):

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
        res = setAPI.save_genome_set_v1(self.getContext(), {
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
        d1 = setAPI.get_genome_set_v1(self.getContext(), {
                'ref': workspace + '/' + setObjName
            })[0]
        self.assertTrue('data' in d1)
        self.assertTrue('info' in d1)
        self.assertEqual(len(d1['info']), 11)
        self.assertTrue('item_count' in d1['info'][10])
        self.assertEqual(d1['info'][10]['item_count'], '0')

        self.assertEqual(d1['data']['description'], 'nothing to see here')
        self.assertEqual(len(d1['data']['items']), 0)

        d2 = setAPI.get_genome_set_v1(self.getContext(), {
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
