#!/bin/env python3
import socket
import json

class connectionManager:
    def __init__(self, lisPort):
        self.BUFFSIZE = 8
        self.LISPORT = lisPort
        self.serveraddr = '127.0.0.1'
        self.listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listenSock.bind((self.serveraddr, self.LISPORT))
        # self.connectSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False


    def f(self, callback):
        data = self.recvData(callback)
        self.sendResponse(data)

    def g(self, callback, addr, port):
        data = callback()
        # if not self.connected:
        self.conncect(addr, port)
        self.sendData(data)
        r = self.recvResponse()
        self.connectSock.shutdown(socket.SHUT_RDWR)
        self.connectSock.close
        return r

    def recvData(self, callback):
        self.listenSock.listen(10)
        self.conn, self.addr = self.listenSock.accept()
        fullData = ''
        data = self.conn.recv(self.BUFFSIZE)
        fullData += data.decode('utf-8')
        if bytes('\0'.encode('utf-8')) not in data[:self.BUFFSIZE]:
            while True:
                data = self.conn.recv(self.BUFFSIZE)
                fullData += data.decode('utf-8')
                if bytes('\0'.encode('utf-8')) in data:
                    break
        fullData = json.loads(fullData[:-1])
        return callback(fullData, self.addr)

    def sendResponse(self, data):
        data = json.dumps(data)
        data += '\0'
        self.conn.send(bytes(data[: self.BUFFSIZE].encode('utf-8')))
        n = self.BUFFSIZE
        if '\0' not in data[: self.BUFFSIZE]:
            while True:
                self.conn.send(bytes(data[n : n + self.BUFFSIZE].encode('utf-8')))
                n += self.BUFFSIZE
                if '\0' in data[n : n + self.BUFFSIZE]:
                    self.conn.send(bytes(data[n : len(data)].encode('utf-8')))
                    break

    def sendData(self, data):
        data = json.dumps(data)
        data += '\0'
        self.connectSock.send(bytes(data[: self.BUFFSIZE].encode('utf-8')))
        n = self.BUFFSIZE
        if '\0' not in data[: self.BUFFSIZE]:
            while True:
                self.connectSock.send(bytes(data[n : n + self.BUFFSIZE].encode('utf-8')))
                n += self.BUFFSIZE
                if '\0' in data[n : n + self.BUFFSIZE]:
                    self.connectSock.send(bytes(data[n : len(data)].encode('utf-8')))
                    break
    
    def recvResponse(self):
        fullData = ''
        data = self.connectSock.recv(self.BUFFSIZE)
        fullData += data.decode('utf-8')
        if bytes('\0'.encode('utf-8')) not in data[:self.BUFFSIZE]:
            while True:
                data = self.connectSock.recv(self.BUFFSIZE)
                fullData += data.decode('utf-8')
                if bytes('\0'.encode('utf-8')) in data:
                    break
        fullData = json.loads(fullData[:-1])
        return fullData
    
    def conncect(self, addr, port):
        self.connectSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connectSock.connect((addr, port))
        self.connected = True
