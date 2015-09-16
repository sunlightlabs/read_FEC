#!/bin/sh
MY_VENV=$HOME/.virtualenvs/rtfc
MY_PYTHON=$MY_VENV/bin/python
PROJ_ROOT=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

$MY_PYTHON $PROJ_ROOT/manage.py regen_results
$MY_PYTHON $PROJ_ROOT/manage.py regen_roi
$MY_PYTHON $PROJ_ROOT/manage.py regen_competitive_primaries
$MY_PYTHON $PROJ_ROOT/manage.py regen_overview
