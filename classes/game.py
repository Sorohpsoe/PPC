from multiprocessing import Semaphore, Queue
from random import shuffle
import threading
from .player import Player
import socket

class Game:
    
    def __init__(self, num_players,port) :
        """
        Args:
            num_players (int): number of players in the game.
            port (int): tcp socket port
        """
        
        #Set up the colors of the game (max 5 players)
        self.colors = ["red","blue","green","black","white"]
        
        self.num_players = num_players
        
        #There is 3 fuse tokens and 3+num_players info
        self.tokens={"fuse":3,"info":3+num_players,"game_over":False}
        
        self.port = port
        self.discard_pile = []
        self.suites = [[] for _ in range(num_players)]
        
        self.create_cards()
        self.shuffle_cards()
        self.deals_cards()
        self.queue=Queue()
        
                
        

    def create_cards(self) :
        
        """
        Creates the cards of the game.
        """
        

        
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
        
        """

            
                

    

if __name__ == "__main__" :
    
    jeu = Game(5,6686)
    jeu.start()
    


        

        

        """
        
        original_list = self.draw_pile.copy()
        
        random_indices = list(range(len(original_list)))
        shuffle(random_indices)
        
        for i, j in enumerate(random_indices) :
            self.draw_pile[i] = original_list[j]
    
        
            
    def deals_cards(self) :
        """
        Deal cards to each player
        """
        
        self.hands = []
        #For each player we create a hand of 5 cards and we remove them from the draw pile
        for i in range(self.num_players):
            self.hands.append([])
            for _ in range(5):
                self.hands[i].append(self.draw_pile.pop())

    def information(self,id_joueur,id_neighbor) :
        """
        When a information is given, the players loses one token of information.
        """
        self.tokens["info"]-=1

    def discard(self,id_joueur,index_card) :
        """
        We remove the card from the hand of the player and we add it to the discard pile.
        A card is only discarded when he made a mistake, so a fuse token is removed.

        Args:
            id_joueur (int): id of the player who discard the card
            index_card (int): index of the card that needs to be discarded
        """
        card=self.hands[id_joueur].pop(index_card)
        self.discard_pile.append(card)
        self.tokens["fuse"]-=1
        self.draw(id_joueur)
    
    def draw(self,id_joueur) :
        """
        We draw a card from the draw pile and we add it to the hand of the player.

        Args:
            id_joueur (int): id of the player who draws the card
        """
        
        card=self.draw_pile.pop()
        self.hands[id_joueur].append(card)

    
    def play(self,id_joueur,index_card,index_suites):
        """
        We remove the card from the hand of the player and we add it to the suite.
        The player draws a new card.

        Args:
            id_joueur (int): id of the player who plays the card
            index_card (int): index of the card that needs to be played in the hand
            index_suites (int): index of the suite where the card needs to be played
        """
        
        card=self.hands[id_joueur].pop(index_card)
        self.suites[index_suites].append(card)
        self.draw(id_joueur)

                
                

    def is_finished(self) :
        """
        Check if the game is finished.

        Returns:
            bool,bool: True if the game is won, True if the game is lost
        """
        
        won = True
        
        lost = False
        
        #Check if all the suites are complete. If not, the game is not won.
        for suite in self.suites :
            if len(suite) != 5 :
                won = False
        
        #Check if all the fuse tokens are used. If they are, the game is lost.
        if self.tokens["fuse"] == 0 :
            lost = True
        else :
            #Check if a 5 has been discarded. If it is, the game is lost.
            for card in self.discard_pile:
                if card%5+1==5:
                    lost = True
                
        return won,lost
    

    def create_players(self) :
        """
        Creates the players of the game and the locks for their turns.
        """
        
        self.locks = []  
        self.players = []
        

            
        for i in range(self.num_players) : 
            
            self.locks.append(Semaphore(0))
            
            self.players.append(Player(i,self.hands,self.locks[i],self.suites,self.num_players,self.tokens,self.port,self.queue))


    def get_socket_message(self, client_socket,lock,my_lock):
        """
        When it's the right turn, get the message from the socket and put it in the buffer.

        Args:
            client_socket (sock): socket of the client
            lock (Semaphore): lock of the game
            my_lock (Semaphore): lock of the buffer
        """

        with client_socket:
            
            while True :
                
                #Wait for the right turn
                my_lock.acquire()
                
                #If the game is not over, get the message from the socket, and put it in the buffer
                if not self.tokens["game_over"]:
                    data = client_socket.recv(1024).decode()
                    self.buffer = data

                #Release the lock of the game, so the game can continue
                lock.release()

                #If the game is over, break the loop.
                #It kills the thread, and the socket is closed.
                if self.tokens["game_over"]:
                    break
    
    def logic(self) :
        """
        For a given message, execute the right action.
        """
        #Here infos are the id of the player, the action, the index of the card 
        #(or the id of the player who gets a information) and the index of the suite (if the action is play)
        infos = self.buffer.split(" ")
        
        if infos[1] == "play" :
            self.play(int(infos[0]),int(infos[2]),int(infos[3]))
        elif infos[1] == "discard" :
            self.discard(int(infos[0]),int(infos[2]))
        elif infos[1] == "info" :
            self.information(int(infos[0]),int(infos[2]))
            

    def start(self) :
        """
        Main loop of the game.
        """
        
        self.create_players()
    
        #Open the socket to send/receive messages
        HOST = "localhost"
        server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #In case of error, we can reuse the port
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, self.port))
        #Listen for only the number of players
        server_socket.listen(self.num_players)
        
        #Lock of the game to wait for the tcp buffer to be written
        self.game_lock = Semaphore(0)
        
        #Create a lock for each tcp reader to wait for the turn of their player
        self.buffer_locks = []
        for _ in range(self.num_players) :
            self.buffer_locks.append(Semaphore(0))
        self.buffer = ""

        #Start the threads of the players
        player_threads = []                
        for i in range(self.num_players) :
            t = threading.Thread(target=self.players[i].game_on)
            t.start()
            player_threads.append(t)
        
        #Start the threads of the tcp readers
        tcp_threads=[]
        connections=[]
        for i in range(self.num_players) :
            conn, addr = server_socket.accept()
            connections.append(conn)
            t = threading.Thread(target=self.get_socket_message, args=(conn, self.game_lock,self.buffer_locks[i]))
            t.start()
            tcp_threads.append(t)
        
        #Initialize the first turn and the winning variables
        num_turn = 0
        won,lost = self.is_finished()

        
        
        while not won and not lost :
            num_turn += 1
            #Print the stats of the turn and tell which player needs to play next
            #Wait for the right player to play (input)
            print('\033c')
            print("Debut du tour : ",num_turn)
            input(f"C'est au joueur {(num_turn-1)%self.num_players} de jouer, appuyer sur entrée pour continuer")
            
            #Release the lock of the right player and their tcp reader
            self.buffer_locks[(num_turn-1)%self.num_players].release()
            self.locks[(num_turn-1)%self.num_players].release()
            
            #Wait for the tcp reader to write the buffer
            self.game_lock.acquire()

            #Execute the action of the player and reset the buffer
            self.logic()
            self.bufffer = ""

            #Check if the game is finished
            won,lost = self.is_finished()
            
            #Tell the player that the turn is finished
            input("Appuyez sur entrée pour finir votre tour")
            print("Tour ",num_turn,"est terminé")
            
        #Print the result of the game
        if won :
            print("Vous avez gagné !")
        else :
            print("Vous avez perdu !")

        #Close the sockets
        for conn in connections:
            conn.close()

        #Set the token game_over to True to stop the threads
        self.tokens["game_over"]=True
        
        #Close the server socket
        server_socket.close()

        #Release the locks of the players and the tcp readers, so the threads can stop
        for lock in self.locks:
            lock.release()
        for buffer_lock in self.buffer_locks:
            buffer_lock.release()
        
        #Wait for the threads to stop before exiting the programm
        for tcp_thread in tcp_threads:
            tcp_thread.join()
        for player_thread in player_threads:
            player_thread.join()