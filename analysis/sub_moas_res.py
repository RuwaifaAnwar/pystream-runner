from __future__ import division
import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib.pyplot as plt
#import pylab
import itertools 
import timeit
import sys
import time
import operator
import re
out = open("full_out_bads_detailed.logs","a") 
fil = open("2test_2months.logs","r") 
lines=fil.readlines()

cc_dict={}
with open("ppdc-ases.txt") as file:
    for line in file:
        if "#" in line:
            continue
        toks=line.split()
        l=[]
        l=[int(x) for x in toks]
        cc_dict[l[0]]={}
        cc_dict[l[0]]=l[1:]

##        
as_rank={}
with open("as_rel.txt") as file:
    for line in file:
        str1=line.split('|')
        provider=int(str1[0])   
        customer=int(str1[1])   
        relation=int(str1[2])
#        if customer > 600000 or provider > 600000:
#            continue
        if provider not in as_rank:
            as_rank[provider]={}
            as_rank[provider][customer]=relation
        else:
            as_rank[provider][customer]=relation

##  

#print find_relation(7018,6478)

##
def prep_siblings():
    miss = open("sib_list.txt","r") 
    lines=miss.readlines()
    domain=""
    ases=[]
    sib_dic={}
    for line in lines:
        toks=line.split()
        asn=int(toks[0])
        org=toks[1]
        sib_dic[asn]=org
    return sib_dic


sib_dict=prep_siblings()
##
def check_siblings(a,b):
#   global sib_list
    global sib_dict
    if a not in sib_dict or b not in sib_dict:
        return 0;
#    print a
    return sib_dict[a] == sib_dict[b]

print "Book keeping ended"

##

def find_relation(as1,as2):
    global as_rank 
#    print as1, " ",as2
    if as1 in as_rank and as2 in as_rank[as1]:
        if as_rank[as1][as2]==-1:
            return "p-c"
        else:
            return "p-p"
    if as2 in as_rank and as1 in as_rank[as2]:
        if as_rank[as2][as1]==-1:
            return "c-p"
        else:
            return "p-p"
    return "Missing"      

##
seen_checks={}
def check_further(as1, super_a,prefix):
    global seen_checks  
    strr=str(as1)+" "+str(super_a)+" "+str(prefix)
    try:
        if strr in seen_checks:
            return seen_checks[strr]
    except Exception,e: 
        print str(e)
        print as1,super_a,prefix
        print "strr is: ",strr
    ases_string=" "+str(as1)
    prefix="ed "+prefix
    for line in lines:
        if "removed" not in line and prefix in line and ases_string in line:
#            print line
            asp=line.split('#')[1]
            if str(super_a) in asp:
                #print "Found orig ",lin
                #print as1,super_a,prefix,line
                seen_checks[strr]=1
                return True
    seen_checks[strr]=0
    return False

def check_private_asn(as1):
  if as1 > 64511 and as1 < 65535:
    return 1
  if as1 >= 4200000000 and as1 <= 4294967295:
    return 1
  return 0


transit=0
peers=0
siblings=0
notFound=0
pref=0
cust=0
prov=0
inPath=0
c_chain=0
tot=0
asn_pairs=[]
uniq_suspect=[]
uniqs=[]
uniq_supers={}
uniq_subs={}
moases=0
bad_guys=[]
bad=0
private_asns=0
case_2346=0


ttime=1401623735
day2=ttime+86400
for line in lines:
    if line=="":
        continue
    if "removed" in line:
        continue
    if "23456" in line:
        case_2346+=1       
        continue
    toks=line.split()

    if len(toks) < 7:
        continue
    time=int(toks[-1])
    if time < day2:
        continue
    try:
        super_asn=int(toks[6])
        asn=int(toks[5])
    except:
        asn=int(toks[5])
        super_asn=int(toks[6].split(',')[0])

    arrs=str(super_asn)+" "+str(asn)

#    if super_asn in uniq_supers:
#        uniq_supers[super_asn]+=1
#    else:
#        uniq_supers[super_asn]=1;
#    continue

    if check_private_asn(asn) or check_private_asn(super_asn):
        private_asns+=1
        continue

    moases+=1
    
    """# Now checks for every string
    if arrs in uniqs:
        continue
    uniqs.append(arrs)
    """
    tot+=1
    if check_siblings(super_asn,asn):
        siblings+=1
        out.write(line)
        continue
    rel=find_relation(super_asn,asn)
    if "p-p" in rel:
        peers+=1
        line="ppBAD"+line
        out.write(line)
        continue
    if "c-p" in rel:
        prov+=1
        line="prBAD"+line
        out.write(line)
#        bad_guys.append(arrs)
        continue
    if "p-c" in rel:
        cust+=1
        out.write(line)
        continue
    asp=line.split('#')[1]
    if str(super_asn) in asp:
        inPath+=1
        out.write(line)
        continue
    if super_asn in cc_dict and asn in cc_dict[super_asn]:
        c_chain+=1
        out.write(line)
        continue
    if "Miss" in rel:
        sub_prefix=toks[3]
        if check_further(asn,super_asn,sub_prefix):
            inPath+=1
            out.write(line)
            continue
#        bad_guys.append(arrs)
        notFound+=1
        line="aBAD"+line
        out.write(line)
        """
        if asn in uniq_subs:
            uniq_subs[asn]+=1
        else:
            uniq_subs[asn]=1;
#        print line
        """
        continue
    
out.close()
print "Private ANSs ",private_asns
print "AS23456 case ",case_2346
print "Total moases ", moases
print "Total_unique AS pairs" , tot    
print prov,cust,peers,siblings,notFound,inPath,c_chain
print "Bad :",bad    

##



##

"""
arr=[]
vals=list(uniq_subs.values())


sorted_data=np.sort(vals)
#print sorted[-5:]

for j in sorted_data[-50:]:
    for i in uniq_subs:
#        arr.append(uniq_supers[i])
        if uniq_subs[i]==j:
            print "ASN",i,j
#sorted_x = sorted(uniq_subs.items(), key=operator.itemgetter(1))
#print uniq_subs[]
"""
