#encoding = utf-8
'''
此文档为电子辞典客户端
'''
from socket import *
import re
import os,sys
import getpass

class DictClient(object):
    def __init__(self,ADDR):
        self.addr = ADDR
        self.socket = socket()

    def serve_forever(self):
        self.socket.connect(self.addr)
        n = 0
        self.first_UI(n)
        while True:
            n = input('>>')
            n = int(n.strip())
            if n not in [1,2,3]:
                print('您的输入有误,请重新输入')
                continue
            else:
                self.first_UI(n)
            break
    
    def first_UI(self,n):
        while True:
            if n == 0:
                os.system('clear')
                print('=====欢迎使用电子辞典=====')
                print('=======输入1,登录=======')
                print('=======输入2,注册=======')
                print('=======输入3,退出=======')
                n = input('>>')
            elif n == '1':
                self.login()
                n = 0
            elif n == '2':
                self.register()
                n = 0       
            elif n == '3':
                sys.exit('退出电子辞典程序')
            else:
                print('您的输入有误')

    def register(self):
        while True:
            name = input('请输入要注册的用户名')
            name = name.strip()
            regex = re.findall(r'\W+',name)
            if regex:
                print('用户名含有非法字符请重新输入')
                continue
            name = 'R '+name
            self.socket.send(name.encode())
            msg = self.socket.recv(1024).decode()
            if msg == 'ok':
                print('用户名可以使用')
                break
            else:
                print('用户名已存在,请重新输入')
                continue
        while True:
            password1 = getpass.getpass('请输入密码')
            password2 = getpass.getpass('请再次输入密码')
            if password1 == password2:
                password = password2
                break
            else:
                print('两次输入密码不一致')
                continue
        self.socket.send(password.encode())
        while True:
            age = input('请输入年龄')
            if age.isdigit():
                break
            else:
                print('您的输入有误,请重新输入')
        self.socket.send(age.encode())
        while True:
            sex = input('请输入性别(m表男,f表示女)')
            if sex == 'm' or sex == 'f':
                break
            else:
                print('仅允许输入m或f')
        self.socket.send(sex.encode())
        self.second_UI()

    def second_UI(self):
        os.system('clear')
        while True:
            print('=====欢迎使用电子辞典=====')
            print('======输入1,查单词=======')
            print('====输入2,查看历史记录====')
            print('=======输入3,注销========')
            n = input('>>')
            n = n.strip()
            if n == '1':
                self.search()
            elif n == '2':
                self.socket.send('H'.encode())
                self.history()
            elif n == '3':
                self.socket.send('OUT'.encode())
                return
            else:
                print('输入有误,请重新输入')

    def search(self):
        self.socket.send('S'.encode())
        while True:
            word = input('请输入要查询的单词,输入!q退出查询')
            if word == '!q':
                self.socket.send('!q'.encode())
                return
            self.socket.send(word.encode())
            result = self.socket.recv(4096).decode()
            print('单词%s的释义为:' % word,'\n',
                   result,sep = '')

    def history(self):
        data = self.socket.recv(2048).decode()
        print(data)
            
    def login(self):
        while True:
            name = input('请输入您的用户名:')
            name = 'L ' +name.strip()
            self.socket.send(name.encode())
            msg = self.socket.recv(1024).decode()
            if name == 'L !':
                self.register()
                return
            elif name == 'L >':
                sys.exit('退出客户端')
            elif msg != 'ok':
                print('您输入的用户名不存在,请重新输入')
                print(r'输入!号注册,>号退出')
            elif msg == 'ok':
                while True:
                    password = getpass.getpass('请输入密码')
                    self.socket.send(password.encode())
                    msg = self.socket.recv(128).decode()
                    if msg == 'ok':
                        self.second_UI()
                        return
                    else:
                        print('您输入的密码有误')
                        continue
        
            
             


if __name__ == '__main__':
    ADDR = ('127.0.0.1',8000)
    c = DictClient(ADDR)
    c.serve_forever()