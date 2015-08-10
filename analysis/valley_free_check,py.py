#gets file with violations
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

as_rank={}
with open("as_rel.txt") as file:
    for line in file:
        str1=line.split('|')
        provider=int(str1[0])   
        customer=int(str1[1])   
        relation=int(str1[2])
        if provider not in as_rank:
            as_rank[provider]={}
            as_rank[provider][customer]=relation
        else:
            as_rank[provider][customer]=relation

def find_relation(as1,as2):
    global as_rank 
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


fil = open("full_out_bads_detailed.logs","r") 
#fil = open("2test_2months.logs","r") 
lines=fil.readlines()
voil=0
miss=0
tot=0
clean=0
for line in lines:
#    if line=="" or "BAD" not in line:
    if line=="" or "remo" in line:
        continue
    if "aBAD" not in line:
        continue   
    if "Total" in line:
        break
    toks=line.split()

    if len(toks) < 7:
        continue
    asn=int(toks[5])
#    if asn!=22698:
#        continue
    tot+=1
    try:
        asp=line.split('#')[1]
    except:
        print line
        continue
#        break
    asp=asp.replace("'","").split(',')
#    asp="1126 24785 1273 39792 39792 57756 43239".split()
    path=[]
    for i in range(len(asp)-1,0,-1):
        path.append(find_relation(int(asp[i]),int(asp[i-1])))
    peerd=0
    downhill=0
    violation=0
    missing=0
    for i in path:
#        print i
        if "Missing" in i:
#            violation=1
            missing=1
            break
        #break
#            print "violation 0"
        if "p-c" in i:
            downhill=1
        if "p-p" in i:
            if peerd:
#                print "violation1"
                violation=1
            peerd=1
            if downhill:
#                print "violation2"
                violation=1
        if "c-p" in i:
            if peerd ==1 or downhill==1:
#                print "violation3"
                violation=1
    if violation:
        voil+=1
    if missing:
        miss+=1
    if violation==0 and missing==0:
        clean+=1
    #    break
#        break
    #break
print "Violations ",voil
print "Miss: ",miss
print "Clean: ",clean
print "Total: ",tot