import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
#outputs daily numebr of moas detected and removed

fil = open("/home/ruwaifa/Dropbox/test_moas/2test_2months.logs","r") 
lines=fil.readlines()
start_interval=1401623715
change_at=1401623715+3600
det=rem=0
det_a=[]
rem_a=[]    
mean_a=[]
for line in lines:
    toks=line.split()
    time=int(toks[-1])
    if time > change_at:
#        print det,rem
#        det=0
#        rem=0
        while time > change_at:
            change_at+=3600
#            print det,rem,det-rem
            det_a.append(det)   
            rem_a.append(rem)
            mean_a.append(det-rem) 
            det=0
            rem=0
    if "detected" in line:
        det+=1
    if "emoved" in line:
        rem+=1
##        
print np.mean(mean_a[1:])


##
"""
y_arr=np.array(det_a)
y_rem=np.array(rem_a)
y_mean=np.array(mean_a)

a_arr=np.arange(1,len(det_a)+1)
#plt.axis([0,len(y_arr),0,100])
#plt.ylim([-50,100])
plt.plot(a_arr,y_mean)
print np.mean(mean_a)
print (sum(mean_a)/len(mean_a))
plt.ylim([-200,200])
plt.xlim([-5,1000])  

plt.ylabel('Number of Occurences')
plt.xlabel('Time (Hours)')
plt.title('Net MOASes ')

"""
#plot moas detec remov
plt.ylim([0,1000])
plt.xlim([-5,1000])
#plt.plot(a_arr,y_arr)
plt.plot(a_arr,y_arr)
plt.plot(a_arr,y_rem)
plt.legend(['SubMoas Detected', 'SubMoas Removed'], loc='upper right')
plt.ylabel('Number of Occurences')
plt.xlabel('Time (Hours)')
plt.title('SubMoases detected and removed')
"""

plt.show()


"""
