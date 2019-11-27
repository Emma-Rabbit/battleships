#!/bin/env python3
import random
import socket
import json
from copy import deepcopy
import threading

BUFF_SIZE = 8
#room
#   roomCreator
#   roomName
#   roomPassword
#   boardWidth
#   boardHeight
#   battleships
#       #tutaj statki xd
#   roomId
#   userCount
#   players
#       sessionId
#           isCreator
#           ready
#           userName
#           port
#           addr
#           userSession
#           board
class Server:
    def __init__(self):
        self.HOST = '127.0.0.1'
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.threads = []
        self.usridCounter = 0
        self.activeUsers = []
        self.roomidCounter = 0
        self.activeRooms = []
        f = open('config.json','r')
        r = f.read()
        x = json.loads(r)
        self.PORT = x['PORT']
        self.s.bind((self.HOST, self.PORT))

    def recvData(self):
        self.s.listen(10)
        self.conn, self.addr = self.s.accept()
        fullData = ''
        data = self.conn.recv(BUFF_SIZE)
        fullData += data.decode('utf-8')
        if bytes('\0'.encode('utf-8')) not in data[:BUFF_SIZE]:
            while True:
                #print(fullData)
                data = self.conn.recv(BUFF_SIZE)
                fullData += data.decode('utf-8')
                if bytes('\0'.encode('utf-8')) in data:
                    #data = self.conn.recv(BUFF_SIZE)
                    #fullData += data.decode('utf-8')
                    break
        fullData = json.loads(fullData[: -1])
        return fullData

    def sendData(self, data):
        data += '\0'
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
        print(data)
        act = data['action']
        if act == 'userRegister':
            self.userRegister(data)
        elif act == 'roomList':
            self.joinRoom(data)
        elif act == 'roomCreate':
            self.createRoom(data)
        elif act == 'roomJoin':
            self.joinRoom(data)
        elif act == 'boardSet':
            self.checkBoard(data)
        elif act == 'roomList':
            self.listRooms(data)
    
    def userRegister(self, data):
        user = {}
        user['userName'] = data['userName']
        user['port'] = data['port']
        user['addr'] = self.addr
        user['userSession'] = self.usridCounter
        msg = {'sessionId':self.usridCounter}
        self.activeUsers.append(user)
        self.usridCounter += 1
        msg = json.dumps(msg)
        self.sendData(msg)
        print('Registered user ', data['userName'])
    
    def listRooms(self, data):
        if data['sessionId'] not in data:
            #ERROR
            pass
        rooms = deepcopy(self.activeRooms)
        for i in rooms:
            if i['roomPassword'] not in rooms[i]:
                i['passwordNeeded'] = False
            else:
                i['passwordNeeded'] = True
                i.pop('roomPassword')
        msg = json.dumps(rooms)
        self.sendData(msg)
        pass
    
    def createRoom(self, data):
        properties = ['sessionId', 'roomName', 'boardWidth', 'boardHight', 'battleships']
        for i in properties:
            if data[i] not in data:
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
        room['players'][room['roomCreator']]['ready'] = False
        for i in self.activeUsers:
            if i['sessionId'] == data['sessionId']:
                room['players'][data['sessionId']] = i
                break
        self.roomidCounter += 1
        self.activeRooms.append(room)
        msg = {'roomId': room['roomId']}
        msg = json.dumps(msg)
        self.sendData(msg)
    
    def joinRoom(self, data):
        if data['sessionId'] not in data:
            #ERROR
            pass
        roomId = -1
        for i in self.activeRooms:
            if i['roomId'] == data['roomId']:
                roomId = i['roomId']
                if i['roomPassword'] in i:
                    if data['password'] not in data:
                        #ERROR
                        break
                    else:
                        if i['roomPassword'] != data['password']:
                            #ERROR
                            break
                i['usercount'] += 1
                player = {'isCreator': False}
                i['players'][data['sessionId']] = player
                i['players'][data['sessionId']]['ready'] = False
                msg = {'status':'successful'}
                msg = json.dumps(msg)
                self.sendData(msg)
                break
        if roomId == -1:
            #ERROR
            pass 
    
    def markCell(self, board, x, y, side):
        if side == 'top':
            for i in range(y - 1, y + 1):
                try:
                    board[x - 1][i] = -1
                except:
                    continue
        elif side == 'bottom':
            for i in range(y - 1, y + 1):
                try:
                    board[x + 1][i] = -1
                except:
                    continue
        elif side == 'left':
            for i in range(x - 1, x + 1):
                try:
                    board[i][y - 1] = -1
                except:
                    continue
        elif side == 'right':
            for i in range(x - 1, x + 1):
                try:
                    board[i][y + 1] = -1
                except:
                    continue

    def checkBoard(self, data):
        room = {}
        for i in self.activeRooms:
            players = i['players']
            if data['sessionId'] in players:
                room = i
                break
            elif i == len(self.activeRooms):
                #ERROR
                pass
        board = data['board']
        boardCopy = deepcopy(data['board'])
        neighbourMap = []
        for i in range(data['boardHeight']):
            a = []
            neighbourMap.append(a)
            for j in range(data['boardWidth']):
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
                    markCell(neighbourMap, i, j, 'left')
                elif counter > 0:
                    if board[i][j] != n:
                        #ERROR
                        pass
                    elif counter > n:
                        #ERROR
                        pass
                    boardCopy[i][j] = 0
                    counter += 1
                    markCell(neighbourMap, i, j, 'top')
                    markCell(neighbourMap, i, j, 'bottom')
                    if counter == n:
                        markCell(neighbourMap, i, j, 'right')
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
                    markCell(neighbourMap, i, j, 'top')
                elif counter > 0:
                    if board[i][j] != n:
                        #ERROR
                        pass
                    elif counter > n:
                        #ERROR
                        pass
                    boardCopy[i][j] = 0
                    counter += 1
                    markCell(neighbourMap, i, j, 'left')
                    markCell(neighbourMap, i, j, 'right')
                    if counter == n:
                        markCell(neighbourMap, i, j, 'botoom')
        for i in range(data['boardHeight']):
            for j in range(data['boardWidth']):
                if board[i][j] != 0 and neighbourMap[i][j] == -1:
                    #ERROR
                    pass
        #przypisać board do gracza tutaj
        room['players'][data['sessionId']]['board'] = data['board']
        msg = {'status': 'success'}
        msg = json.dumps(msg)
        sendData(msg)
        #dodać do gracza status gotowości
        room['players'][data['sessionId']]['ready'] = True
    
    def chceckIfReady(self):
        for i in self.activeRooms:
            p = []
            ready = False
            for j in i['players']:
                if j['ready'] == False:
                    ready = False
                    break
                k = 0
                p[k] = j
                k += 1
                ready = True
            if ready:
                pass #stworzyć thread

class Thred(threading.Thread):
    def __init__(self, threadID, room):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.player = []
        # self.player[0] = player1
        # self.player[1] = player2
        self.ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sr.bind(('127.0.0.1', 1234)) #co rzobić z portem? xd
        self.currentPlayer = -1
        self.room = room
        for i in self.room['players']:
            n = 0
            self.player[n] = i
            n += 1
    
    def run(self):
        #wysłać powiadomienia o początku gry
        #wybrać pierwszego gracza
        #while gameOn:
        #wysłać powiadomienie o początku tury
        #czekać na ruch
        #sprawdzić ruch
        #zapisać zmiany
        #sprawdzić koniec gry
        #wysłać zmiany do drugiego gracza?
        #zmienić currentPlayer
        self.sendStartNotif()
        self.choosePlayer()
        gameOn = True
        while gameOn:
            self.sendTurnNotif()
            self.recvMove()
            gameOn = self.gameOver()
            #???
            self.changePlayer()
        pass
    
    def sendDataFirst(self, playerNo, data):
        addr = self.player[playerNo]['addr']
        port = self.player[playerNo]['port']
        self.ss.connect((addr, port))
        self.ss.send()
    
    def recvData(self):
        self.s.listen(2)
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
    
    def sendStartNotif(self):
        msg = {'status': 'gameStart'}
        msg = json.dumps(msg)
        self.sendDataFirst(0, msg)
        self.sendDataFirst(1, msg)
    
    def choosePlayer(self):
        self.currentPlayer = random.randint(0,1)
    
    def sendTurnNotif(self):
        msg = {'status' : 'yourTurn'}
        self.sendDataFirst(self.currentPlayer, msg)
    
    def recvMove(self):
        data = recvData()
        if self.addr != self.player[self.currentPlayer]['addr']:
            #ERROR
            return -1
        hit = self.chceckMove(data)
        if hit < 0:
            #ERROR
            pass
        self.saveMove(data, hit)
        msg = {}
        if hit:
            msg = {'status' : 'hit'}
        else:
            msg = {'status' : 'miss'}
        msg = json.dumps(msg)
        self.sendData(msg)

    def chceckMove(self, data):
        if data['x'] < 0 or data['y'] < 0 or data['x'] > self.roomSettings['boardWidth'] or data['y'] > self.roomSettings['boardHeight']:
            #ERROR
            return -1
        if self.player[self.currentPlayer]['board'][data['x']][data['y']] == -1:
            #ERROR
            return -1
        if self.player[self.currentPlayer]['board'][data['x']][data['y']] > 0:
            return True
        elif self.player[self.currentPlayer]['board'][data['x']][data['y']] == 0:
            return False

    def saveMove(self, data, hit):
        board = self.player[self.currentPlayer]['board']
        board[data['x']][data['y']] = -1

    def gameOver(self):
        over = False
        for i in self.player:
            over = True
            for j in i['board']['boardWidth']:
                for k in i['board']['boardHeight']:
                    if k > 0:
                        over = False
                        break
                break
            if over:
                return over
        return over

    def changePlayer(self):
        if self.currentPlayer == 0:
            self.currentPlayer = 1
        elif self.currentPlayer == 1:
            self.currentPlayer = 0
        else:
            #ERROR
            pass

class errorMng:
    def __init__(self):
        pass
    
server = Server()
while True:
    data = server.recvData()
    server.manageActions(data)