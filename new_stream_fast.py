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
stream.set_data_interface('mysql')
stream.set_data_interface_option('mysql', 'db-host', 'loki-ge')
stream.set_data_interface_option('mysql', 'db-port', '3306')
stream.set_data_interface_option('mysql', 'db-user', 'bgpstream')
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
out = open("2test_2months.logs","a")
##########################################
class Sub_moas():
  def __init__(self,prefix,start,sp_asn,sb_asn,super_p):
    self.start=start
    self.prefix=prefix
    self.end=-1
    self.superasn=sp_asn
    self.subasn=sb_asn
    self.super_prefix=super_p
p_tree = radix.Radix()
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

# build dicts for super_prefixes, so that when a super prefix is removed, it's correspoding sub prefixes are removed
def add_to_super_pref(sub, super_p):
    global super_pref
    if super_p in super_pref:
      super_pref[super_p][sub]=1
    else:
      super_pref[super_p]={}
      super_pref[super_p][sub]=1

def add_to_tree(prefix, orig_as, diag,ases,time):
    global p_tree, sub_prf, moases, out
    match=p_tree.search_best(prefix)
    if (match and prefix not in match.prefix):
        if orig_as not in match.data["asns"] and diag:
            sub_prf+=1
            printable= "Sub prefix detected "+ prefix+" "+match.prefix+" "+str(orig_as)+ " "+str(match.data["asns"])[1:-1]+"# "+str(ases)[1:-1]+" bgptime "+str(time)+"\n"
            out.write(printable)
            add_to_super_pref(prefix,match.prefix)
            sm=Sub_moas(prefix,time,match.data["asns"][0],orig_as,match.prefix);
            moases[prefix]=sm
    node=p_tree.search_exact(prefix)
    if (node):
        if orig_as not in node.data["asns"]:
            node.data["asns"].append(orig_as)
    else:
        new_node=p_tree.add(prefix)
        p_tree.add(prefix)
        new_node.data["asns"] = []
        new_node.data["asns"].append(orig_as)

#For every removed prefix from rib, looks for sub_moases that can be removed
def remove_sub_moas(prefix,time):
    global moases, out, super_pref
    if(prefix in moases):
        node = moases.get(prefix)
        start= node.start
        del moases[prefix]
        del super_pref[node.super_prefix][prefix]
        printable= "Sub moas removed  "+prefix+" Lasted for "+str(time-start)+" [Sub][Sup] "+str(node.subasn)+" "+str(node.superasn)+" bgptime "+str(time)+"\n"
        out.write(printable)
        #Node to be removed was moas, so all it's submoases now belong to it's super_prefix
        if node.super_prefix in super_pref:
          #Changing ownerships
          if prefix in super_pref:
            for i in super_pref[prefix]:
              super_pref[node.super_prefix].append(i)
              moases[i].super_prefix=node.super_prefix
            del super_pref[prefix]
        else:
          print "ERR super_prefix not found in super_prefix dic"
          sys.stdout.flush()
        
        #when prefix removed wasn't a submoas itself. All it's subprefix are no longer a moas  
    if prefix in super_pref:
      for i in super_pref[prefix]:
        if i in moases:
          node=moases.get(i)
          start=node.start
          del moases[i]
          printable= "Sub moas removed2  "+i+" Lasted for "+str(time-start)+" [Sub][Sup] "+str(node.subasn)+" "+str(node.superasn)+" bgptime "+str(time)+"\n"
          out.write(printable)
        else:
          print "ERR not found in moas"
      del super_pref[prefix]               
############################################################33
prefx_dic ={}
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
                    del pref_as[prefix][p_id]
                    if (len(pref_as[prefix])==0 and p_tree.search_exact(prefix) != None ):
                        p_tree.delete(prefix);
                        remove_sub_moas(prefix,elem.time);
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
        else:
#            new=0 # only check for new prefixes
            for ids in pref_as[prefix]:
                if pref_as[prefix][ids]==orig_as:
                    new=0

            if p_id in pref_as[prefix]:               
                pref_as[prefix][p_id]=orig_as
                
            else:
                pref_as[prefix][p_id]={}
                pref_as[prefix][p_id]=orig_as
        elem_cnt +=1
        if new and first_block:
            add_to_tree(prefix,orig_as,1,ases,elem.time)
        if (create_new):
            out.flush()
            first_block=1
            p_tree = radix.Radix()
            print "New Tree: Sub_prf= ",len(moases)," time: ",elem.time
            sys.stdout.flush()
            for prefix in pref_as:
                for peer_ids in pref_as[prefix]:
                    add_to_tree(prefix,pref_as[prefix][peer_ids],0,ases,elem.time)
            create_new=0        

        elem = rec.get_next_elem()
        continue     

print "Done"
print elem_cnt
print sub_prf
print "err ", err_cnt
out.close()
