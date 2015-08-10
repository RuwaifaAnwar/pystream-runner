import numpy as np
import matplotlib.pyplot as plt
file=open("moases_hist.txt","r")
lines=file.readlines()

prev_moas=0
time=0
arr=[]
for line in lines:
    time+=1
    if (time % 20 != 0):
        continue
    moases=int(line)
    diff=moases-prev_moas
    arr.append(diff)
    prev_moas=moases

#newList = np.sort(arr)
#print sorted_data[1000]
#newList = [float(x / 60) for x in sorted_data]
#print max(newList)
##
print arr[1]
##
a_arr=[]
a_arr=np.arange(1,len(arr)*20+1,+20)
a_arr2=np.arange(1,len(arr)+1,1)
print len(a_arr)
plt.plot(a_arr,arr,color='r')
#plt.plot(a_arr2,arr)
print a_arr[0:5]
print arr[0:5]
##
#plt.legend(['SubMoas Detected', 'SubMoas Removed'], loc='upper right')
plt.ylabel('Number of Occurences')
plt.xlabel('Time (Minutes)')
plt.title('Net MOASes added')
plt.yticks(np.arange(-700, max(arr)+1, 200.0))
plt.axis([0,max(a_arr),-800,700])
plt.show()