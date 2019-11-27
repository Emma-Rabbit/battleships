#!/bin/env python3
import socket
import json

class packetMng:
    def __init__(self, addr, port):
        self.BUFFSIZE = 8
        self.addr = addr
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.s.connect((self.addr, self.port))

    def sendData(self, data):
        data = json.dumps(data)
        data +='\0'
        self.s.send(bytes(data[: self.BUFFSIZE].encode('utf-8')))
        n = self.BUFFSIZE
        if '\0' not in data[: self.BUFFSIZE]:
            while True:
                #print(data[n : n + self.BUFFSIZE])
                self.s.send(bytes(data[n : n + self.BUFFSIZE].encode('utf-8')))
                n += self.BUFFSIZE
                if '\0' in data[n : n + self.BUFFSIZE]:
                    self.s.send(bytes(data[n : len(data)].encode('utf-8')))
                    break
    
    def recvData(self):
        fullData = ''
        data = self.s.recv(self.BUFFSIZE)
        fullData += data.decode('utf-8')
        if bytes('\0'.encode('utf-8')) not in data[:self.BUFFSIZE]:
            while True:
                data = self.s.recv(self.BUFFSIZE)
                fullData += data.decode('utf-8')
                if bytes('\0'.encode('utf-8')) in data:
                    #data = self.s.recv(self.BUFFSIZE)
                    #fullData += data.decode('utf-8')
                    break
        fullData = json.loads(fullData[: -1])
        #print(fullData)
        return fullData


class Client:
    def __init__(self):
        self.pnmg = packetMng('127.0.0.1', 42069)

    def run(self):
        self.pnmg.connect()
        print('Welcome to battleships!\nYour name: ')
        self.inputName()
        self.getSessionId(self.pnmg.recvData())
        while True:
            print('Type help for help.')
            self.actionMng()

    def inputName(self):
        x = input()
        msg = {'action' : 'userRegister', 'userName' : x, 'port' : 1234}
        self.pnmg.sendData(msg)

    def getSessionId(self, data):
        self.sessionId = data['sessionId']
        #print("sessionId: ", self.sessionId)

    def actionMng(self):
        x = input()
        if x == 'help':
            self.printHelp()
        elif x == 'list':
            pass
        elif x == 'join':
            pass
        elif x == 'create':
            pass
    
    def printHelp(self):
        print('Commands:\n')
        print('list - lists existing rooms\n')
        print('join - joins the room\n')
        print('create - creates the room\n')

    def listRooms(self):
        msg = {'action' : 'roomList', 'sessionId' : self.sessionId}
        data = self.pnmg.recvData()

    def createRoom(self):
        print('Enter room name: ')
        name = input()
        print('Would you like to add description? (y/n)')
        opt = input()
        if opt == 'y':
            print('Enter room description: ')
            desc = input()
        print('Would you like to add password? (y/n)')
        opt = input()
        if opt == 'y':
            print('Enter password: ')
            password = input()
        print('Leave board option as default? (y/n)')
        opt = input()
        width = 10
        height = 10
        if opt == 'n':
            print('Enter board width: ')
            width = input()
            print('Enter board height: ')
            height = input()
        msg = {'action': 'roomCreate', 'sessionId': self.sessionId, 'roomName' : name, 'boardWidth' : width, 'boardHeight': height}
        
client = Client()
client.run()