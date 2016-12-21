#!/usr/bin/env bash

#This script is run before the updated package is deployed to the server. It checks to see
#if any of the ingest scripts are currently running and waits till they are all done. Long running
#processes are killed.

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

pid_clon=`ps -ef | grep .*[c]loned_dep_data.py.* | awk '{ printf $2 }'`
if [ ! -z "${pid_clon}" ]; then
    echo "Shutting down Cloned_dep_data.py process.."
    kill ${pid_clon}
fi

pid_son=`ps -ef | grep .*[p]rocess_sonar_messages.py.* | awk '{ printf $2 }'`
if [ ! -z "${pid_son}" ]; then
    echo "Shutting down Process_sonar_messages.py process.."
    kill ${pid_son}
fi
