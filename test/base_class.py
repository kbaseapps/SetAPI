# -*- coding: utf-8 -*-
import unittest
from test.conftest import get_test_config


class BaseTestClass(unittest.TestCase):
    @classmethod
    def setUpClass(cls: unittest.TestCase) -> None:
        props = get_test_config()
        for prop in [
            "cfg",
            "ctx",
            "serviceImpl",
            "wsClient",
            "wsName",
            "au",
            "dfu",
            "foft",
        ]:
            setattr(cls, prop, props[prop])

        cls.prepare_data()

    @classmethod
    def prepare_data(cls: unittest.TestCase) -> None:
        """Set up test fixtures.
        Subclasses should implement whatever functions are required to set up the test cases.

        :param cls: class object
        :type cls: BaseTestClass
        """

    @classmethod
    def tearDownClass(cls: unittest.TestCase) -> None:
        if hasattr(cls, "wsName"):
            cls.wsClient.delete_workspace({"workspace": cls.wsName})
            print("Test workspace was deleted")
