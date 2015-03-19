#!/bin/sh
MY_VENV=/Users/nikole/.virtualenvs/rtfc
MY_PYTHON=$MY_VENV/bin/python
PROJ_ROOT='/Users/nikole/Documents/git_projects/read_FEC/fecreader'

$MY_PYTHON $PROJ_ROOT/manage.py regen_results
$MY_PYTHON $PROJ_ROOT/manage.py regen_roi
$MY_PYTHON $PROJ_ROOT/manage.py regen_competitive_primaries
$MY_PYTHON $PROJ_ROOT/manage.py regen_overview
