# -*- coding: utf-8 -*-
import unittest
import os
import json
import time
import requests

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


    # @classmethod
    # def setup_data(cls):

    #     ws = self.getWsClient()
    #     ws_name = self.getWsName()

    #     ru = ReadsUtils(os.environ['SDK_CALLBACK_URL'])
    #     shutil.copy('data/GCF_000005845.2_ASM584v2_genomic.gbff', cls.cfg['scratch'])
    #     shock_file = dfu.file_to_shock({
    #                         'file_path': os.path.join(cls.cfg['scratch'], 'GCF_000005845.2_ASM584v2_genomic.gbff'),
    #                         'make_handle': 1
    #                     })




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
    def test_your_method(self):


        set_data = {
            'description':'stuff and things',
            'items': [ 
            {
                'ref':'11492/19'
            },
            {
                'ref':'11492/19',
                'label':'number2'
            }
            ]
        }

        setAPI = self.getImpl()
        res = setAPI.save_reads_set_v1(self.getContext(), {
                'data':set_data,
                'output_object_name':'my_reads',
                'workspace_id': 11492
            })[0]
        pprint(res)


        setAPI.get_reads_set_v1(self.getContext(), {
                'ref':res['set_ref']
            })


        pass
        
