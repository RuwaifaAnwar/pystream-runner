#! bin/bash
#Check whether a ASN in it customer cone or not
a=$(cat subs701.txt)
for i in $a
    do
        ans=$(cat dum | grep " $i " | wc -l)
        if [ $ans -eq 1 ]; then
            echo "yes for $i" 
        fi
    done
            
