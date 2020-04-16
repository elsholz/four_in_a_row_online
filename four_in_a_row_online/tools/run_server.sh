#!/bin/bash
python3 four_in_a_row_online/backend/server.py &
server_pid=$!
sleep 5s
while true
do 
	if [ ./repo_updated.sh ] 
	then
		echo "Repo has been updated. Service will restart server (pid $server_pid)."
		echo "Python Path is: $PYTHONPATH"
		echo "Path is $(pwd)"
		kill $server_pid
		python3 four_in_a_row_online/backend/server.py &
		server_pid=$!
		echo "Server has been restarted, pid: $server_pid"
	else
		echo "Repo has not been updated, so the server will remain running."
	fi
	sleep 1m
done
