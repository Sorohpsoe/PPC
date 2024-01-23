from multiprocessing import Array ,Value
from random import shuffle

class Game:
    
    def __init__(self, num_players) :
        
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
        couleurs = ["red","blue","green","black","white"]
    
        cartes = list(Array)
        for i in range(len(cartes)) :
            couleur = cartes[i]//5
            cartes[i] = f"{couleurs[couleur]} {cartes[i]%5+1}"
        
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

    def game_won(self) :
        
        
            
        
if __name__ == "__main__" :
    
    jeu = Game(5)

    for i in range(jeu.num_players.value) :
        print("Player",i+1,"has the following cards:")
        jeu.show_cards(jeu.players[i])

        

        
