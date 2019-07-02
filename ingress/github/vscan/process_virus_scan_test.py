#!/usr/bin/env python

import unittest
import mock
from process_virus_scan import ProcessVirusScan

class TestProcessVirusScan(unittest.TestCase):

    def setUp(self):
        self.pvs = ProcessVirusScan()

    def test_prepare_update_data__invalid_data(self):
        data = None
        result = self.pvs._prepare_update_data(data)
        self.assertIsNone(result)


    def test_prepare_update_data__invalid_vscan_data(self):
        data = {}
        result = self.pvs._prepare_update_data(data)
        self.assertIsNone(result)


    def test_prepare_update_data__valid_vscan(self):
        data = {}
        data["vscan"] = "test"
        result = self.pvs._prepare_update_data(data)
        self.assertTrue("doc" in result)
        self.assertTrue("vscan" in result["doc"])
        self.assertEqual("test", result["doc"]["vscan"])


    def test_update_project_data__invalid_project_id(self):
        configurations = {}
        configurations["stage_es_url"] = "http://test"
        config={}
        config["config"]=configurations
        data={}

        result = self.pvs._update_project_data(config, data)
        self.assertIsNone(result)


    def test_update_project_data__invalid_data(self):
        configurations = {}
        configurations["stage_es_url"] = "http://test"
        config={}
        config["config"]=configurations
        data={}
        data["_id"] = "the_id"

        result = self.pvs._update_project_data(config, data)
        self.assertIsNone(result)


    @mock.patch("process_virus_scan.requests.post")
    def test_update_project_data__valid_update(self, mock_post):
        configurations = {}
        configurations["stage_es_url"] = "http://test"
        config={}
        config["config"]=configurations
        data={}
        data["_id"] = "the_id"
        data["vscan"] = "test"

        m = mock.Mock(ok=True,status_code=200,return_value=True)
        r = mock.Mock(return_value=m)
        mock_post.return_value = r()

        result = self.pvs._update_project_data(config, data)
        self.assertTrue(result)


    @mock.patch("process_virus_scan.requests.post")
    def test_update_project_data__invalid_update(self, mock_post):
        configurations = {}
        configurations["stage_es_url"] = "http://test"
        config={}
        config["config"]=configurations
        data={}
        data["_id"] = "the_id"
        data["vscan"] = "test"

        m = mock.Mock(ok=False,status_code=404,return_value=False)
        r = mock.Mock(return_value=m)
        mock_post.return_value = r()

        result = self.pvs._update_project_data(config, data)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
