#!/usr/bin/env python

import unittest
import mock
from exec_virus_scan import ExecVirusScan

class TestExecVirusScan(unittest.TestCase):

    def setUp(self):
        self.evs = ExecVirusScan()

    def test_process_metric_line__valid_line(self):
        line = None
        name, val = self.evs._process_metric_line(line)
        self.assertIsNone(name)
        self.assertIsNone(val)


    def test_process_metric_line__valid_data(self):
        line = "Scanned directories: 5"
        name, val = self.evs._process_metric_line(line)
        self.assertEqual(name.lower(), 'scanned_directories')
        self.assertEqual(val, 5)


    def test_process_metric_line__invalid_data(self):
        line = "Scanned directories"
        name, val = self.evs._process_metric_line(line)
        self.assertEqual(name, None)
        self.assertEqual(val, None)


    def test_process_metric_line__not_valid_field(self):
        line = "ddirectories"
        name, val = self.evs._process_metric_line(line)
        self.assertEqual(name, None)
        self.assertEqual(val, None)


    def test_process_metric_line__name_without_spaces(self):
        line = "Infected files:0"
        name, val = self.evs._process_metric_line(line)
        self.assertFalse(' ' in name)
        self.assertIsNotNone(val)


    def test_process_metric_line__value_is_digit(self):
        line = "Infected files:5"
        name, val = self.evs._process_metric_line(line)
        self.assertTrue(type(val) is int)
        self.assertIsNotNone(name)


    def test_process_file_line__invalid_line(self):
        line = None
        result = self.evs._process_file_line(line, None)
        self.assertIsNone(result)


    def test_process_file_line__has_3_parts1(self):
        line = "./cloned_projects/Stage/stage-webapp/file-name1: Trojan.FakeAV-136 FOUND"
        result = self.evs._process_file_line(line, "")
        self.assertIsNotNone(result)


    def test_process_file_line__has_3_parts2(self):
        line = "./cloned_projects/Stage/stage-webapp/file-name1: Trojan.FakeAV-136"
        result = self.evs._process_file_line(line, "")
        self.assertIsNone(result)


    def test_process_file_line__fix_path(self):
        line = "./cloned_projects/Stage/stage-webapp/file-name1: Trojan.FakeAV-136 FOUND"
        result = self.evs._process_file_line(line, "Stage/stage-webapp")
        self.assertEqual(result['filename'], "Stage/stage-webapp/file-name1")


    def test_process_vscan_output__invalid_data(self):
        ref_path = "Stage/stage-webapp"
        output = None
        result = self.evs._process_vscan_output(output, ref_path)
        self.assertIsNone(result)


    def test_process_vscan_output__no_lines(self):
        ref_path = "Stage/stage-webapp"
        output = ""
        result = self.evs._process_vscan_output(output, ref_path)
        self.assertIsNone(result)


    def test_process_vscan_output__no_data(self):
        ref_path = "Stage/stage-webapp"
        output = "line 1\nline2\nline3"
        result = self.evs._process_vscan_output(output, ref_path)
        r = len(result)
        self.assertEqual(r, 2)


    def test_process_vscan_output__no_files(self):
        ref_path = "Stage/stage-webapp"
        output = "line 1\nline2\nline3"
        result = self.evs._process_vscan_output(output, ref_path)
        r = len(result['reported_files'])
        self.assertEqual(r, 0)


    def test_process_vscan_output__one_file_found(self):
        ref_path = "Stage/stage-webapp"
        output = "./cloned_projects/Stage/stage-webapp/file-name1: Trojan.FakeAV-136 FOUND\n"
        result = self.evs._process_vscan_output(output, ref_path)
        r = len(result['reported_files'])
        self.assertEqual(r, 1)


    def test_process_vscan_output__one_metric(self):
        ref_path = "Stage/stage-webapp"
        output = "- SCAN SUMMARY -\nInfected files: 2\n"
        result = self.evs._process_vscan_output(output, ref_path)
        self.assertIsNotNone(result['infected_files'])


    @mock.patch("exec_virus_scan.Popen")
    def test_execute_vscan__error_returned(self,mock_popen):
        proc = mock.Mock()
        proc.communicate.return_value = ['test', 'err']
        mock_popen.return_value = proc
        mock_popen().returncode = 2

        ref_path = "Stage/stage-webapp"
        cloned_project_path = "/x/y/z"

        result = self.evs._execute_vscan(cloned_project_path,ref_path)
        self.assertIsNone(result)


    @mock.patch("exec_virus_scan.Popen")
    def test_execute_vscan__no_virus(self,mock_popen):
        output = """
----------- SCAN SUMMARY -----------
Scanned directories: 5
        """
        proc = mock.Mock()
        proc.communicate.return_value = [output, 'err']
        mock_popen.return_value = proc
        mock_popen().returncode = 0

        ref_path = "Stage/stage-webapp"
        cloned_project_path = "/x/y/z"

        result = self.evs._execute_vscan(cloned_project_path,ref_path)
        self.assertIsNotNone(result)
        self.assertTrue(len(result['reported_files']) == 0)


    @mock.patch("exec_virus_scan.Popen")
    def test_execute_vscan__virus_found(self,mock_popen):
        output = """
./cloned_projects/Stage/stage-webapp/file-name2: Trojan.FakeAV-136 FOUND
----------- SCAN SUMMARY -----------
Scanned directories: 5
        """
        proc = mock.Mock()
        proc.communicate.return_value = [output, 'err']
        mock_popen.return_value = proc
        mock_popen().returncode = 1

        ref_path = "Stage/stage-webapp"
        cloned_project_path = "/x/y/z"

        result = self.evs._execute_vscan(cloned_project_path,ref_path)
        self.assertIsNotNone(result)
        self.assertTrue(len(result['reported_files']) == 1)


if __name__ == "__main__":
    unittest.main()
