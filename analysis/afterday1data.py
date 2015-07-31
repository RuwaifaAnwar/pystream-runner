fil = open("2test_2months.logs","r") 
lines=fil.readlines()

out = open("afterday.log","a") 

ttime=1401623735
day2=ttime+86400
for line in lines:
    toks=line.split()
    if len(toks) < 7:
        continue
    time=int(toks[-1])
    if time > day2:
         out.write(line)
out.close()
