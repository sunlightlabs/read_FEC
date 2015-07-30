#!/bin/bash
NAME=realtimefec
PROJ=fecreader

# This doesn't use the feed, it tests the file downloads
# This is everything to handle the files before the body rows are entered
# After the body rows are entered, the exotic ones must be superceded

source /projects/$NAME/virt/bin/activate
# /projects/$NAME/src/$NAME/$PROJ/manage.py scrape_rss_filings
/projects/$NAME/src/$NAME/$PROJ/manage.py find_new_filings
/projects/$NAME/src/$NAME/$PROJ/manage.py download_new_filings
/projects/$NAME/src/$NAME/$PROJ/manage.py enter_headers_from_new_filings
/projects/$NAME/src/$NAME/$PROJ/manage.py set_new_filing_details
/projects/$NAME/src/$NAME/$PROJ/manage.py mark_amended
/projects/$NAME/src/$NAME/$PROJ/manage.py send_body_row_jobs
/projects/$NAME/src/$NAME/$PROJ/manage.py remove_blacklisted
