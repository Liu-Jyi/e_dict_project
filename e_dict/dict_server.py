#encoding = utf-8
'''
此文档为电子辞典服务端
'''

from socket import *
from threading import Thread
import pymysql
import sys
from hashlib import sha1

class DictServer(object):
    def __init__(self,ADDR):
        self.addr = ADDR
        self.ip = ADDR[0]
        self.port = ADDR[1]
        self.create_socket()
        self.connect_mysql()
    
    def connect_mysql(self):
        # print('运行connect_mysql')
        self.db = pymysql.connect(host = 'localhost',
                                  user = 'root',
                                  password = '123456',
                                  database = 'e_dict',
                                  charset = 'utf8')
        self.cursor = self.db.cursor()
    
    def register_mysql(self,name,connfd):
        # print('运行register_mysql')

        fd = 'select * from user where name = %s'
        self.cursor.execute(fd,[name])
        data = self.cursor.fetchall()
        if not data:
            connfd.send('ok'.encode())
        else:
            connfd.send('error'.encode())
            return
        try:
            password = connfd.recv(1024).decode()
            s1 = sha1()
            s1.update(password.encode('utf8'))
            pwd = str(s1.hexdigest())
            age = connfd.recv(1024).decode()
            sex = connfd.recv(1024).decode()
            fd = 'insert into user(name,password,age,sex) values (%s,%s,%s,%s)' 
            self.cursor.execute(fd,[name,pwd,age,sex])
            self.db.commit()
        except Exception as e:
            print(e)
            self.db.rollback()
        self.login_mysql(name,connfd,pwd = password)
    
    def login_mysql(self,name,connfd,pwd = None):
        # print('运行login_mysql')
        
        fd = 'select * from user where name = %s'
        self.cursor.execute(fd,[name])
        data = self.cursor.fetchall()
        if data and (pwd is None):
            connfd.send('ok'.encode())
        elif pwd:
            pass
        else:
            connfd.send('error'.encode())
            return
        while True:
            if pwd is None:
                pwd = connfd.recv(128).decode()
                s1 = sha1()
                s1.update(pwd.encode('utf8'))
                pwd = str(s1.hexdigest())
                fd = 'select * from user where name = %s and password = %s'
                data = self.cursor.execute(fd,[name,pwd])
                if data:
                    connfd.send('ok'.encode())
                    break
                else:
                    connfd.send('error'.encode())
                    continue
            break
        self.s_handle(connfd,name)

    def s_handle(self,connfd,name):
        # print('s_handle')
        
        while True:
            request = connfd.recv(128).decode()
            if request == 'S':
                self.search_mysql(connfd,name)
            elif request == 'H':
                self.history_mysql(connfd,name)
            elif request == 'OUT':
                return

    def history_mysql(self,connfd,name):
        # print('运行history_mysql')
        i = True
        fd = 'select word,time from history where name = %s limit 10'
        self.cursor.execute(fd,[name])
        inf = ''
        while True:
            try:
                data = self.cursor.fetchone()
                word = str(data[0])
                dt = data[1].strftime('%Y-%m-%d %H:%M:%S')
                data = '%-20s' % word + '   ' + dt + '\n'
                inf += data
                i = False
            except Exception as e:
                if i:
                    connfd.send('暂无历史记录\n'.encode())
                break
        connfd.send(inf.encode())
        
    def search_mysql(self,connfd,name):
        # print('运行search_mysql')

        while True:
            word = connfd.recv(128).decode()
            if word == '!q':
                return
            fd = 'select statement from dictionary where word = %s'
            self.cursor.execute(fd,[word])
            try:
                data = self.cursor.fetchone()[0]
                data += '\n'
                connfd.send(data.encode())
                self.insert_mysql(name,word)
            except:
                connfd.send('未查找到该单词\n'.encode())

    def insert_mysql(self,name,word):
        # print('运行connect_mysql')

        try:
            ins = 'insert into history(name,word) values (%s,%s)'
            self.cursor.execute(ins,[name,word])
            self.db.commit()
        except Exception as e:
            print(e)
            self.db.rollback()
            
    def create_socket(self):
        self.socket = socket()
        self.socket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        self.socket.bind(self.addr)

    def serve_forever(self):
        self.socket.listen(5)
        print('Listen to the port:',self.port)
        while True:
            try:
                connfd,addr = self.socket.accept()
                print('Connect :',addr)
            except KeyboardInterrupt:
                self.socket.close()
                sys.exit('服务器退出')
            except Exception as e:
                print('Error:',e)
                continue
            
            #创建线程处理客户端请求
            clientThread = Thread(target=self.f_handle,args=(connfd,))
            clientThread.setDaemon(True)
            clientThread.start()
 
    def f_handle(self,connfd):
        # print('运行f_handle')

        while True:
            request = connfd.recv(128).decode()
            if not request:
                sys.exit('客户端退出')
            request = request.split(' ')
            if request[0] == 'L':
                self.login_mysql(request[1],connfd)
            elif request[0] == 'R':
                self.register_mysql(request[1],connfd)
                continue



if __name__ == '__main__':
    ADDR = ('0.0.0.0',8000)
    ds = DictServer(ADDR)
    ds.serve_forever()