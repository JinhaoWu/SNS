import pandas as pd
import numpy as np
import csv
import os
import sys

# progress bar
class percent():
    bar_length = 70
    max = 0
    index = 0

    def __init__(self, max):
        self.max = max
    def display_bar(self):
        if self.index % 5000 == 0 or self.index == self.max:
            sys.stdout.write('\r')
            percent =  100 * float(self.index) / float(self.max)
            num_arrow = int(percent / 100 * 70) +1
            num_line = self.bar_length - num_arrow
            bar = '['+'>'* num_arrow + '-'*num_line+']'+'{:.2f}'.format(percent)+'%'
            sys.stdout.write(bar)
            sys.stdout.flush()
        self.index += 1

# global list of label
global label_list
label_list = ['normal.', 'buffer_overflow.', 'loadmodule.', 'perl.', 'neptune.', 'smurf.',
                  'guess_passwd.', 'pod.', 'teardrop.', 'portsweep.', 'ipsweep.', 'land.', 'ftp_write.',
                  'back.', 'imap.', 'satan.', 'phf.', 'nmap.', 'multihop.', 'warezmaster.', 'warezclient.',
                  'spy.', 'rootkit.']

# convert protocol to number
def conv_protocol(sample):
    protocol_list = ['tcp', 'udp', 'icmp']
    if sample[1] in protocol_list:
        return protocol_list.index(sample[1])

# convert service to number
def conv_services(sample):
    services_list = ['aol', 'auth', 'bgp', 'courier', 'csnet_ns', 'ctf', 'daytime', 'discard', 'domain', 'domain_u',
                    'echo', 'eco_i', 'ecr_i', 'efs', 'exec', 'finger', 'ftp', 'ftp_data', 'gopher', 'harvest', 'hostnames',
                    'http', 'http_2784', 'http_443', 'http_8001', 'imap4', 'IRC', 'iso_tsap', 'klogin', 'kshell',
                    'ldap', 'link', 'login', 'mtp', 'name', 'netbios_dgm', 'netbios_ns', 'netbios_ssn', 'netstat', 'nnsp',
                    'nntp', 'ntp_u', 'other', 'pm_dump', 'pop_2', 'pop_3', 'printer', 'private', 'red_i', 'remote_job',
                    'rje', 'shell', 'smtp', 'sql_net', 'ssh', 'sunrpc', 'supdup', 'systat', 'telnet', 'tftp_u', 'tim_i',
                    'time', 'urh_i', 'urp_i', 'uucp', 'uucp_path', 'vmnet', 'whois', 'X11', 'Z39_50','icmp']
    if sample[2] in services_list:
        return services_list.index(sample[2])

# convert flag to number
def conv_flag(sample):
    flag_list =['OTH','REJ','RSTO','RSTOS0','RSTR','S0','S1','S2','S3','SF','SH']
    if sample[3] in flag_list:
        return flag_list.index(sample[3])

# convert label to number
def conv_label(sample):
    if sample[41] in label_list:
        return label_list.index(sample[41])
    else:
        label_list.append(sample[41])
        return label_list.index(sample[41])


# adding categories to each sample
def add_category(type):
    normal = ['normal.']
    DOS = ['apache2.', 'back.','land.', 'mailbomb.', 'neptune.','pod.', 'processtable.','smurf.','teardrop.', 'udpstorm.']
    R2L = ['ftp_write.', 'guess_passwd.','imap.', 'multihop.', 'named.', 'phf.', 'sendmail.', 'snmpgetattack.', 'snmpguess.', 'spy.', 'warezclient.', 'warezmaster.', 'worm.', 'xlock.', 'xsnoop.']
    PROBE = ['ipsweep.', 'mscan.', 'nmap.', 'portsweep.', 'saint.', 'satan.']
    U2R = ['buffer_overflow.', 'httptunnel.', 'loadmodule.', 'perl.', 'ps.', 'rootkit.', 'sqlattack.', 'xterm.']
    catalog_list = [normal, DOS, R2L, PROBE, U2R]
    normal_num=[]
    DOS_num=[]
    R2L_num=[]
    PROBE_num = []
    U2R_numm=[]
    catalog_list_num =[normal_num, DOS_num, R2L_num, PROBE_num, U2R_numm]
    if type == 'training':
        name = 'kddcup.data_10_percent_corrected.csv'
    if type == 'test':
        name = 'corrected.csv'
    for i in range(len(label_list)):
        for ii in catalog_list:
            if label_list[i] in ii:
                catalog_list_num[catalog_list.index(ii)].append(i)
                break
    df = pd.read_csv(name)
    label_list_num = df.loc[:,'label']
    catalog = []
    for label_num in label_list_num:
        if label_num in catalog_list_num[0]:
            catalog.append(0)
            continue
        if label_num in catalog_list_num[1]:
            catalog.append(1)
            continue
        if label_num in catalog_list_num[2]:
            catalog.append(2)
            continue
        if label_num in catalog_list_num[3]:
            catalog.append(3)
            continue
        if label_num in catalog_list_num[4]:
            catalog.append(4)
    df.insert(42, 'catalog', catalog)
    clear_all = open(name, 'w+')
    clear_all.truncate()
    clear_all.close()
    df.to_csv(name, index = False )
    f = open(name,"rb+")
    f.seek(-1 , os.SEEK_END)
    if next(f) == b'\n':
        f.seek(-1 , os.SEEK_END)
        f.truncate()
    f.close()

# pre-handle of data, convert literal features to numbers
def prehandle(type):
    if type == 'training':
        source_file ='kddcup.data_10_percent_corrected'
        data_file = 'kddcup.data_10_percent_corrected.csv'
    if type == 'test':
        source_file ='corrected'
        data_file = 'corrected.csv'
    data_source = open(source_file,'r')
    data_convert = open(data_file,'w',newline='')
    readCSV = csv.reader(data_source)
    writeCSV = csv.writer(data_convert)
    column_names = ["duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes", "land",
                    "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in", "num_compromised",
                    "root_shell", "su_attempted", "num_root", "num_file_creations", "num_shells",
                    "num_access_files", "num_outbound_cmds", "is_host_login", "is_guest_login", "count",
                    "srv_count", "serror_rate", "srv_serror_rate", "rerror_rate", "srv_rerror_rate",
                    "same_srv_rate", "diff_srv_rate", "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count",
                    "dst_host_same_srv_rate", "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
                    "dst_host_srv_diff_host_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate",
                    "dst_host_rerror_rate", "dst_host_srv_rerror_rate", "label"]
    writeCSV.writerow(column_names)
    for row in readCSV:
        temp_row = np.array(row)
        temp_row[1] = conv_protocol(row)
        temp_row[2] = conv_services(row)
        temp_row[3] = conv_flag(row)
        temp_row[41] = conv_label(row)
        writeCSV.writerow(temp_row)
    data_convert.close()
    data_source.close()
    if type == 'training':
        add_category('training')
    if type == 'test':
        add_category('test')



if __name__ == '__main__':
    prehandle('test')
    prehandle('training')
