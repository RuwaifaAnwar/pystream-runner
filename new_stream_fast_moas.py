# 2ZZplease run the following command in your
# enviroment (or make it part of your bash
# profile) before using pybgpstream
# export LD_LIBRARY_PATH="/usr/local/pkg/ioda-tools/lib:$LD_LIBRARY_PATH"

# this tutorial is not complete, please
# refer to this page for a complete documentation
#
# https://staff.caida.org/~alistair/pybgpstream/index.html


from _pybgpstream import BGPStream, BGPRecord, BGPElem
import radix
import sys
import calendar
import time

stream = BGPStream()
rec = BGPRecord()
start_interval= 1401623715
##stream.add_filter('project', 'ris')
stream.add_filter('collector', 'route-views2')
#stream.add_filter('collector', 'rrc04')
stream.add_filter('record-type', 'ribs')
stream.add_filter('record-type', 'updates')
stream.add_interval_filter(start_interval,1406894115 )
stream.add_rib_period_filter(172800)
stream.set_data_interface('broker')
#stream.set_data_interface_option('broker', 'db-host', 'loki-ge')
#stream.set_data_interface_option('broker', 'db-port', '3306')
#stream.set_data_interface_option('broker', 'db-user', 'bgpstream')
print "start bgpstream"
stream.start()

# signature {collector}{ip}{asn} -> id
info_id = {}
# id peer ASN (for right analysis)
id_ASN = {}
# id signature (for charthouse)
id_sig = {}

# last id assigned
last_id = -1

sub_prf=0
moases={}
super_pref={}  #stores super_prefixes for Moases
out = open("normal_moas.logs","a")
##########################################
def get_peer_id(col, ip, asn):
    global info_id
    global last_id
    global id_sig
    global id_ASN
    if col not in info_id:
        info_id[col] = {}
    if ip not in info_id[col]:
        info_id[col][ip] = {}
    if asn not in info_id[col][ip]:
        last_id = last_id + 1
        info_id[col][ip][asn] = last_id
    peer_id = info_id[col][ip][asn]
    id_sig[peer_id] = col.replace(".","-") + ".AS." + str(asn) + ".__IP_" + ip.replace(".","-")
    id_ASN[peer_id] = str(asn)
    # print peer_id, id_sig[peer_id]
    return peer_id
###########################################################33
prefx_dic ={}
moas_table={}
record_cnt = 0
elem_cnt = 0
err_cnt=0
first_block=0
create_new=0
first_time=0
init_time_set=0
size_init_time=0
size_print_thres=7200;
pref_as = {}
pref_history={}
print "Start at: ",start_interval
threshold=3 # 3 seconds given to set it
sys.stdout.flush()
ecc=0
while(stream.get_next_record(rec)):
#    print "s"
    record_cnt += 1
    elem = rec.get_next_elem()
    while(elem):
#        print "### size of Rib: ",len(pref_as),"# size of Moases: ",len(moases),"##"
        if(elem.type != 'R' and elem.type != 'A'and elem.type!='W'):
            elem = rec.get_next_elem()
            continue
        if(not init_time_set):
            init_time_set=elem.time
        if(elem.time - init_time_set > threshold):
            init_time_set=elem.time
            create_new=1
            threshold=172800 #rebuild tree aftre two days
        #prints every new seconds
#        if(elem.time !=size_init_time):
#            size_init_time=elem.time
#            print elem.time
#            sys.stdout.flush()    
        prefix = str(elem.fields['prefix'])

        if ("0.0.0.0/0" in prefix):
            elem = rec.get_next_elem()
            continue
        p_id=get_peer_id(rec.collector,elem.peer_address,elem.peer_asn)
        if(elem.type =='W'):
            if prefix in pref_as:
                if p_id  in pref_as[prefix]:
                    orig_as=pref_as[prefix][p_id] 
                    del pref_as[prefix][p_id]
                    moas_table[prefix][orig_as]+=-1
                    if ( len(moas_table[prefix]) > 1 and moas_table[prefix][orig_as] < 1  ):
                        print "Removed"
                        del moas_table[prefix][orig_as]
                        printable="Moas removed Prefix "+prefix+" as_removed "+str(orig_as)+" others:"
                        for asn in moas_table[prefix].keys():
                           printable=printable+" "+str(asn)+":"+str(moas_table[prefix][asn])
                        printable=printable+" "+str(elem.time)+"\n"
                        out.write(printable)
                    elif (moas_table[prefix][orig_as] < 1):
                        del moas_table[prefix][orig_as]
            elem=rec.get_next_elem()
            continue       
        
        path = elem.fields['as-path']
        if "{" in path:
            elem = rec.get_next_elem()
            continue

        ases = path.split(" ")
        try:
            orig_as = int(ases[-1])
        except:
            elem=rec.get_next_elem()
            err_cnt+=1
            continue
        new=1
        
        if prefix not in pref_as:
            pref_as[prefix]={}
            pref_as[prefix][p_id]=orig_as        
            moas_table[prefix]={}
            moas_table[prefix][orig_as]=1
            print "Added for",orig_as,"for pref",prefix
        else:
            if p_id in pref_as[prefix]: # peerid seen before               
                pref_as[prefix][p_id]=orig_as
                if orig_as not in moas_table[prefix]: #rare case when peerid changes orig without prior withdrawal
                    printable= "Moas Detected2 "+prefix+" new "+str(orig_as)+" old "
                    for asn in moas_table[prefix]:
                        printable=printable+" "+str(asn)+":"+str(moas_table[prefix][asn])
                    printable=printable+" "+str(elem.time)+"\n"
                    out.write(printable)
                    moas_table[prefix][orig_as]=1
#                else:
#                    moas_table[prefix][orig_as]+=1
               
            else: #new peer id seen
                pref_as[prefix][p_id]={}
                pref_as[prefix][p_id]=orig_as

                if not (orig_as in moas_table[prefix]):# moas detected, new peer id, new orig asn

                    moas_table[prefix][orig_as]=1
                    printable= "Moas Detected "+prefix+" new "+str(orig_as)+" old "
                    print "MOAS ", orig_as
                    for asn in moas_table[prefix]:
                        print "old",asn,
                        if asn == orig_as:
                            print "Match"
                        else:
                            print "No"
                        printable=printable+" "+str(asn)+":"+str(moas_table[prefix][asn])
                    printable=printable+" "+str(elem.time)+"\n"
                    out.write(printable)
                    moas_table[prefix][orig_as]=1
                    ecc=1
                    break
#
                else:
                    moas_table[prefix][orig_as]+=1
        elem = rec.get_next_elem()
        continue     
    if ecc:
        break
print "Done"
print elem_cnt
print sub_prf
print "err ", err_cnt
out.close()





