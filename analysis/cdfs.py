from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt

fil = open("/home/ruwaifa/Dropbox/test_moas/pystream-runner/analysis/time_durations.txt","r") 
lines=fil.readlines()

arr=[]
for line in lines:
    arr.append(int(line))
    
##    
sorted_data = np.sort(arr)
print sorted_data[1000]
newList = [float(x / 60) for x in sorted_data]
print max(newList)
##

yvals=np.arange(len(newList))/float(len(newList ))

plt.plot(sorted_data,yvals)
plt.axis([0,107789,0,1])
plt.ylabel('CDF')
plt.xlabel('Percentage visibility of highest ASN')
plt.title('CDF showing skewness in MOAS visibility')
plt.show()