from multiprocessing import Array ,Value, Semaphore
from os import system, kill, getpid
import signal
import signal

class Player :
    def __init__(self,id,hands,lock,game_lock,suites,draw_pile,discard_pile,number_players,fuse,info):

        self.id = id
        self.number_players = number_players
        self.lock = lock
        self.game_lock=game_lock

        self.suites = suites
        self.draw_pile = draw_pile
        self.discard_pile = discard_pile
        
        self.fuse = fuse
        self.info = info
        
        self.colors = ["red","blue","green","black","white"]
        


    def handler(self,sig,frame):
        if  sig == signal.SIGUSR1 :
            
            #close queue
            
            pid = getpid()
            kill(pid, signal.SIGKILL)

    def draw_card(self,index):
        #envoi un message au game pour piocher  une carte et la mettre dans le tas de main du joueur a l'index donné
        
        pass        



    def give_info(self,neighbor):
        chek_choice=False
        while not chek_choice:
            choice = input("Voulez-vous donner une information sur une couleur ou un chiffre ? ").lower()
            if choice =="couleur" or choice=="chiffre":
                chek_choice=True
            else:
                print ("Choix incorrect")
        
        if choice == "couleur":
            valid_color = False
            while not valid_color:
                color_input = input("Veuillez entrer une couleur : ").lower()
                if color_input in self.colors:
                    valid_color = True
                else:
                    print("Couleur invalide. Veuillez choisir une couleur parmi :", self.colors)
            
            # Envoyer l'info a game ou au joueur
            
        elif choice == "chiffre":
            valid_number = False
            while not valid_number:
                number_input = input("Veuillez entrer un chiffre entre 1 et 5 : ")
                if number_input.isdigit() and 1 <= int(number_input) <= 5:
                    valid_number = True
                else:
                    print("Chiffre invalide. Veuillez choisir un chiffre entre 1 et 5.")
            
            # Envoyer l'info a game ou au joueur
            
        else:
            print("Choix non valide. Veuillez choisir 'couleur' ou 'chiffre'.")


    def discard(self,index):
        if self.hand[index]!=-1:
            card=self.hand[index]
            self.discard_pile.append(card)
            self.hand[index]=-1
            print(f"La carte :{card} a ete defaussee")
        else :
            print(f"La carte n'existe pas")
        self.draw_card(index)

    def play_card(self,index_card,index_suites):
        if self.hand[index_card]!=-1:
                card=self.hand[index_card]
                card_color=card//5
                card_number=card%5+1

                vide=True
                #On test si la liste souhaitée est vide 
                if self.suites[index_suites][0]!=-1 :
                    vide=False

                test_color=True
                for i in range(len(list(self.suites))):
                    #On regarde pour les suites non vides si la couleur n'est pas deja utilisée
                    if self.suites[i][0]!=-1 and i!=index_suites:  
                        if self.suites[i][0]//5==card_color:
                            test_color=False

                if test_color==False:  #La couleur est deja dans un autre suite 
                    self.discard(index_card)
                else:

                    if vide:
                        #Si notre carte est un 1 on la place sinon on la jette
                        if card_number==1:
                            self.suites[index_suites][0]=card
                            self.hand[index_card]=-1

                        else:
                            self.discard(index_card)
                    else:
                        #On cherche l'index de la derniere carte de la suite
                        last_card_index = 4
                        while (last_card_index>=0 and self.suites[index_suites][last_card_index] == -1):
                            last_card_index -= 1
                            #Si notre carte est bien la carte de la meme couleur incrementée de 1 on la place, sinon on la jette
                            if self.suites[index_suites][last_card_index]//5==card_color and self.suites[index_suites][last_card_index]%5+1==card_number-1:
                                self.suites[index_suites].append(card)
                                self.hand[index_card]=-1
                            else:
                                self.discard(index_card)

                
            
    
    def game_on(self) :
        
        signal.signal(signal.SIGUSR1, self.handler)
        
        while True :
        
            self.lock.acquire()
            
            self.my_turn()
            
            self.game_lock.release()
        
        
if __name__ == "__main__" :
    hand1=[22,11,2,18,7]
    hand2=[11,8,5,23,16]
    hand3=[1,18,9,21,19]
    hands=[hand1,hand2,hand3]
    
    
    player = Player(0,hands,153,[20,123,23131],[456,564,456,3455],[435,453,53],3,1,2)
    
    player.my_turn()
    