#!/usr/bin/env bash

./env/bin/rqscheduler --host localhost --port 6379 --db 0 --interval 0.033 &
./env/bin/rq worker message &
wait
