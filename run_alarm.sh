#!/bin/bash
SRC_DIR=$(dirname $0)
TZ=UTC date +"%F %H:%M:%S %Z starting"
source ~/anaconda2/bin/activate
python alarm.py
TZ=UTC date +"%Y-%m-%d %H:%M:%S %Z finished"
