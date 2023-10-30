# -*- coding: utf-8 -*-
import time
from pprint import pprint
from test.base_class import BaseTestClass
from test.conftest import INFO_LENGTH

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
        [info1, info2] = cls.foft.create_fake_reads(
            {"ws_name": cls.wsName, "obj_names": ["reads1", "reads2"]}
        )
        cls.read1ref = str(info1[6]) + "/" + str(info1[0]) + "/" + str(info1[4])
        cls.read2ref = str(info2[6]) + "/" + str(info2[0]) + "/" + str(info2[4])

    def create_sets(self):
        if hasattr(self.__class__, "setNames"):
            return

        self.__class__.setNames = ["set_o_reads1", "set_o_reads2", "set_o_reads3"]
        self.__class__.setRefs = []

        setAPI = self.serviceImpl
        for s in self.setNames:
            set_data = {
                "description": "my first reads",
                "items": [
                    {"ref": self.read1ref, "label": "reads1"},
                    {"ref": self.read2ref, "label": "reads2"},
                ],
            }
            # test a save - makes a new ReadsSet object in the workspace.
            res = setAPI.save_reads_set_v1(
                self.ctx,
                {"data": set_data, "output_object_name": s, "workspace": self.wsName},
            )[0]
            self.setRefs.append(res["set_ref"])

    def test_list_sets_bad_input(self):
        ctx = self.ctx
        set_api = self.serviceImpl

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
        setAPI = self.serviceImpl

        # make sure we can see an empty list of sets before WS has any
        res = setAPI.list_sets(
            self.ctx, {"workspace": self.wsName, "include_set_item_info": 1}
        )[0]
        assert len(res["sets"]) == 0

        # create the test sets, adds a ReadsSet object in the workspace
        self.create_sets()

        # Get the sets in the workspace along with their item info.
        res = setAPI.list_sets(
            self.ctx, {"workspace": self.wsName, "include_set_item_info": 1}
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
        res2 = setAPI.list_sets(self.ctx, {"workspace": self.wsName})[0]
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
        res3 = setAPI.list_sets(
            self.ctx, {"workspace": self.wsName, "include_set_item_ref_paths": 1}
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
            for ws_info in self.wsClient.list_workspace_info(
                {"perm": "r", "excludeGlobal": 1}
            ):
                if ws_info[4] < 1000:
                    ids.append(str(ws_info[0]))
                else:
                    print(f"Workspace: {ws_info[1]}, size={ws_info[4]} skipped")

            print("Number of workspaces for bulk list_sets: " + str(len(ids)))
            if len(ids) > 0:
                ret = self.serviceImpl.list_sets(
                    self.ctx,
                    {"workspaces": [ids[0]], "include_set_item_info": 1},
                )[0]
            GenericSetNavigator.DEBUG = True
            t1 = time.time()
            ret = self.serviceImpl.list_sets(
                self.ctx, {"workspaces": ids, "include_set_item_info": 1}
            )[0]
            print(
                (
                    "Objects found: "
                    + str(len(ret["sets"]))
                    + ", time="
                    + str(time.time() - t1)
                )
            )
        finally:
            GenericSetNavigator.DEBUG = False

    def unit_test_get_set_items(self):
        res = self.serviceImpl.get_set_items(
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
