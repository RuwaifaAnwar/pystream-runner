import numpy as np
import matplotlib.pyplot as plt
from pylab import legend
fil = open("/home/ruwaifa/Dropbox/test_moas/pystream-runner/analysis/window_1w_full_out_bads_detailed.logs","r") 
lines=fil.readlines()
arr1w=[]
prev=0
for line in lines:
    toks=line.split()
    change=int(toks[-1]) - prev
    #print prev, int(toks[-1]), change
    prev=int(toks[-1])
    
    arr1w.append(change)
## 
fil = open("/home/ruwaifa/Dropbox/test_moas/pystream-runner/analysis/window_2w_full_out_bads_detailed.logs","r") 
lines=fil.readlines()
prev=0
arr2w=[]
for line in lines:
    toks=line.split()
    change=int(toks[-1]) - prev
    prev=int(toks[-1])
    arr2w.append(change)


fil = open("/home/ruwaifa/Dropbox/test_moas/pystream-runner/analysis/window_3w_full_out_bads_detailed.logs","r") 
lines=fil.readlines()
prev=0
arr3w=[]
for line in lines:
    toks=line.split()
    change=int(toks[-1]) - prev
    prev=int(toks[-1])
    arr3w.append(change)

fil = open("/home/ruwaifa/Dropbox/test_moas/pystream-runner/analysis/window_unlimit_full_out_bads_detailed.logs","r") 
lines=fil.readlines()
prev=0
arruw=[]
for line in lines:
    toks=line.split()
    change=int(toks[-1]) - prev
    prev=int(toks[-1])
    arruw.append(change)
##    
a_arr1=np.arange(1,len(arr1w)*30+1,+30)
a_arr=[x/60 for x in a_arr1]
plt.plot(a_arr,arr1w)
#plt.plot(a_arr,arr2w)
#plt.plot(a_arr,arr3w)
#plt.plot(a_arr,arruw)
plt.ylim([-30,30])
#plt.legend(['Window size = 7 days', 'Window size = 14 days','Window size = 21 days','Infinite window'], loc='upper left')
#plt.yticks(np.arange(0, max(arruw)+1, 500.0))
plt.xlabel('Time (minutes)')
plt.ylabel('Change in subMOAS entries inside window')
plt.title('Number of elements in the window for different window sizes')
#plt.legend(frameon=False)

plt.show()