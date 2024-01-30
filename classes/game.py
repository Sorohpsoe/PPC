from multiprocessing import Manager, Semaphore
from random import shuffle
import signal
import threading
from player import Player
import socket

class Game:
    
    def __init__(self, num_players,port) :
        
        self.colors = ["red","blue","green","black","white"]
        
        self.num_players = num_players
        self.fuse = 3
        self.info = 3+num_players
        self.port = port
        
        self.discard_pile = []
        self.suites = [[] for _ in range(num_players)]

        self.create_cards()
        self.shuffle_cards()
        self.deals_cards()
        
                
        
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
        
        
    def show_cards(self,cartes) :
        
        top = "╔"
        color_text = "║"
        number_text = "║"
        bottom = "╚"
        
        
        for i in range(len(cartes)) :
            color = self.colors[cartes[i]//5]
            number = cartes[i]%5+1

            
            if color == "red" :
                top += "═══════╦"
                color_text += "  \033[31m"+color+"\033[0m  ║"
                number_text += "   \033[31m"+str(number)+"\033[0m   ║"
                bottom += "═══════╩"
            if color == "blue" :
                top += "═══════╦"
                color_text += " \033[34m"+color+"\033[0m  ║"
                number_text += "   \033[34m"+str(number)+"\033[0m   ║"
                bottom += "═══════╩"
            if color == "green" :
                top += "═══════╦"
                color_text += " \033[32m"+color+"\033[0m ║"
                number_text += "   \033[32m"+str(number)+"\033[0m   ║"
                bottom += "═══════╩"
            if color == "black" :
                top += "═══════╦"
                color_text += " \033[30m"+color+"\033[0m ║"
                number_text += "   \033[30m"+str(number)+"\033[0m   ║"
                bottom += "═══════╩"
            if color == "white" :
                top += "═══════╦"
                color_text += " \033[37m"+color+"\033[0m ║"
                number_text += "   \033[37m"+str(number)+"\033[0m   ║"
                bottom += "═══════╩"
                
        top = top[:-1] + "╗"
        color_text = color_text[:-1] + "║"
        number_text = number_text[:-1] + "║"
        bottom = bottom[:-1] + "╝"
        
        print(top)
        print(color_text)
        print(number_text)
        print(bottom)

        
    
            
    def deals_cards(self):
        """Deal cards to each player"""
        self.hands = []
        for i in range(self.num_players):
            self.hands.append([])
            for _ in range(5):
                self.hands[i].append(self.draw_pile.pop())

    def information(self,id_joueur,id_neighbor):
        self.info-=1
        
    def discard(self,id_joueur,index_card):
        card=self.hands[id_joueur].pop(index_card)
        self.discard_pile.append(card)
        self.fuse-=1
    
    def draw(self,id_joueur):
        card=self.draw_pile.pop()
        self.hands[id_joueur].append(card)
    
    def play(self,id_joueur,index_card,index_suites):
        card=self.hands[id_joueur].pop(index_card)
        self.suites[index_suites].append(card)

                
                

    def is_finished(self) :
        
        won = True
        
        lost = False
        
        for suite in self.suites :
            if len(suite) != 5 :
                won = False
                
        if self.fuse == 0 :
            lost = True
        else :
            if 5 in self.discard_pile :
                lost = True
                
        return won,lost
    

    def create_players(self) :
        
        self.locks = []  
        self.players = []
        

            
        for i in range(self.num_players) : 
            
            self.locks.append(Semaphore(0))
            
            self.players.append(Player(i,self.hands,self.locks[i],self.suites,self.num_players,self.fuse,self.info,self.port))


    def get_socket_message(self, client_socket,lock,my_lock):
        
        print("ouverture handler")
        
        with client_socket:
            
            while True :
                
                my_lock.acquire()

                data = client_socket.recv(1024).decode()
                self.buffer += data
                lock.release()
    
    def logic(self) :
        infos = self.buffer.split(" ")
        self.bufffer = ""
        if infos[1] == "play" :
            self.play(infos[0],infos[2],infos[3])
        elif infos[1] == "discard" :
            self.discard(infos[0],infos[2])
        elif infos[1] == "info" :
            self.information(infos[0],infos[2])
            

    def start(self) :
        
        HOST = "localhost"
        self.create_players()
    
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            
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
                print(f"thread {i} created")
                t.start()
                player_threads.append(t)
            

            tcp_threads=[]
            for i in range(self.num_players) :
                conn, addr = server_socket.accept()
                t = threading.Thread(target=self.get_socket_message, args=(conn, self.game_lock,self.buffer_locks[i]))
                print(f"connection {i} connected")
                t.start()
                tcp_threads.append(t)
            
            num_turn = 0
                
            won,lost = self.is_finished()

            
            
            while not won and not lost :
                
                print("Beggining of turn : ",num_turn)
                
                num_turn += 1
                
                self.buffer_locks[(num_turn-1)%self.num_players].release()
                self.locks[(num_turn-1)%self.num_players].release()
                
                self.game_lock.acquire()
                
                self.logic()
               
            
                won,lost = self.is_finished()
                print("Turn",num_turn,"is over")
                
            if won :
                print("You won!")
            else :
                print("You lost!")

if __name__ == "__main__" :
    
    jeu = Game(5,6698)
    jeu.start()
    
'''
    for i in range(jeu.num_players) :
        print("Player",i+1,"has the following cards:")
        print(jeu.hands[i])
        jeu.show_cards(jeu.hands[i])
'''

        

        
