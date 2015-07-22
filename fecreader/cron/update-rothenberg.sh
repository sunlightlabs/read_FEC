#!/bin/bash
NAME=realtimefec
PROJ=fecreader

source /projects/realtimefec/src/realtimefec/fecreader/rothenberg/shellscripts/get_files.sh

source /projects/$NAME/virt/bin/activate
/projects/$NAME/src/$NAME/$PROJ/manage.py load_rothenberg_ratings
/projects/$NAME/src/$NAME/$PROJ/manage.py set_rothenberg_ratings
