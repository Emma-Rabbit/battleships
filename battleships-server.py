#!/bin/env python3
import socket
import json
import threading

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
            pass
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
        sendData(msg)
    
    def listRooms(self, data):
        pass

    def createRoom(self, data):
        properties = ['sessionId', 'roomName', 'boardWidth', 'boardHight', 'battleships']
        for i in properties:
            if data[properties[i]] not in data:
                #ERROR
                pass
        room = {}
        room['roomOwner'] = data['sessionId']
        room['roomName'] = data['roomName']
        if data['roomPassword'] in data:
            room['roomPassword'] = data['roomPassword']
        room['boardWidth'] = data['boardWidth']
        room['boardHeight'] = data['boardHeight']
        room['roomDescription'] = data['roomDescription']
        room['battleships'] = data['batleships']
        room['roomId'] = self.roomidCounter
        room['usercount'] = 1
        room['assignedUsers'] = [room['roomOwner']]
        self.roomidCounter += 1
        self.activeRooms.append(room)
        msg = {'roomId': room['roomId']}
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
                self.activeRooms[i]['assignedUsers'].append(data['sessionId'])
                msg = {'status':'successful'}
                sendData(msg)
                break
        if roomId == -1:
            pass #ERROR
    
