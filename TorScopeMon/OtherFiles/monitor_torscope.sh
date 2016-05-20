#!/bin/bash

source /home/uboonesmc/setup_SMC_EPICS.sh
setup root v5_34_25a -q e7:prof
export PYTHONPATH=$PYTHONPATH:$HOME/.local/lib/python2.6/site-packages/pyepics-3.2.4-py2.6.egg/
echo $PYTHONPATH
which -a python

python mon_root.py
