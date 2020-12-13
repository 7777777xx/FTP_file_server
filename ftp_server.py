"""

FTP文件服务器 服务端
多线程 tcp 并发

"""
import os
from socket import *
from threading import Thread
from time import sleep

# 全局变量定义地址
HOST = "0.0.0.0"
PORT = 7777
ADDR = (HOST, PORT)

# 文件库位置
FTP = "D:\\MyProjects\\FTP_File_Server\\FTP\\"


# 具体处理客户端请求
class FtpServer(Thread):
    def __init__(self, connfd):
        self.connfd = connfd
        super().__init__()

    # 处理请求文件列表
    def do_list(self):
        # 判断文件库是否为空
        files = os.listdir(FTP)
        if not files:
            self.connfd.send(b"FAIL")  # 失败
        else:
            self.connfd.send(b"OK")
            sleep(0.1)
            data = "\n".join(files)
            self.connfd.send(data.encode())
            sleep(0.1)
            self.connfd.send(b"##")

    # 处理下载文件
    def do_get(self, filename):
        try:
            f = open(FTP + filename, 'rb')
        except:
            # 文件不存在
            self.connfd.send(b"FAIL")
        else:
            self.connfd.send(b"OK")
            sleep(0.1)
            # 发送文件
            while True:
                data = f.read(1024)
                if not data:
                    break
                self.connfd.send(data)
            sleep(0.1)
            self.connfd.send(b"##")
            f.close()

    # 处理上传文件、
    def do_put(self, filename):
        # 判断文件是否存在
        if os.path.exists(FTP + filename):
            self.connfd.send(b"FAIL")
        else:
            self.connfd.send(b"OK")
            # 接收文件
            f = open(FTP + filename, 'wb')
            while True:
                data = self.connfd.recv(1024)
                if data == b"##":
                    break
                f.write(data)
            f.close()

    # 线程启动方法
    def run(self):
        while True:
            # 接受某一个类请求
            data = self.connfd.recv(1024).decode()
            print(data)
            if not data or data == "EXIT":
                break
            elif data == "LIST":
                self.do_list()
            elif data == "GET":
                self.do_get()
            elif data[:4] == "RETR":
                filename = data.split(' ')[-1]
                self.do_get(filename)
            elif data[:4] == "STOR":
                filename = data.split(' ')[-1]
                self.do_put(filename)

        self.connfd.close()


# 在函数中搭建并发结构
def main():
    # 创建tcp套接字
    sock = socket()
    sock.bind(ADDR)
    sock.listen(5)

    print("Listen the port %d..." % PORT)
    while True:
        # 循环接收端连接
        try:
            connfd, addr = sock.accept()
            print("Connect from", addr)
        except KeyboardInterrupt:
            sock.close()
            return

        # 使用自定义线程类为连接的客户端创建新线程
        t = FtpServer(connfd)
        # 客户端随服务端退出
        t.setDaemon(True)
        t.start()


if __name__ == '__main__':
    main()
