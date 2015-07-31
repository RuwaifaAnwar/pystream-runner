#!/bin/bash
here=$1

cat as_rel.txt | grep "$1|" | grep "$2|"
#line=$(cat afterday.log | grep " 19905 " | grep -v "19905," | grep -v "19905 #" | grep detected | awk '{print $6,$7}' | sort | uniq)
