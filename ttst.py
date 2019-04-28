import socket
import pandas as pd
host  = 'localhost'
port = 12345

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((host, port))
s.listen(5)
c, addr = s.accept()
s =[1,2,3,4,5]

a = pd.read_csv('cellphone.csv')