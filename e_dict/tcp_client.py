from socket import *

#创建套接字
sockfd = socket()   #默认流式套接字

#发起连接
server_addr = ('127.0.0.1',8000)
sockfd.connect(server_addr)

while True:
# 收发信息
    data = input('>>')
    if data == 'q':
        break
    sockfd.send(data.encode())
    if data == 'quit_server':
        break
    data = sockfd.recv(1024)
    print('From server:',data.decode())
#关闭套接字
sockfd.close()
