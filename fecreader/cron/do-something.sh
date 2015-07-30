#!/bin/bash
NAME=realtimefec
PROJ=fecreader

source /projects/$NAME/virt/bin/activate
/projects/$NAME/src/$NAME/$PROJ/manage.py management_command_here
