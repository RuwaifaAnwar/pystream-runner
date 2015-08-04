from __future__ import division
fil=open("prefix_feq_all.txt","r")
lines=fil.readlines()
tot=0
for line in lines:
    toks=line.split()
    tot+=int(toks[0])

for line in lines:
    toks=line.split()
    freq=(int(toks[0])/tot)*100
    print toks[1],freq
