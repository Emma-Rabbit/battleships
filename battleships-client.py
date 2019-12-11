#!/bin/env python3
import socket
import json
from connectionManager import connectionManager

class Client:
    def __init__(self):
        print('enter port')
        self.port = int(input())
        self.connmng = connectionManager(self.port)

    def run(self):
        print('Welcome to battleships!\nYour name: ')
        while True:
            start = True
            # self.pnmg.connect()
            if start:
                start = False
                data = self.connmng.g(self.inputName, '127.0.0.1', 42069)
                self.getSessionId(data)
                print('Type help for help.')
            self.connmng.g(self.actionMng, '127.0.0.1', 42069)
            # self.pnmg.closeConnection()


    def inputName(self):
        x = input()
        msg = {'action' : 'userRegister', 'userName' : x, 'port' : self.port}
        return msg

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
            return self.createRoom()
    
    def printHelp(self):
        print('Commands:\n')
        print('list - lists existing rooms\n')
        print('join - joins the room\n')
        print('create - creates the room\n')

    def listRoomsRequest(self):
        msg = {'action' : 'roomList', 'sessionId' : self.sessionId}
        return msg

    def createRoom(self):
        print('Enter room name: ')
        name = input()
        print('Would yhou like to add description? (y/n)')
        opt = input()
        if opt == 'y':
            print('Enter room description: ')
            desc = input()
        print('Would you like to add password? (y/n)')
        opt = input()
        if opt == 'y':
            print('Enter password: ')
            password = input()
        print('Leave board settings default? (y/n)')
        opt = input()
        width = 10
        height = 10
        battleships = {'1': 4, '2': 3, '3': 2, '4': 1}
        if opt == 'n':
            print('Enter board width: ')
            width = input()
            print('Enter board height: ')
            height = input()
        msg = {'action': 'roomCreate', 'sessionId': self.sessionId, 'roomName' : name, 'boardWidth' : width, 'boardHeight': height, 'battleships': battleships}
        return msg
        
client = Client()
client.run()