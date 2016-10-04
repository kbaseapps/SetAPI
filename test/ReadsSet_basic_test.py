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

        pprint(cls.cfg)

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
        cls.read3ref = ru.upload_reads({
                'fwd_file': fq_path,
                'sequencing_tech': 'tech3',
                'wsname': wsName,
                'name': 'reads3',
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
                    'ref': self.read2ref,
                    'label':'reads3'
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

        item2 = d1['data']['items'][2]
        self.assertTrue('info' not in item2)
        self.assertTrue('ref' in item2)
        self.assertEqual(item2['ref'],self.read2ref)


        # test the call to make sure we get info for each item
        d2 = setAPI.get_reads_set_v1(self.getContext(), {
                'ref':res['set_ref'],
                'include_item_info':1
            })[0]
        self.assertTrue('data' in d2)
        self.assertTrue('info' in d2)
        self.assertEqual(len(d2['info']), 11)
        self.assertTrue('item_count' in d2['info'][10])
        self.assertEqual(d2['info'][10]['item_count'], '3')

        self.assertEqual(d2['data']['description'], 'my first reads')
        self.assertEqual(len(d2['data']['items']), 3)

        item2 = d2['data']['items'][2]
        self.assertTrue('info' in item2)
        self.assertTrue(len(item2['info']), 11)
        self.assertTrue('ref' in item2)
        self.assertEqual(item2['ref'],self.read2ref)


