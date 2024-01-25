from multiprocessing import Array, Value, Semaphore
from random import shuffle
import signal

class Game:
    
    def __init__(self, num_players) :
        
        self.colors = ["red","blue","green","black","white"]
        
        self.num_players = Value('i',num_players)
        self.fuse = Value('i',3)
        self.info = Value('i',3+num_players)
        
        self.create_suites()
        
        self.create_cards()
        self.shuffle_cards()
        self.deals_cards()
                
        
    def create_suites(self) :
        self.suites = []
        for i in range (self.num_players.value) :
            self.suites.append(Array('i',[-1]*(5)))
        
    def create_cards(self) :
        
        #Create set of cards
        
        self.discard_pile = Array('i',[-1]*(self.num_players.value*10))
        
        self.draw_pile = Array('i', [0] * (self.num_players.value*10))
        
        for i in range(self.num_players.value) :
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
        
        original_list = list(self.draw_pile)
        
        random_indices = list(range(len(original_list)))
        shuffle(random_indices)
        
        for i, j in enumerate(random_indices) :
            self.draw_pile[i] = original_list[j]
        
        
    def show_cards(self,Array) :

    
        cartes = list(Array)
        for i in range(len(cartes)) :
            color = cartes[i]//5
            cartes[i] = f"{self.colors[color]} {cartes[i]%5+1}"
        
        for i in cartes :
            print(i)
            
    def deals_cards(self):
        """Deal cards to each player"""
        self.players = []
        for i in range(self.num_players.value):
            self.players.append(Array('i', [0] * (5)))

            for j in range(5):
                self.players[i][j] = self.draw_pile[0]
                for k in range(len(self.draw_pile) - 1):
                    self.draw_pile[k] = self.draw_pile[k + 1]
                self.draw_pile[len(list(self.draw_pile)) - 1] = -1 

    def is_finished(self) :
        
        won = True
        
        lost = False
        
        for suite in self.suites :
            if suite[4]%5+1 != 5  :
                won = False
                
        if self.fuse.value == 0 :
            lost = True
        else :
            i = 0
            while (i<len(list(self.discard_pile)) and (self.discard_pile[i] != 5 or self.discard_pile[i] != -1 )) :
                i += 1
            if self.discard_pile[i] == 5 :
                lost = True
                
        return won,lost

        
             
    def start(self) :
        
        num_turn = 0
            
        won,lost = self.is_finished()
        
        locks = []
        game_lock = Semaphore(0)
        for _ in range(self.num_players) :
            locks.append(Semaphore(0))
        
        
        while not won and not lost :
            
            num_turn += 1
            
            locks[(num_turn+1)%self.num_players].release()
            
            game_lock.acquire()
            
        
            won,lost = self.is_finished()
            print("Turn",self.num_turn,"is over")
            
        
        
        
        if won :
            print("You won!")
        else :
            print("You lost!")
            
        print("The game lasted",self.num_turn,"turns")
        

                
        
        
            
        
if __name__ == "__main__" :
    
    jeu = Game(5)

    for i in range(jeu.num_players.value) :
        print("Player",i+1,"has the following cards:")
        jeu.show_cards(jeu.players[i])

        

        
