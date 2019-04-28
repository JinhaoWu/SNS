import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.utils import to_categorical
from keras.optimizers import RMSprop
from sklearn.model_selection import train_test_split
from time import ctime
from sklearn.utils import shuffle
import pandas as pd

# global list of label
global label_list
label_list = ['normal.', 'buffer_overflow.', 'loadmodule.', 'perl.', 'neptune.', 'smurf.',
              'guess_passwd.', 'pod.', 'teardrop.', 'portsweep.', 'ipsweep.', 'land.', 'ftp_write.',
              'back.', 'imap.', 'satan.', 'phf.', 'nmap.', 'multihop.', 'warezmaster.', 'warezclient.',
              'spy.', 'rootkit.']

# convert label to number
def conv_label(sample):
    if sample[41] in label_list:
        return label_list.index(sample[41])
    else:
        label_list.append(sample[41])
        return label_list.index(sample[41])

# convert category to number
def conv_category(sample):
    catalog_list = ['normal', 'DOS', 'R2L', 'PROBE', 'U2R']
    if sample[42] in catalog_list:
        return catalog_list.index(sample[42])

# import kdd data
def import_samples(type,df): # (to run this file along, please delete the input df)
    if type == 'training':
        #name = 'kddcup.data_10_percent_corrected.csv' # (to run this file along, please delete the first comment symbol # )
        print('processing training data starts at {}'.format(ctime()))
        print('processing....')
    if type == 'test':
        #name = 'corrected.csv' # (to run this file along, please delete the first comment symbol # )
        print('processing test data starts at {}'.format(ctime()))
        print('processing....')
    #df = pd.read_csv(name) # (to run this file along, please delete the first comment symbol # )
    df_set = df.values
    avg_list = []
    stad_list = []
    for column in range(df.shape[1] - 2): # calculate mean values of each column
        avg_list.append(df.iloc[:, column].mean())
    for column in range(df.shape[1] - 2): # calculate stad values of each column
        temp = []
        for row in df.iloc[:, column]:
            temp.append(abs(row - avg_list[column]))
        temp_np = np.array(temp)
        stad_list.append(temp_np.mean())
    x = df_set[:, 0:41].astype(float)
    y = df_set[:, 42]
    for column in range(x.shape[1]): # standardization of each column
        if column == 1 or column == 2 or column == 3 or column == 6 or column == 11 or column == 13 or column == 14 or column == 20 or column == 21:
            pass
        elif stad_list[column] == 0:
            pass
        else:
            x[:, column] = (x[:, column] - avg_list[column]) / stad_list[column]
    for column in range(x.shape[1]): # normalization of each column
        if column == 1 or column == 2 or column == 3 or column == 6 or column == 11 or column == 13 or column == 14 or column == 20 or column == 21:
            pass
        elif x[:, column].max() - x[:, column].min() == 0:
            pass
        else:
            x[:, column] = (x[:, column] - x[:, column].min()) / (x[:, column].max() - x[:, column].min())

    one_hot_x_list =[]
    error_line_list =[]
    error = 0
    for i in range(x[:,2].shape[0]): # finding the error rows in testing data correct.csv
        if x[i,2] == 70:
            error_line_list.append(i)
            error = 1
    if error == 1:
        error_line_tup = tuple(error_line_list)
        x = np.delete(x, error_line_tup, axis=0)
        y = np.delete(y, error_line_tup, axis=0)
    column_bias = np.ones(x.shape[0]) # adding bias 1 to data
    one_hot_x_list.append(column_bias)
    for column in range(x.shape[1]): # one-hot coding for discrete features
        if column != 1 and column != 2 and column != 3:
            one_hot_x_list.append(x[:,column])
        else:
            one_hot_x_list.append(to_categorical(x[:,column]))
    for column in range(len(one_hot_x_list)): # creating final kdd data sample
        if column == 0:
            one_hot_x = one_hot_x_list[0]
        else:
            one_hot_x = np.c_[one_hot_x,one_hot_x_list[column]]
    one_hot_y = to_categorical(y) # one-hot coding of labels
    one_hot_x = shuffle(one_hot_x, random_state=5)
    one_hot_y = shuffle(one_hot_y, random_state=5)
    if type == 'training':
        print('processing training data ends at {}'.format(ctime()))
        print(70 * '-')
    if type == 'test':
        print('processing test data ends at {}'.format(ctime()))
        print(70 * '-')
    return one_hot_x, one_hot_y

# neural network set-up
def neu_net(x_train, y_train, x_test, y_test):
    model = Sequential()
    model.add(Dense(16, activation='relu', input_shape=(123,)))
    model.add(Dropout(0.2))
    model.add(Dense(16, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(5, activation='softmax'))
    model.compile(loss='categorical_crossentropy',optimizer = RMSprop(lr = 0.001), metrics = ['accuracy'])
    print("training starts at {}".format(ctime()))
    x_train, x_valid, y_train, y_valid = train_test_split(x_train,y_train,test_size=0.01, random_state= 8)
    history = model.fit(x_train, y_train, batch_size = 24, epochs = 5, verbose = 1, validation_data=(x_valid, y_valid))
    print('training ends at {}'.format(ctime()))
    print(70 * '-')
    print('evaluating starts at {}'.format(ctime()))
    print('evaluating....')
    score = model.evaluate(x_test, y_test, verbose = 0)
    print('evaluating ends at {}'.format(ctime()))
    print(70 * '-')
    predictions = model.predict_classes(x_test)
    return score, predictions

# statistics of labels in kdd data
def label_statis(df):
    label_statistic = {}
    unknown = 0
    for label_num in df['label']:
         if label_num > 22:
             unknown += 1
    for label in label_list:
        temp = [0 for _ in range(41)]
        temp.append(label)
        label_statistic[label] = len(df.loc[df['label'] == conv_label(temp)])
    for key, value in label_statistic.items():
        print(key,':',value)
    if unknown != 0:
        print('unknown attack:', unknown)

# statistics of categories in kdd data
def category_statis(df):
    catalog_statistic = {}
    catalog_list = ['normal', 'DOS', 'R2L', 'PROBE', 'U2R']
    for catalog in catalog_list:
        temp = [0 for _ in range(42)]
        temp.append(catalog)
        catalog_statistic[catalog] = len(df.loc[df['catalog'] == conv_category(temp)])
    for key, value in catalog_statistic.items():
        print(key,':',value)


if __name__ == '__main__':
    x_train, y_train = import_samples('training')
    x_test, y_test = import_samples('test')
    score, predictions, history = neu_net(x_train, y_train, x_test, y_test)
    print('Test loss:', score[0])
    print("Test accuracy:", score[1])
