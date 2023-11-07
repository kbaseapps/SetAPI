# -*- coding: utf-8 -*-
import time
from pprint import pprint
from test.base_class import BaseTestClass
from test.conftest import INFO_LENGTH
from test.util import make_reads_refs

import pytest
from SetAPI.generic.GenericSetNavigator import GenericSetNavigator


class SetAPITest(BaseTestClass):
    DEBUG = False

    @classmethod
    def prepare_data(cls: BaseTestClass) -> None:
        """Set up fixtures for the class.

        :param cls: class object
        :type cls: BaseTestClass
        """
        cls.reads_refs = make_reads_refs(cls.foft, cls.ws_name)

    def create_sets(self):
        if hasattr(self.__class__, "setNames"):
            return

        self.__class__.setNames = ["set_o_reads1", "set_o_reads2", "set_o_reads3"]
        self.__class__.setRefs = []

        for s in self.setNames:
            set_data = {
                "description": "my first reads",
                "items": [
                    {"ref": self.reads_refs[0], "label": "reads1"},
                    {"ref": self.reads_refs[1], "label": "reads2"},
                ],
            }
            # test a save - makes a new ReadsSet object in the workspace.
            res = self.set_api_client.save_reads_set_v1(
                self.ctx,
                {"data": set_data, "output_object_name": s, "workspace": self.ws_name},
            )[0]
            self.setRefs.append(res["set_ref"])

    def test_list_sets_bad_input(self):
        ctx = self.ctx
        set_api = self.set_api_client

        with pytest.raises(
            ValueError,
            match='One of "workspace" or "workspaces" field required to list sets',
        ):
            set_api.list_sets(ctx, {"include_set_item_info": 1})

        with pytest.raises(
            ValueError, match='"include_set_item_info" field must be set to 0 or 1'
        ):
            set_api.list_sets(ctx, {"workspace": 12345, "include_set_item_info": "foo"})

    def test_list_sets(self):
        # make sure we can see an empty list of sets before WS has any
        res = self.set_api_client.list_sets(
            self.ctx, {"workspace": self.ws_name, "include_set_item_info": 1}
        )[0]
        assert len(res["sets"]) == 0

        # create the test sets, adds a ReadsSet object in the workspace
        self.create_sets()

        # Get the sets in the workspace along with their item info.
        res = self.set_api_client.list_sets(
            self.ctx, {"workspace": self.ws_name, "include_set_item_info": 1}
        )[0]
        assert "sets" in res
        assert len(res["sets"]) == len(self.setNames)
        for s in res["sets"]:
            assert "ref" in s
            assert "info" in s
            assert "items" in s
            assert len(s["info"]) == INFO_LENGTH
            assert len(s["items"]) == 2
            for item in s["items"]:
                assert "ref" in item
                assert "info" in item
                assert len(item["info"]) == INFO_LENGTH

        # Get the sets in a workspace without their item info (just the refs)
        res2 = self.set_api_client.list_sets(self.ctx, {"workspace": self.ws_name})[0]
        assert "sets" in res2
        assert len(res2["sets"]) == len(self.setNames)
        for s in res2["sets"]:
            assert "ref" in s
            assert "info" in s
            assert "items" in s
            assert len(s["info"]) == INFO_LENGTH
            assert len(s["items"]) == 2
            for item in s["items"]:
                assert "ref" in item
                assert "info" not in item

        # Get the sets with their reference paths
        res3 = self.set_api_client.list_sets(
            self.ctx, {"workspace": self.ws_name, "include_set_item_ref_paths": 1}
        )[0]

        if self.DEBUG:
            print("Result from list_items with ref_paths")
            pprint(res3)
            print("=====================================")

        assert "sets" in res3
        assert len(res3["sets"]) == len(self.setNames)
        for s in res3["sets"]:
            assert "ref" in s
            assert "info" in s
            assert "items" in s
            assert len(s["info"]) == INFO_LENGTH
            assert len(s["items"]) == 2
            for item in s["items"]:
                assert "ref" in item
                assert "info" not in item
                assert "ref_path" in item
                assert item["ref_path"] == s["ref"] + ";" + item["ref"]

        self.unit_test_get_set_items()

    def test_bulk_list_sets(self):
        try:
            ids = []
            for ws_info in self.ws_client.list_workspace_info(
                {"perm": "r", "excludeGlobal": 1}
            ):
                if ws_info[4] < 1000:
                    ids.append(str(ws_info[0]))
                else:
                    print(f"Workspace: {ws_info[1]}, size={ws_info[4]} skipped")

            print("Number of workspaces for bulk list_sets: " + str(len(ids)))
            if len(ids) > 0:
                ret = self.set_api_client.list_sets(
                    self.ctx,
                    {"workspaces": [ids[0]], "include_set_item_info": 1},
                )[0]
            GenericSetNavigator.DEBUG = True
            t1 = time.time()
            ret = self.set_api_client.list_sets(
                self.ctx, {"workspaces": ids, "include_set_item_info": 1}
            )[0]

            print(f"Objects found: {len(ret['sets'])}, time={time.time() - t1}")
        finally:
            GenericSetNavigator.DEBUG = False

    def unit_test_get_set_items(self):
        res = self.set_api_client.get_set_items(
            self.ctx,
            {
                "set_refs": [
                    {"ref": self.setRefs[0]},
                    {"ref": self.setRefs[1]},
                    {"ref": self.setRefs[2]},
                ],
                "include_set_item_ref_paths": 1,
            },
        )[0]
        if self.DEBUG:
            print("Result from get_set_items with ref_paths")
            pprint(res)
            print("========================================")

        assert len(res["sets"]) == 3
        for s in res["sets"]:
            assert "ref" in s
            assert "info" in s
            assert "items" in s
            assert len(s["info"]) == INFO_LENGTH
            assert len(s["items"]) == 2
            for item in s["items"]:
                assert "ref" in item
                assert "info" in item
                assert len(item["info"]) == INFO_LENGTH
                assert "ref_path" in item
                assert item["ref_path"] == s["ref"] + ";" + item["ref"]
