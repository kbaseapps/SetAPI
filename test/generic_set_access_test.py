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

from ReadsUtils.ReadsUtilsClient import ReadsUtils
from DataPaletteService.DataPaletteServiceClient import DataPaletteService


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
        cls.serviceWizardURL = cls.cfg['service-wizard']
        cls.dataPaletteServiceVersion = cls.cfg['datapaletteservice-version']


        # setup data at the class level for now (so that the code is run
        # once for all tests, not before each test case.  Not sure how to
        # do that outside this function..)
        suffix = int(time.time() * 1000)
        wsName = "test_SetAPI_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': wsName})
        cls.wsName = wsName

        # copy test file to scratch area
        fq_filename = "interleaved.fastq"
        fq_path = os.path.join(cls.cfg['scratch'], fq_filename)
        shutil.copy(os.path.join("data", fq_filename), fq_path)

        ru = ReadsUtils(os.environ['SDK_CALLBACK_URL'])
        cls.read1ref = ru.upload_reads({
                'fwd_file': fq_path,
                'sequencing_tech': 'tech1',
                'wsname': wsName,
                'name': 'reads1',
                'interleaved':1
            })['obj_ref']
        cls.read2ref = ru.upload_reads({
                'fwd_file': fq_path,
                'sequencing_tech': 'tech2',
                'wsname': wsName,
                'name': 'reads2',
                'interleaved':1
            })['obj_ref']

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
                'description':'my first reads',
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
                    'data':set_data,
                    'output_object_name':s,
                    'workspace': workspace
                })[0]
            self.setRefs.append(res['set_ref'])


    # NOTE: According to Python unittest naming rules test method names should start from 'test'.
    def test_list_sets(self):

        workspace = self.getWsName()
        setAPI = self.getImpl()

        # make sure we can see an empty list of sets before WS has any
        res = setAPI.list_sets(self.getContext(), {
                'workspace':workspace,
                'include_set_item_info':1
            })[0]


        # create the test sets
        self.create_sets()

        res = setAPI.list_sets(self.getContext(), {
                'workspace':workspace,
                'include_set_item_info':1
            })[0]
        self.assertTrue('sets' in res)
        self.assertEqual(len(res['sets']), len(self.setNames))
        for s in res['sets']:
            self.assertTrue('ref' in s)
            self.assertTrue('info' in s)
            self.assertTrue('items' in s)
            self.assertEqual(len(s['info']),11)
            self.assertEqual(len(s['items']),2)
            for item in s['items']:
                self.assertTrue('ref' in item)
                self.assertTrue('info' in item)
                self.assertEqual(len(item['info']),11)

        res2 = setAPI.list_sets(self.getContext(), {
                'workspace':workspace
            })[0]
        self.assertTrue('sets' in res2)
        self.assertEqual(len(res2['sets']), len(self.setNames))
        for s in res2['sets']:
            self.assertTrue('ref' in s)
            self.assertTrue('info' in s)
            self.assertTrue('items' in s)
            self.assertEqual(len(s['info']),11)
            self.assertEqual(len(s['items']),2)
            for item in s['items']:
                self.assertTrue('ref' in item)
                self.assertTrue('info' not in item)


        res = setAPI.get_set_items(self.getContext(), {
                'set_refs': [{'ref':self.setRefs[0]}]
            })[0]
        self.assertEqual(len(res['sets']), 1)
        for s in res['sets']:
            self.assertTrue('ref' in s)
            self.assertTrue('info' in s)
            self.assertTrue('items' in s)
            self.assertEqual(len(s['info']),11)
            self.assertEqual(len(s['items']),2)
            for item in s['items']:
                self.assertTrue('ref' in item)
                self.assertTrue('info' in item)
                self.assertEqual(len(item['info']),11)

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
            set_list = self.getImpl().list_sets(self.getContext(),
                                                {'workspace': wsName2, 
                                                 'include_set_item_info': 1})[0]['sets']
            self.assertEqual(1, len(set_list))
            set_info = set_list[0]
            info = set_info['info']
            self.assertEqual(self.getWsName(), info[7])
            self.assertEqual(set_obj_name, info[1])
        finally:
            self.getWsClient().delete_workspace({'workspace': wsName2})


