#!/bin/env python3
import socket
import json
from copy import deepcopy

BUFF_SIZE = 1024

class Server:
    def __init__(self):
        self.HOST = '127.0.0.1'
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.usridCounter = 0
        self.activeUsers = []
        self.roomidCounter = 0
        self.activeRooms = []
        f = open('config.json','r')
        x = json.loads(f)
        self.PORT = x['PORT']
        self.s.bind((self.HOST, self.PORT))
        self.s.listen(10)

    def recvData(self):
        self.conn, self.addr = self.s.accept()
        fullData = ''
        data = self.conn.recv(BUFF_SIZE)
        fullData += data.decode('utf-8')
        if '\0' not in data:
            while True:
                data = self.conn.recv(BUFF_SIZE)
                fullData += data.decode('utf-8')
                if '\0' in data:
                    data = self.conn.recv(BUFF_SIZE)
                    fullData += data.decode('utf-8')
                    break
        return fullData

    def sendData(self, data):
        self.conn.send(bytes(data[: BUFF_SIZE].encode('utf-8')))
        n = BUFF_SIZE
        if '\0' not in data[: BUFF_SIZE]:
            while True:
                self.conn.send(bytes(data[n : n + BUFF_SIZE].encode('utf-8')))
                n += BUFF_SIZE
                if '\0' in data[n : n + BUFF_SIZE]:
                    self.conn.send(bytes(data[n : len(data)].encode('utf-8')))
                    break

    def manageActions(self, data):
        #potem obsługa błędów
        act = data['action']
        if act == 'userRegister':
            userRegister(data)
        elif act == 'roomList':
            joinRoom(data)
        elif act == 'roomCreate':
            createRoom(data)
        elif act == 'roomJoin':
            joinRoom(data)
        elif act == 'boardSet':
            pass

    def userRegister(self, data):
        user = {}
        user['userName'] = data['userName']
        user['userSession'] = self.usridCounter
        msg = {'sessionID':self.usridCounter}
        self.activeUsers.append(user)
        self.usridCounter += 1
        msg = json.dumps(msg)
        sendData(msg)
    
    def listRooms(self, data):
        if data['sessionId'] not in data:
            #ERROR
            pass
        rooms = deepcopy(self.activeRooms)
        for i in rooms:
            if rooms[i]['roomPassword'] not in rooms[i]:
                rooms[i]['passwordNeeded'] = False
            else:
                rooms[i]['passwordNeeded'] = True
                rooms[i].pop('roomPassword')
        msg = json.loads(rooms)
        sendData(msg)
        pass

    def createRoom(self, data):
        properties = ['sessionId', 'roomName', 'boardWidth', 'boardHight', 'battleships']
        for i in properties:
            if data[properties[i]] not in data:
                #ERROR
                pass
        room = {}
        room['roomCreator'] = data['sessionId']
        room['roomName'] = data['roomName']
        if data['roomPassword'] in data:
            room['roomPassword'] = data['roomPassword']
        room['boardWidth'] = data['boardWidth']
        room['boardHeight'] = data['boardHeight']
        if data['roomDescription'] in data:
            room['roomDescription'] = data['roomDescription']
        room['battleships'] = data['batleships']
        room['roomId'] = self.roomidCounter
        room['usercount'] = 1
        creator = {'isCreator' : True}
        room['players'][room['roomCreator']] = creator
        self.roomidCounter += 1
        self.activeRooms.append(room)
        msg = {'roomId': room['roomId']}
        msg = json.dumps(msg)
        sendData(msg)

    def joinRoom(self, data):
        if data['sessionId'] not in data:
            #ERROR
            pass
        roomId = -1
        for i in self.activeRooms:
            if self.activeRooms[i]['roomId'] == data['roomId']:
                roomId = self.activeRooms[i]['roomId']
                if self.activeRooms[i]['roomPassword'] in self.activeRooms[i]:
                    if data['password'] not in data:
                        #ERROR
                        break
                    else:
                        if self.activeRooms[i]['roomPassword'] != data['password']:
                            #ERROR
                            break
                self.activeRooms[i]['usercount'] += 1
                player = {'isCreator': False}
                self.activeRooms[i]['players'][data['sessionId']] = player
                msg = {'status':'successful'}
                msg = json.dumps(msg)
                sendData(msg)
                break
        if roomId == -1:
            #ERROR
            pass 
    
    def checkBoard(self, data):
        room = {}
        for i in self.activeRooms:
            players = self.activeRooms[i]['players']
            if data['sessionId'] in players:
                room = self.activeRooms[i]
                break
            elif i == len(self.activeRooms):
                #ERROR
                pass
        board = data['board']
        boardCopy = deepcopy(data['board'])
        neighbourMap = []
        for i in range(data['boardWidth']):
            a = []
            neighbourMap.append(a)
            for j in range(data['boardHeight']):
                neighbourMap[i].append(0)
        for i in range(room['boardHeight']):
            counter = 0
            n = 0
            for j in range(room['boardWidth']):
                if board[i][j] != 0 and counter == 0:
                    if board[i][j + 1] == 0:
                        continue
                    n = board[i][j]
                    counter += 1
                    boardCopy[i][j] = 0
                    neighbourMap[i][j]
                elif counter > 0:
                    if board[i][j] != n:
                        #ERROR
                        pass
                    elif counter > n:
                        #ERROR
                        pass
                    boardCopy[i][j] = 0
                    counter += 1
        for j in range(room['boardWidth']):
            counter = 0 
            n = 0
            for i in range(room['boardHeight']):
                if board[i][j] != 0 and counter == 0:
                    if board[i + 1][j] == 0:
                        continue
                    n = board[i][j]
                    counter += 1
                    boardCopy[i][j] = 0
                elif counter > 0:
                    if board[i][j] != n:
                        #ERROR
                        pass
                    elif counter > n:
                        #ERROR
                        pass
                    boardCopy[i][j] = 0
                    counter += 1
