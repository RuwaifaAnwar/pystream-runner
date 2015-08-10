cat full_out_bads_detailed.logs | grep BAD  | grep -v remov | awk '{print $7}' | sort | uniq -c | sort -nk1 
