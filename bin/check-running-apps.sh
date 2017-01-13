#!/usr/bin/env bash

#set -e

#This script is run before the updated package is deployed to the server. It checks to see
#if any of the ingest scripts are currently running and waits till they are all done. Long running
#processes are killed.

INGEST_TOOLS=${ingest.tools.dir}

echo Stopping Nifi ...
sudo -u ec2-user $INGEST_TOOLS/nifi-*/bin/nifi.sh stop

sleep 60

PROCESS_NAME_ENDING="ingest.sh"

pids=$(pgrep -f $PROCESS_NAME_ENDING)
while [ "$pids" != "" ]; do
    echo "Waiting for jobs to finish .."
    sleep 10
    pids=$(pgrep -f $PROCESS_NAME_ENDING)
done

pid_dep=`ps -ef | grep .*[p]rocess_dependency_messages.py.* | awk '{ printf $2 }'`
echo $pid_dep
if [ ! -z "${pid_dep}" ]; then
    echo "Shutting down Process_dependency_messages.py process.."
    kill ${pid_dep}
fi

pid_kaf=`ps -ef | grep .*[k]afkaDependencyEsUpdate.py.* | awk '{ printf $2 }'`
if [ ! -z "${pid_kaf}" ]; then
    echo "Shutting down KafkaDependencyEsUpdate.py process.."
    kill ${pid_kaf}
fi

pid_clon=`ps -ef | grep .*[c]lone_repos.py.* | awk '{ printf $2 }'`
if [ ! -z "${pid_clon}" ]; then
    echo "Shutting down cloned_repos.py process.."
    kill ${pid_clon}
fi

pid_clon_dep=`ps -ef | grep .*[c]loned_dep_data.py.* | awk '{ printf $2 }'`
if [ ! -z "${pid_clon_dep}" ]; then
    echo "Shutting down cloned_dep_data.py process.."
    kill ${pid_clon_dep}
fi

pid_son=`ps -ef | grep .*[p]rocess_sonar_messages.py.* | awk '{ printf $2 }'`
if [ ! -z "${pid_son}" ]; then
    echo "Shutting down process_sonar_messages.py process.."
    kill ${pid_son}
fi

pid1=`ps -ef | grep .*[d]ep_clone_projects.sh.* | awk '{ printf $2 }'`
if [ ! -z "${pid1}" ]; then
    echo "Shutting down dep_clone_projects.sh process.."
    kill ${pid1}
fi

pid2=`ps -ef | grep .*[k]afka_consume_cloned_data.sh.* | awk '{ printf $2 }'`
if [ ! -z "${pid2}" ]; then
    echo "Shutting down kafka_consume_cloned_data.sh process.."
    kill ${pid2}
fi

pid3=`ps -ef | grep .*[k]afka_process_dependecy_data.sh.* | awk '{ printf $2 }'`
if [ ! -z "${pid3}" ]; then
    echo "Shutting down kafka_process_dependecy_data.sh process.."
    kill ${pid3}
fi

pid4=`ps -ef | grep .*[k]afka_consume_dependency_data.sh.* | awk '{ printf $2 }'`
if [ ! -z "${pid4}" ]; then
    echo "Shutting down kafka_consume_dependency_data.sh process.."
    kill ${pid4}
fi

pid5=`ps -ef | grep .*[s]harable_clone_projects.sh.* | awk '{ printf $2 }'`
if [ ! -z "${pid5}" ]; then
    echo "Shutting down sharable_clone_projects.sh process.."
    kill ${pid5}
fi
exit 0
