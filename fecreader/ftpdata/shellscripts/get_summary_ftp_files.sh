#!/bin/bash

datadir=/projects/realtimefec/src/realtimefec/fecreader/ftpdata/data

for year in  '16' 
do
    echo "Getting files for: $year"

    #for filename in 'ccl' 'oth' 'pas2' 'cn' 'cm' 'indiv'
    for filename in 'ccl' 'cn' 'cm'
    
    do
        echo "Getting file: $filename"
        curl -o $datadir/$year/$filename$year.zip ftp://ftp.fec.gov/FEC/20$year/$filename$year.zip
        unzip -p -o $datadir/$year/$filename$year.zip  > $datadir/$year/$filename$year.txt
        
        # The files have no variable representing the cycle; add one
        # Be careful not to mix shell variables... 
        # \Q ... \E means escape special chars -- so we don't get messed up by '('
        perl -pe "s/(\Q\$_\E)/20$year|\$1/" $datadir/$year/$filename$year.txt > $datadir/$year/$filename$year-fixed.txt
        # one or more backslashes immediately preceding a bar messes up postgres' copy
        perl -pi -e 's/\\+\|/|/g' $datadir/$year/$filename$year-fixed.txt
        # also, kill out some weird chars that are in here too
        perl -pi -e 'tr/\xa0//d' $datadir/$year/$filename$year-fixed.txt
        
        sleep 1
    done

done
    
