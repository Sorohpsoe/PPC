from multiprocessing import Semaphore, Queue
from random import shuffle
import signal
import threading
from .player import Player
import socket
import os

class Game:
    
    def __init__(self, num_players,port) :
        
        self.colors = ["red","blue","green","black","white"]
        
        self.num_players = num_players
        
        self.tokens={"fuse":3,"info":3+num_players,"game_over":False}
        self.port = port
        
        self.discard_pile = []
        self.suites = [[] for _ in range(num_players)]

        self.create_cards()
        self.shuffle_cards()
        self.deals_cards()
        self.queue=Queue()
        
                
        
    def create_suites(self) :
        self.suites = []
        for i in range (self.num_players) :
            self.suites.append([])
        
    def create_cards(self) :
        
        #Create set of cards
        

        
        self.draw_pile = [0]*(self.num_players*10)
        
        for i in range(self.num_players) :
            self.draw_pile[i*10] = 0 + i*5
            self.draw_pile[i*10+1] = 0 + i*5
            self.draw_pile[i*10+2] = 0 + i*5
            
            self.draw_pile[i*10+3] = 1 + i*5
            self.draw_pile[i*10+4] = 1 + i*5
            
            self.draw_pile[i*10+5] = 2 + i*5
            self.draw_pile[i*10+6] = 2 + i*5
        
            self.draw_pile[i*10+7] = 3 + i*5
            self.draw_pile[i*10+8] = 3 + i*5
            
            self.draw_pile[i*10+9] = 4 + i*5
            
    def shuffle_cards(self) :
        
        #Shuffles the draw pile 
        
        original_list = self.draw_pile.copy()
        
        random_indices = list(range(len(original_list)))
        shuffle(random_indices)
        
        for i, j in enumerate(random_indices) :
            self.draw_pile[i] = original_list[j]
    
        
            
    def deals_cards(self):
        """Deal cards to each player"""
        self.hands = []
        for i in range(self.num_players):
            self.hands.append([])
            for _ in range(5):
                self.hands[i].append(self.draw_pile.pop())

    def information(self,id_joueur,id_neighbor):
        self.tokens["info"]-=1

    def discard(self,id_joueur,index_card):
        card=self.hands[id_joueur].pop(index_card)
        self.discard_pile.append(card)
        self.tokens["fuse"]-=1
        self.draw(id_joueur)
    
    def draw(self,id_joueur):
        card=self.draw_pile.pop()
        self.hands[id_joueur].append(card)

    
    def play(self,id_joueur,index_card,index_suites):
        card=self.hands[id_joueur].pop(index_card)
        self.suites[index_suites].append(card)
        self.draw(id_joueur)

                
                

    def is_finished(self) :
        
        won = True
        
        lost = False
        
        for suite in self.suites :
            if len(suite) != 5 :
                won = False
                
        if self.tokens["fuse"] == 0 :
            lost = True
        else :
            for card in self.discard_pile:
                if card%5+1==5:
                    lost = True
                
        return won,lost
    

    def create_players(self) :
        
        self.locks = []  
        self.players = []
        

            
        for i in range(self.num_players) : 
            
            self.locks.append(Semaphore(0))
            
            self.players.append(Player(i,self.hands,self.locks[i],self.suites,self.num_players,self.tokens,self.port,self.queue))


    def get_socket_message(self, client_socket,lock,my_lock):
        
        
        with client_socket:
            
            while True :
                
                my_lock.acquire()
                
                if not self.tokens["game_over"]:
                    data = client_socket.recv(1024).decode()
                    self.buffer = data

                lock.release()
                
                if self.tokens["game_over"]:
                    break
    
    def logic(self) :
        infos = self.buffer.split(" ")
        
        if infos[1] == "play" :
            self.play(int(infos[0]),int(infos[2]),int(infos[3]))
        elif infos[1] == "discard" :
            self.discard(int(infos[0]),int(infos[2]))
        elif infos[1] == "info" :
            self.information(int(infos[0]),int(infos[2]))
            

    def start(self) :
        
        HOST = "localhost"
        self.create_players()
    
        server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        
        server_socket.bind((HOST, self.port))
        server_socket.listen(self.num_players)
        
        self.game_lock = Semaphore(0)
        self.buffer_locks = []
        
        for _ in range(self.num_players) :
            self.buffer_locks.append(Semaphore(0))
        
        self.buffer = ""

        player_threads = []                
        for i in range(self.num_players) :
            t = threading.Thread(target=self.players[i].game_on)
            t.start()
            player_threads.append(t)
        

        tcp_threads=[]
        connections=[]
        for i in range(self.num_players) :
            conn, addr = server_socket.accept()
            connections.append(conn)
            t = threading.Thread(target=self.get_socket_message, args=(conn, self.game_lock,self.buffer_locks[i]))
            t.start()
            tcp_threads.append(t)
        
        num_turn = 0
            
        won,lost = self.is_finished()

        
        
        while not won and not lost :
            #print('\033c')
            print("Debut du tour : ",num_turn)
            
        
            
            num_turn += 1
            input(f"C'est au joueur {(num_turn-1)%self.num_players} de jouer, appuyer sur entrée pour continuer")
            
            self.buffer_locks[(num_turn-1)%self.num_players].release()
            self.locks[(num_turn-1)%self.num_players].release()
            
            self.game_lock.acquire()

            self.logic()
            self.bufffer = ""

            won,lost = self.is_finished()
            input("Appuyez sur entrée pour finir votre tour")

            print("Tour ",num_turn,"est terminé")
            
        if won :
            print("Vous avez gagné !")
        else :
            print("Vous avez perdu !")

        for conn in connections:
            conn.close()

        self.tokens["game_over"]=True
        
        server_socket.close()

        for lock in self.locks:
            lock.release()
        
        for buffer_lock in self.buffer_locks:
            buffer_lock.release()
        
        for tcp_thread in tcp_threads:
            tcp_thread.join()

        for player_thread in player_threads:
            player_thread.join()


            
                

            

if __name__ == "__main__" :
    
    jeu = Game(5,6686)
    jeu.start()
    


        

        
