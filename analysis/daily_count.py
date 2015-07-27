#outputs daily numebr of moas detected and removed

fil=open("2test_2months.logs","r")
lines=fil.readlines()
start_interval=1401623715
change_at=1401623715+3600
det=rem=0
for line in lines:
    toks=line.split()
    time=int(toks[-1])
    if time > change_at:
#        print det,rem
#        det=0
#        rem=0
        while time > change_at:
            change_at+=3600
            print det,rem,det-rem    
            det=0
            rem=0
    if "detected" in line:
        det+=1
    if "emoved" in line:
        rem+=1

