import pyasn
import glob
import os
import datetime
import gzip
import json
import ipaddress

path_tr_files="/scratch/ruwaifa/submoas/"
path_susp_folder="/data/routing/submoas/"
out=open("final.txt","w")
log_dict={}
start_from=1461626264

asndb = pyasn.pyasn('ipasn_20150224.dat')

print asndb.lookup('10.0.0.2')

def get_susp_dict(file_path):
	global log_dict
	with gzip.open(file_path, 'rb') as f:
	    for line in f:
	    	if "#" in line:
	    		continue
	    	toks=line.split("|")
	    	log_dict[toks[0]]=toks[3:5]

def process_tr_hops(hops,event_id,dst_pfx,line):
	decision=0
	#print "start"
	try:
		origins=log_dict[event_id]

	except:
		print "ERR not found"

	keys=sorted(hops, key=lambda x:int(x))
	h=[hops[x] for x in keys]
	aspath=""
	last_ip=""
	superasn_found=0
	subasn_found=0
	last_resolved_asn=""
	last_hop_not_origin=0
	asn="asn"
	for hop in h:
		#print hop
		if len(hop["addr"]):
			last_ip=hop["addr"]
			asn=str(asndb.lookup(hop["addr"])[0])
			
			if asn.isdigit():
				last_resolved_asn=asn
				aspath=aspath+" "+ asn

				if superasn_found ==0 and subasn_found==0:
					if asn in origins[0]:
							superasn_found=1
							decision=1
					if asn in origins[1]:
							subasn_found=1
							decision=3
				else:
					if asn in origins[0] and subasn_found:
						decision=4
						#superfound after sub
					if asn in origins[1] and superasn_found:
						decision="inter"
						#subasn found after super

	try:
		is_same_network=ipaddress.ip_address(last_ip) in ipaddress.ip_network(dst_pfx)
	except Exception,e:
		is_same_network=1
		#print line
		#print str(e)
		#exit()
	if decision > 0 and str(last_resolved_asn) not in origins:
		last_hop_not_origin=1 

	printable=aspath+"| "+str(origins[0])+"|"+str(origins[1])+"|"+str(decision)+"|"+str(is_same_network)+"|"+str(last_hop_not_origin)
	"""
	print printable
	print "origins",origins
	print "LS",last_resolved_asn
	print last_ip
	print dst_pfx
	exit()
	"""
	return printable

for tr_file in os.listdir(path_tr_files):
	timestamp=int(tr_file.split(".")[1])
	if timestamp < start_from:
		continue
	print tr_file
	susp_file=tr_file.replace("trace_ripe","log")
	print timestamp
	date_f=datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
	print date_f
	susp_file_path=path_susp_folder+date_f+"/"+susp_file
	get_susp_dict(susp_file_path)
	printable=""
	with gzip.open(path_tr_files+tr_file, 'rb') as f:
	    for line in f:
	    	tr=json.loads(line)
	    	res=process_tr_hops(tr["hops"],tr["event_id"], tr["dst_pfx"],line)
	    	# printable=tr["event_id"]+"|"+tr["dst_pfx"]+"|"+tr["m_id"]
	    	printable=tr["event_id"]+"|"+tr["dst_pfx"]+"|"+str(tr["m_id"])+"|"+res+"\n"
	    	out.write(printable)
#	    	print printable
	#exit()
out.close()

