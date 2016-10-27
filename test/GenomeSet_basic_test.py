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

#from AssemblyUtil.AssemblyUtilClient import AssemblyUtil
from GenomeFileUtil.GenomeFileUtilClient import GenomeFileUtil
class SetAPITest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        user_id = requests.post(
            'https://kbase.us/services/authorization/Sessions/Login',
            data='token={}&fields=user_id'.format(token)).json()['user_id']
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
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('SetAPI'):
            cls.cfg[nameval[0]] = nameval[1]
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL, token=token)
        cls.serviceImpl = SetAPI(cls.cfg)

        # setup data at the class level for now (so that the code is run
        # once for all tests, not before each test case.  Not sure how to
        # do that outside this function..)
        suffix = int(time.time() * 1000)
        wsName = "test_SetAPI_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': wsName})
#        wsName = 'pranjan77:1477441032423'
        cls.wsName = wsName
        # copy test file to scratch area
        gbff_filename = "GCF_000005845.2_ASM584v2_genomic.gbff"
        gbff_path = os.path.join(cls.cfg['scratch'], gbff_filename)
        shutil.copy(os.path.join("data", gbff_filename), gbff_path)

        ru = GenomeFileUtil(os.environ['SDK_CALLBACK_URL'])
        ws_obj_name = 'MyNewGenome'
        cls.genome1ref = ru.genbank_to_genome( 
            {
                'file':{'path':gbff_path},
                'workspace_name':wsName,
                'genome_name':'genome_obj_1'
            })['genome_ref']
        cls.genome2ref = ru.genbank_to_genome( 
            {
                'file':{'path':gbff_path},
                'workspace_name':wsName,
                'genome_name':'genome_obj_2'
            })['genome_ref']


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
                'include_item_info':1
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


        # NOTE: According to Python unittest naming rules test method names should start from 'test'.
    def skip_test_save_and_get_of_emtpy_set(self):

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
