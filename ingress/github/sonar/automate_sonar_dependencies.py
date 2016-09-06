import requests
import json
import os
import configparams
import time
import logging
from subprocess import call,check_output, run
import subprocess

def install_sonar_server_dependencies(config):
    configurations = config['config']
    print("yeeeepepepepepeppe")
    print(configurations['install_sonar_server'])
    if(configurations['install_sonar_server']):
        install_sonar_server(config)

def install_sonar_server(config):
    print(os.getcwd())
    configurations = config['config']
    curr_dir = os.getcwd()
    run(["ls","-l"])
    if not os.path.exists("sonar_server_dir"):
        os.makedirs("sonar_server_dir")
    os.chdir("sonar_server_dir")
    if not os.path.exists("sonarqube-6.0.zip"):
        run(["wget", "https://sonarsource.bintray.com/Distribution/sonarqube/sonarqube-6.0.zip"],check=True)
    elif not os.path.exists("sonarqube-6.0"):
        run(["unzip", "sonarqube-6.0.zip"],check=True)
    if os.path.exists("sonarqube-6.0"):
        run(["sonarqube-6.0/bin/macosx-universal-64/sonar.sh","console"])
    os.chdir("..")

def install_sonar_runner_dependencies(config):
    configurations = config['config']
    runner_dir=''
    if(configurations['install_sonar_runner']):
        runner_dir=install_sonar_runner(config)
    return runner_dir

def install_sonar_runner(config):
    configurations = config['config']
    if not os.path.exists("sonar_runner_dir"):
        os.makedirs("sonar_runner_dir")
    os.chdir("sonar_runner_dir")
    if not os.path.exists("sonar-runner-dist-2.4.zip"):
        run(["wget", "http://repo1.maven.org/maven2/org/codehaus/sonar/runner/sonar-runner-dist/2.4/sonar-runner-dist-2.4.zip"],check=True)
    elif not os.path.exists("sonar-runner-2.4"):
        run(["unzip", "sonar-runner-dist-2.4.zip"],check=True)
    print("immmmmmmm")
    runner_dir = os.getcwd()+'/sonar-runner-2.4/bin/sonar-runner'
    print(runner_dir)
    return runner_dir

def automate_processes(config):
    install_sonar_server_dependencies(config)
    install_sonar_runner_dependencies(config)


if __name__ == "__main__":
    parsed = configparams._parse_commandline()
    config = configparams.main(parsed)
    automate_processes(config)
