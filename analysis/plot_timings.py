import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt('/home/ruwaifa/Dropbox/test_moas/pystream-runner/analysis/ind_times')

newList = np.sort(data)
yvals=np.arange(len(newList))/float(len(newList ))
plt.plot(newList,yvals)
plt.axis([2,1000,0,1])
plt.ylabel('CDF')
plt.xlabel('Time durations (seconds)')
plt.title('SubMoas durations for verified hijacks')

plt.show()