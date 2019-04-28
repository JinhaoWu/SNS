import socket
import pandas
from time import ctime
import struct
import kdd_handle
import sys
from kdd_handle import label_statis
from kdd_handle import category_statis
'testing testing'
# host set-up
def Main():
    host = '127.0.0.1'
    port = 12345
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msc:
        print('Error in creating socket: '+str(msc[0])+' Message: '+msc[1])
        sys.exit()
    print('socket created')
    print(70 * '-')
    try:
        s.connect((host,port))
    except socket.gaierror as msg:
        print('Fail to connect to server: '+str(msg[0])+' Message: '+msg[1])
        sys.exit()
    except ConnectionRefusedError:
        print('The connection is refused')
        sys.exit()


    row_training = []
    row_test = []
    flag_1 = 0
    flag_2 = 0
    while (1): # loop for receiving kdd data
        if flag_1 == 0:
            message_1 = ' requesting kdd training data on: '
            print('requesting kdd training data from kdd data server starts on:',ctime())
            print('waiting for response.....')
            try:
                s.sendall(message_1.encode('ascii'))
            except BrokenPipeError:
                print('The server is disconnected')
                sys.exit()
        if flag_1 == 1: # sending starting message
            message_2 = ' requesting kdd test data on: '
            print('requesting kdd test data from kdd data server on:', ctime())
            print('waiting for response.....')
            try:
                s.sendall(message_2.encode('ascii'))
            except BrokenPipeError:
                print('The server is disconnected')
                sys.exit()
        if flag_2 == 0:
            try:
                data = s.recv(1161,socket.MSG_WAITALL) # receiving index of kdd data
            except KeyboardInterrupt:
                print('You closed the host')
                sys.exit()
            print('transmitting....')
        else:
            try:
                data = s.recv(172,socket.MSG_WAITALL) # receiving kdd data
            except KeyboardInterrupt:
                print('You closed the host')
                sys.exit()
        if data == (172 * '!').encode('utf-8'): # judge whether the transmission of testing data is done
            print('requesting kdd test data from kdd data server ends on:', ctime())
            print('transmission completed')
            print(70 * '-')
            break
        if data == (172 * '*').encode('utf-8'): # judge whether the transmission of training data is done
            flag_1 = 1
            flag_2 = 0
            print('requesting kdd training data from kdd data server ends on:', ctime())
            print(70 * '-')
            continue
        if (flag_1 == 0 and flag_2 == 0) or (flag_1 == 1 and flag_2 == 0): # unpack index row
            index_row = []
            for index in range(27, len(data)+27, 27):
                index_row.append(struct.unpack('!27s', data[index - 27:index])[0])
            for i in index_row:
                index = index_row.index(i)
                i = i.rstrip('\x00'.encode('utf-8'))
                index_row[index] = i.decode('utf-8')
            if flag_1 == 0:
                row_training.append(index_row)
                flag_1 =2
                flag_2 = 1
                continue
            if flag_1 == 1:
                row_test.append(index_row)
                flag_1 = 3
                flag_2 =1
                continue
        if (flag_1 == 2 and flag_2 == 1) or (flag_1 == 3 and flag_2 == 1): # unpack data row
            row_data = []
            for index in range(4, len(data)+4, 4):
                row_data.append(struct.unpack('!f', data[index - 4:index])[0])
            if flag_1 == 2:
                row_training.append(row_data)
            if flag_1 == 3:
                row_test.append(row_data)
    s.close()
    print('connection to server is disconnected')
    print(70 * '-')
    return row_training, row_test

# convert received kdd data to Pandas DataFrame
def convert_to_DataFrame(nest_list):
    index = nest_list.pop(0)
    df = pandas.DataFrame(data = nest_list,columns = index)
    return df


if __name__ == '__main__':
    training, test = Main()
    df_training = convert_to_DataFrame(training)
    df_test = convert_to_DataFrame(test)  # import kdd data
    x_train, y_train = kdd_handle.import_samples('training',df_training)
    x_test, y_test = kdd_handle.import_samples('test',df_test) # deeping learning start
    score, predictions = kdd_handle.neu_net(x_train, y_train, x_test, y_test) # obtain evaluation results and predicted classification
    print('The statistics of training data:')
    label_statis(df_training) # statistics of labels in training data
    print(35*'-')
    category_statis(df_training) # statistics of categories in training data
    print(70*'-')
    print('The statistics of test data:')
    label_statis(df_test) # statistics of labels in testing data
    print(35 * '-')
    category_statis(df_test) # statistics of categories in testing data
    print(70 * '-')
    print('The statistics of predicted data:')
    predict_df = pandas.DataFrame(data = predictions, columns = ['catalog']) # convert predicted data to DataFrame
    category_statis(predict_df) # statistics of categories in testing data
    print('Test loss:', score[0])
    print("Test accuracy:", score[1])
