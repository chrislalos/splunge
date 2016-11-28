#!/bin/bash

if [[ -z SSH_AUTH_SOCK || -z SSH_AGENT_PID ]]; then
	>&2 echo "Please run ssh-agent and then rerun this script"
	exit 1
fi

home=$(getdir "${BASH_SOURCE[0]}")
export PYTHONPATH=$PYTHONPATH:$home
echo PYTHONPATH=$PYTHONPATH
commitMsg=${1:-'no message'}
git -C "$home" commit -am "$commitMsg" && git push; python3 -m setup clean sdist upload -r splunge
