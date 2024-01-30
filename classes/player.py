from multiprocessing import Array ,Value, Semaphore
from os import system, kill, getpid
import signal
import socket

class Player :
    
    def __init__(self, id, hands, lock,suites,number_players, fuse, info,port):
        self.id = id
        self.number_players = number_players
        self.lock = lock

        self.hand=hands[id]
        self.hands=hands

        self.suites = suites

        self.fuse = fuse
        self.info = info

        self.colors = ["red", "blue", "green", "black", "white"]

        self.port=port




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


    def draw_card(self,index):
        message = f"{self.id} draw"
        self.tcp_socket.send(message.encode())



    def give_info(self,neighbor):
        check_choice=False
        while not check_choice:
            choice = input("Voulez-vous donner une information sur une couleur ou un chiffre ? ").lower()
            if choice =="couleur" or choice=="chiffre":
                check_choice=True
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
            message = f"{self.id} info {neighbor}"
            self.tcp_socket.send(message.encode())
            
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
            message = f"{self.id} info {neighbor}"
            self.tcp_socket.send(message.encode())
            
        else:
            print("Choix non valide. Veuillez choisir 'couleur' ou 'chiffre'.")


    def discard(self,index):
        if index<len(self.hand):
            card=self.hand[index]
            message = f"{self.id} discard {card}"
            self.tcp_socket.send(message.encode())
        else :
            print(f"La carte n'existe pas")
        self.draw_card(index)

    def play_card(self,index_card,index_suites):
        if self.hand[index_card]!=-1:
                card=self.hand[index_card]
                card_color=card//5
                card_number=card%5+1

                vide=False
                #On test si la liste souhaitée est vide 
                if len(self.suites[index_suites])==0:
                    vide=True

                test_color=True
                for i in range(len(list(self.suites))):
                    #On regarde pour les suites non vides autre que celles on l'on veut jouer si la couleur n'est pas deja utilisée
                    if len(self.suites[i])!=0 and i!=index_suites:  
                        if self.suites[i][0]//5==card_color:
                            test_color=False

                if test_color==False:  #La couleur est deja dans un autre suite 
                    self.discard(index_card)
                else:

                    if vide:
                        #Si notre carte est un 1 on la place sinon on la jette
                        if card_number==1:
                            message = f"{self.id} play {index_card} {index_suites}"
                            self.tcp_socket.send(message.encode())

                        else:
                            self.discard(index_card)
                    else: 
                        last_card=self.suites[index_suites][len(self.suites[index_suites])-1]
                        #Si notre carte est bien la carte de la meme couleur incrementée de 1 on la place, sinon on la jette
                        if last_card//5==card_color and last_card%5+1==card_number-1:
                            message = f"{self.id} play {index_card} {index_suites}"
                            self.tcp_socket.send(message.encode())
                        else:
                            self.discard(index_card)


    def my_turn(self):
        # Afficher toutes les suites avec la fonction show_cards
        for i in range(len(self.suites)):
            print(f"Suite {i} : \n")
            self.show_cards(self.suites[i])
        
        # Afficher toutes les mains sauf celle avec l'index self.id
        for i in range(len(self.hands)):
            if i != self.id:
                print(f"Main du joueur {i}:\n")
                self.show_cards(self.hands[i])
        
        if self.info > 0:
            action = input("Voulez-vous donner une information (information) ou jouer une carte (jouer) ? ")
            while action != "information" and action != "jouer":
                action = input("Veuillez entrer 'information' pour donner une information ou 'jouer' pour jouer une carte : ")
        else:
            print("Vous n'avez pas de jeton d'information vous pouvez seulement jouer")
            action = "jouer"

        if action == "information":
            player_num = int(input(f"À quel joueur voulez-vous donner une information ? (0-{self.number_players-1}): "))

            while player_num < 1 or player_num > self.number_players - 1:
                player_num = int(input(f"Veuillez entrer un numéro de joueur valide (0-{self.number_players-1}): "))
            self.give_info(player_num)

        else:
            card_index = int(input(f"Quelle carte voulez-vous jouer ? (0-{len(self.hands[0])-1}): "))

            while card_index < 0 or card_index >= len(self.hands[0]):
                card_index = int(input(f"Veuillez entrer un numéro de carte valide (0-{len(self.hands[0])-1}): "))

            suite_index = int(input(f"Dans quelle suite voulez-vous jouer la carte ? (0-{len(self.suites)-1}): "))

            while suite_index < 0 or suite_index >= len(self.suites):
                suite_index = int(input(f"Veuillez entrer un numéro de suite valide (0-{len(self.suites)-1}): "))

            self.play_card(card_index, suite_index)
                    
                


                            
            
    
    def game_on(self) :
        
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect(("localhost", self.port))
        
        while True :
        
            self.lock.acquire()

            print(f"lock {self.id} acquired")    
            
            input("")
            
            
            
            self.my_turn()
            
        
        
if __name__ == "__main__" :
    hand1=[22,11,2,18,7]
    hand2=[11,8,5,23,16]
    hand3=[1,18,9,21,19]
    hands=[hand1,hand2,hand3]
    
    
    player = Player(0,hands,153,[20,123,23131],[456,564,456,3455],[435,453,53],3,1)
    player.show_cards(player.hand)
    player.my_turn()
    