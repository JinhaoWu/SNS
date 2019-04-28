import socket
from _thread import *
import threading
from kdd_Prehandle import prehandle
from time import ctime
import pandas as pd
import struct
import sys
from kdd_Prehandle import percent

print_lock = threading.Lock() # define a lock


# define a thread
def threaded(c,addr):
    trans_log = []
    flag = 0
    flag_1 =0
    while (1): # loop for transmitting kdd data
        data = c.recv(1024)
        if not data: # judge whether the transmission is done
            if flag == 2:
                print('kdd data transmission completed')
                print('connection to host: '+str(addr[0]) + ' port: ' + str(addr[1])+' is disconnected')
                print(70 * '-')
                trans_log.append('host: ' + str(addr[0]) + ' port: ' + str(addr[1]) + ' disconnected to server on: ' + ctime())
            else:
                print('The host is disconnected before the transmission is done')
                print(70 * '-')
                trans_log.append('host: ' + str(addr[0]) + ' port: ' + str(addr[1]) + ' abnormally disconnected to server on: ' + ctime())
            print_lock.release()
            break
        trans_log.append('host: '+str(addr[0]) + ' port: ' + str(addr[1]) +data.decode('ascii') + ctime()) # writing server log
        if data == ' requesting kdd training data on: '.encode('ascii'): # judge transmitting training data or testing data
            df = pd.read_csv('kddcup.data_10_percent_corrected.csv')
            print('transmitting kdd training data to host:',addr[0], 'port:', addr[1],'starts on {}'.format(ctime()))
            print('processing....')
        if data == ' requesting kdd test data on: '.encode('ascii'): # judge transmitting training data or testing data
            df = pd.read_csv('corrected.csv')
            print('transmitting kdd test data to host:', addr[0], 'port:', addr[1], 'starts on {}'.format(ctime()))
            print('processing....')

        # packing and transmitting the index of kdd data
        index_str = b''
        for index in df.columns:
            temp = struct.pack('!27s', index.encode('utf-8'))
            index_str += temp
        try:
            c.sendall(index_str)
        except BrokenPipeError:
            print('The host is disconnected before the transmission is done')
            print(70 * '-')
            trans_log.append('host: ' + str(addr[0]) + ' port: ' + str(addr[1]) + ' abnormally disconnected to server on: ' + ctime())
            print_lock.release()
            break


        # packing the kdd data
        index_str = []
        s = []
        for row in range(df.shape[0]):
            s.append(b'')
            index_str.append([])
            for column in range(df.shape[1]):
                index_str[row].append(0.0)
        process_bar = percent(df.shape[0]-1)
        for row in range(df.shape[0]):
            for item in df.iloc[row, :]:
                temp = struct.pack('!f', item)
                s[row] += temp
            process_bar.display_bar()
        print('\nprocessing completed')


        # transmitting the kdd data
        print('transmitting...')
        process_bar = percent(len(s)-1)
        for item in s:
            try:
                c.sendall(item)
                process_bar.display_bar()
            except BrokenPipeError:
                print('\nThe host is disconnected before the transmission is done')
                print(70 * '-')
                trans_log.append('host: ' + str(addr[0]) + ' port: ' + str(addr[1]) + ' abnormally disconnected to server on: ' + ctime())
                print_lock.release()
                flag_1 = 1
                break
        if flag_1 == 1:
            break


        # judge whether the transmission is done
        if flag == 0:
            print('\ntransmitting kdd training data to host:', addr[0], 'port:', addr[1], 'completes on {}'.format(ctime()))
            print(70 * '-')
            try:
                c.sendall((172 * '*').encode('utf-8'))
            except BrokenPipeError:
                print('\nThe host is disconnected before the transmission is done')
                print(70 * '-')
                trans_log.append('host: ' + str(addr[0]) + ' port: ' + str(addr[1]) + ' abnormally disconnected to server on: ' + ctime())
                print_lock.release()
                break
            trans_log.append('host: '+str(addr[0]) + ' port: ' + str(addr[1]) + ' training transmission end on ' + ctime())
            flag = 1
        elif flag == 1:
            print('\ntransmitting kdd test data to host:', addr[0], 'port:', addr[1], 'completes on {}'.format(ctime()))
            print(70 * '-')
            trans_log.append('host: ' + str(addr[0]) + ' port: ' + str(addr[1]) + ' test transmission end on ' + ctime())
            try:
                c.sendall((172 * '!').encode('utf-8'))
            except BrokenPipeError:
                print('\nThe host is disconnected before the transmission is done')
                print(70 * '-')
                trans_log.append('host: ' + str(addr[0]) + ' port: ' + str(addr[1]) + ' abnormally disconnected to server on: ' + ctime())
                print_lock.release()
                break
            flag = 2
    c.close()
    server_log = open('server_log.txt', 'a') # writing in server log
    for log in trans_log:
        server_log.write(log+'\n')
    server_log.close()


# server set-up
def Main():
    host  = 'localhost'
    port = 12345
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    except socket.error as msc :
        print('Error in creating socket: '+str(msc[0])+' Message: '+msc[1])
        sys.exit()
    print('socket created')
    try:
        s.bind((host,port))
    except socket.error as msg:
        print('Bind failed: '+str(msg[0])+' Message: '+msg[1])
        sys.exit()
    print('server address: {}\nsocket binded to port: {}'.format(host,port))
    s.listen(5)
    print('kdd socket is listening')
    print(70 * '-')
    server_log = open('server_log.txt', 'a')
    server_log.write('server started up on: {}'.format(ctime())+'\n')
    server_log.close()
    while (1):
        try:
            c, addr = s.accept()
            server_log = open('server_log.txt', 'a')
            server_log.write('host: ' + str(addr[0]) + ' port: ' + str(addr[1]) + ' connected to server on: ' + ctime()+'\n')
            server_log.close()
        except KeyboardInterrupt:
            print('You closed the server')
            server_log = open('server_log.txt', 'a')
            server_log.write('server shunted down on: {}'.format(ctime()) + '\n')
            server_log.close()
            break
        print_lock.acquire()
        print('Connected to : ',addr[0],':',addr[1])
        print(70 * '-')
        start_new_thread(threaded,(c,addr))
    s.close()

if __name__ == '__main__':
    print('kdd server starts up')
    print(70 * '-')
    print('prehandle training data starts on: {}'.format(ctime()))
    print("prehandling.....")
    prehandle('training')
    print('prehandle training data completed on: {}'.format(ctime()))
    print(70 * '-')
    print('prehandle test data starts on: {}'.format(ctime()))
    print("prehandling.....")
    prehandle('test')
    print('prehandel test data completed on: {}'.format(ctime()))
    print(70 * '-')
    Main()