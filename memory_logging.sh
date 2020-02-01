#!/usr/bin/env bash

memory_log_path=find_me_more_like_logs/memory.log

rm $memory_log_path
echo "      date     time $(free -mh | grep total | sed -E 's/^    (.*)/\1/g')" >> $memory_log_path
while true; do
    echo "$(date '+%Y-%m-%d %H:%M:%S') $(free -mh | grep Mem: | sed 's/Mem://g')" >> $memory_log_path
    sleep 1
done