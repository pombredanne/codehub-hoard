#!/usr/bin/env python

import glob2
import requests
import json
import xmltodict
import shutil,pickle
import pickle, kafkaConsumer, kafkaProducer
import time
from datetime import datetime
import logging
from subprocess import Popen, PIPE
import subprocess
from os.path import expanduser
from pykafka import KafkaClient
import os, sys
sys.path.append(os.path.abspath("../config"))
#pylint: disable=import-error
import configparams
ssl_verify='/etc/ssl/cert.pem'

class ExecVirusScan():

    def _process_metric_line(self, line):
        if line is None:
            return None, None

        supportedMetrics = ["Scanned directories","Scanned files","Infected files","Data scanned","Time"]

        parts = line.split(':')
        if len(parts) != 2:
            return None, None

        name = parts[0].strip()
        if name.lower() not in (x.lower() for x in supportedMetrics):
            return None, None

        name = name.lower().replace(" ","_")
        val = parts[1].strip()
        if val.isdigit():
            v = int(val)
            val = v

        return name, val

    def _process_file_line(self, line, ref_path):
        if line is None:
            return None

        parts = line.split(" ")
        if len(parts) != 3:
            return None

        result = {}
        file_name = parts[0][:-1]
        p = file_name.find(ref_path)
        if p >= 0:
            file_name = file_name[p:]

        result['filename'] = file_name
        result['virus'] = parts[1]
        return result


    def _process_vscan_output(self, output, ref_path):
        if output is None:
            return None

        lines = output.splitlines()
        if len(lines) <= 0:
            return None

        result = {}
        files = []
        metrics = False
        for line in lines:
            if not metrics:
                if "FOUND" in line:
                    pline = self._process_file_line(line, ref_path)
                    if pline is None:
                        continue
                    files.append(pline)
                if "SCAN SUMMARY" in line:
                    metrics = True
                    continue
            else:
                mName, mValue = self._process_metric_line(line)
                if mName is None:
                    continue
                result[mName] = mValue
        result['lastscan'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        result['reported_files'] = files
        return result


    def _execute_vscan(self, cloned_project_path, ref_path):
        target = cloned_project_path
        proc = Popen(['clamscan', '-i', '-o', '-r', target], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = proc.communicate()
        rc = proc.returncode
        # rc values: 0=no virus found, 1=virus found, 2=error
        if rc == 2:
            print("ERROR: " + err)
            return None

        report = self._process_vscan_output(output, ref_path)
        return report


    def _process_messages(self, config, messages):
        for message in messages:
            if message is not None:
                data = pickle.loads(message.value)
                if data is None:
                    continue
                print(time.strftime("%c")+" Scanning files for: "+data['org']+"->"+data['project_name'])
                cloned_project_path = data["cloned_project_path"]
                if not os.path.isdir(cloned_project_path):
                    print("ERROR: Path not found: "+ cloned_project_path)
                    print(time.strftime("%c")+" Scan completed.")
                    continue
                ref_path = data["org"]+"/"+data["project_name"]
                vscan_result = self._execute_vscan(cloned_project_path, ref_path)
                if vscan_result is None:
                    print("WARNING: No results")
                    print(time.strftime("%c")+" Scan completed.")
                    continue
                data["vscan"] = vscan_result
                print('MSG: VIRUS_SCAN_QUEUE')
                kafkaProducer.publish_kafka_message(data,config,'VIRUS_SCAN_QUEUE')
                print(time.strftime("%c")+" Scan completed.")


    def automate_processes(self, config):
        print(time.strftime("%c")+" VScan processing started")
        messages = kafkaConsumer._get_balanced_consumer(config,'consumer_vscan_group')
        self._process_messages(config, messages)
        print(time.strftime("%c")+" VScan processing started")


if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    evs = ExecVirusScan()
    evs.automate_processes(config)

