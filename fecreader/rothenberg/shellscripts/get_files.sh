#!/bin/bash

# Download rating files, and back them up to a timestamped backup dir

datadir=/projects/realtimefec/src/realtimefec/fecreader/rothenberg/data

now=$(date +"%m-%d-%Y-%H-%M")

for type in 'house' 'senate' 
do
    download_filename=$datadir/$type.xml
    backup_filename=$datadir/backups/$type$now.xml
    echo "Running command: curl -o $download_filename --connect-timeout 500 \"http://www.rothenbergpoliticalreport.com/api/xml/ratings/$type\""
    curl -o $download_filename --connect-timeout 500 "http://www.rothenbergpoliticalreport.com/api/xml/ratings/$type"
    cp $download_filename $backup_filename
    echo "sleeping 10"
    sleep 10
done

