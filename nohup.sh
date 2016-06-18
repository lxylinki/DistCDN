#!/bin/bash
# referred from: http://ss64.com/osx/nohup.html
mkdir -p ~/.launch
logfilename="${1##*/}_$(date +%F_%H%M%S)"
echo "== LAUNCH $@ ==" > ~/.launch/${logfilename}_stdout.log
echo "== LAUNCH $@ ==" > ~/.launch/${logfilename}_stderr.log
nohup "$@" >>~/.launch/${logfilename}_stdout.log 2>>~/.launch/${logfilename}_stderr.log &
