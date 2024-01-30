from multiprocessing import Semaphore
import socket

class Player :
     
    def __init__(self, id, hands, lock,suites,number_players, tokens,port,queue):
        """_summary_

        Args:
            id (int): id of the player
            hands (list): hands of all players
            lock (list): lock of the player
            suites (list): all the suites in the game
            number_players (int): number of players in the game
            tokens (dict): info and fuses tokens and state of the game
            port (str): Port to which connect with the server
            queue (queue): queue to communicate with the server
        """
        self.id = id
        self.number_players = number_players
        self.lock = lock
        self.hand=hands[id]
        self.hands=hands
        self.suites = suites
        self.tokens=tokens
        self.colors = ["red", "blue", "green", "yellow", "white"]
        self.port=port
        #Sets the hints of the color and number of the cards to false
        self.indice=[ [False,False] for i in range(5)]
        self.queue=queue




    def show_cards(self,cartes) :
        """
        Show a given list of cards

        Args:
            cartes (list): list of cards to show
        """
        
        #Starts of the different lines of the cards
        top = "╔"
        color_text = "║"
        number_text = "║"
        bottom = "╚"
    
        #For each card in the list we add the corresponding line to the card's string representation 
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
            if color == "yellow" :
                top += "═══════╦"
                color_text += "\033[33m"+color+"\033[0m ║"
                number_text += "   \033[33m"+str(number)+"\033[0m   ║"
                bottom += "═══════╩"
            if color == "white" :
                top += "═══════╦"
                color_text += " \033[37m"+color+"\033[0m ║"
                number_text += "   \033[37m"+str(number)+"\033[0m   ║"
                bottom += "═══════╩"
      
        #We remove the last character of each line and add the corresponding character to close the card
        top = top[:-1] + "╗"
        color_text = color_text[:-1] + "║"
        number_text = number_text[:-1] + "║"
        bottom = bottom[:-1] + "╝"
        
        #If the list is empty we print an empty card, otherwise we print all the cards with their respective lines
        if len(top)!=1: 
            print(top)
            print(color_text)
            print(number_text)
            print(bottom)
        else:
            print("Suite vide\n")

    def give_info(self,neighbor):
        """
        Make the player choose between giving a color or a number information to a neighbor

        Args:
            neighbor (int): id of the neighbor to give the information to
        """
        
        #Loop until the player chooses a valid option
        check_choice=False
        while not check_choice:
            choice = input("Voulez-vous donner une information sur une couleur ou un chiffre ? ").lower()
            if choice =="couleur" or choice=="chiffre":
                check_choice=True
            else:
                print ("Choix incorrect")
                
        #If the player chooses to give a color information
        if choice == "couleur":
            
            #Loop until the player chooses a valid color
            valid_color = False
            while not valid_color:
                color_input = input("Veuillez entrer une couleur : ").lower()
                if color_input in self.colors:
                    valid_color = True
                else:
                    print("Couleur invalide. Veuillez choisir une couleur parmi :", self.colors)
            
            #Send the information to the neighbor using the queue
            self.send_message_q(f"{neighbor}{color_input[0]}")
            
            #Send the information to the game
            message = f"{self.id} info {neighbor}"
            self.tcp_socket.send(message.encode())
        
        #Elif the player chooses to give a number information
        elif choice == "chiffre":
            
            #Loop until the player chooses a valid number
            valid_number = False
            while not valid_number:
                number_input = input("Veuillez entrer un chiffre entre 1 et 5 : ")
                if number_input.isdigit() and 1 <= int(number_input) <= 5:
                    valid_number = True
                else:
                    print("Chiffre invalide. Veuillez choisir un chiffre entre 1 et 5.")
            
            #Send the information to the neighbor using the queue
            self.send_message_q(f"{neighbor}{number_input}")
            
            #Send the information to the game
            message = f"{self.id} info {neighbor}"
            self.tcp_socket.send(message.encode())
            

    def discard(self,index):
        """
        Send the information to the game that the player discarded a card at index 'index'.
        Put the hints of the color and number of the card to false for this position.

        Args:
            index (int): index of the card to discard
        """
        if index<len(self.hand):
            card=self.hand[index]

            print(f"Mauvais choix ! Vous avez jeté cette carte :")
            self.show_cards([card])

            message = f"{self.id} discard {index}"
            self.indice[index][0]=0
            self.indice[index][1]=0
            self.tcp_socket.send(message.encode())

        else :
            print(f"La carte n'existe pas")

    def play_card(self,index_card,index_suites):
        """
        Test if the card can be played, if not discard it. Then send the information to the game.

        Args:
            index_card (int): index of the card to play
            index_suites (int): index of the suite to play the card in
        """
        
        #Get the color and number of the card
        card=self.hand[index_card]
        card_color=card//5
        card_number=card%5+1

        #Look if the suite is empty
        vide=False        
        if len(self.suites[index_suites])==0:
            vide=True

        #Test if the color is already in another suite
        test_color=True
        for i in range(len(list(self.suites))):
            if len(self.suites[i])!=0 and i!=index_suites:  
                if self.suites[i][0]//5==card_color:
                    test_color=False

        #If the color is not in another suite, test if the card can be played.
        #Else discard the card
        if test_color==False:
            self.discard(index_card)
        else:
            
            #If the suite is empty, we can only play a 1.
            #If it's not a 1, discard the card.
            if vide:
                if card_number==1:
                    print("\nBon choix ! votre carte a été ajoutée à la suite\n")
                    self.indice[index_card][0]=0
                    self.indice[index_card][1]=0
                    message = f"{self.id} play {index_card} {index_suites}"
                    self.tcp_socket.send(message.encode())
                else:
                    self.discard(index_card)
                    
            #If the suite is not empty, get the last card of the suite
            #The card played must be the same color and the number must be incremented by 1
            #If not discard the card
            else: 
                last_card=self.suites[index_suites][len(self.suites[index_suites])-1]
                if last_card//5==card_color and last_card%5+1==card_number-1:
                    print("\nBon choix ! votre carte a été ajoutée à la suite\n")
                    self.indice[index_card][0]=0
                    self.indice[index_card][1]=0
                    message = f"{self.id} play {index_card} {index_suites}"
                    self.tcp_socket.send(message.encode())
                    
                    #If the card played is a 5, add a info token
                    if card_number==5:
                        self.tokens["info"]+=1
                
                else:
                    self.discard(index_card)

    def send_message_q(self,msg):
        """
        Send a message to the server using the queue

        Args:
            msg (str): message to send
        """
        self.queue.put(msg)  

    def get_all_msg(self):
        """
        Get all the messages in the queue

        Returns:
            str: messages in the queue
        """
        message = []
        while not self.queue.empty():
            message = self.queue.get()
        return message
    
    def set_indice_and_reload(self):
        """
        Copy the queue and set the hints of the color and number of the cards to true
        Replace the message not destined to the player in the queue
        """
        
        copie_queue = list(self.get_all_msg())
        data_to_resend = ""

        for i in range (0,len(copie_queue),2):
            ID=int(copie_queue[i])
            info=copie_queue[i+1]
            
            #If the message is destined to the player, set the hints of the color and number of the cards to true
            if ID == self.id:
                if info=='1' or info=='2' or info=='3' or info=='4' or info=='5':
                    for i in range(len(self.hand)):
                        if self.hand[i]%5+1==int(info):
                            self.indice[i][1] = True
                else:
                    for i in range(len(self.hand)):
                        if self.colors[self.hand[i]//5][0]==info:
                            self.indice[i][0] = True
            #Else, add the message to the string to resend
            else:
                data_to_resend+=f"{ID}"
                data_to_resend+=info
        
        #Resend the messages not destined to the player
        self.send_message_q(f"{data_to_resend}")


    def show_indice(self):
        """
        Show the hints of the color and number of the cards given by the other players
        """
        for i in range(len(self.indice)):
            if self.indice[i][0] == True:
                print("La carte ",i," est de couleur ",self.colors[self.hand[i]//5])
            if self.indice[i][1] == True:
                print("La carte ",i," est de valeur ",self.hand[i]%5+1)


    def my_turn(self):
        """
        Decision tree of te player's choices during his turn
        """
        
        #Show the suites
        for i in range(len(self.suites)):
            print(f"Suite {i} : \n")
            self.show_cards(self.suites[i])
        
        #Show the hands of the other players
        for i in range(len(self.hands)):
            if i != self.id:
                print(f"Main du joueur {i}:\n")
                self.show_cards(self.hands[i])

        #Get the messages in the queue and set the hints of the color and number of the cards to true
        self.set_indice_and_reload()
        #Show the hints of the color and number of the cards given by the other players
        self.show_indice()

        #Tell the player how many information and fuse tokens he has left
        print(f"\nVous avez {self.tokens['fuse']} jetons de fuse et {self.tokens['info']} jetons d'information\n")
        
        #If the player has no informations tokens left, he can only play a card
        if self.tokens["info"] > 0:
            action = input("Voulez-vous donner une information (information) ou jouer une carte (jouer) ? ")
            while action != "information" and action != "jouer":
                action = input("Veuillez entrer 'information' pour donner une information ou 'jouer' pour jouer une carte : ")
        else:
            print("Vous n'avez pas de jeton d'information vous pouvez seulement jouer")
            action = "jouer"

        if action == "information":
            
            #Loop until the player chooses a valid player
            player_num = input(f"À quel joueur voulez-vous donner une information ? (0-{self.number_players-1}): ")
            check_num = False
            while not check_num:
                try:
                    player_num = int(player_num)
                    if 0 <= player_num <= self.number_players - 1:
                        check_num = True
                    else:
                        player_num = input(f"Veuillez entrer un numéro de joueur valide (0-{self.number_players-1}): ")
                except:
                    player_num = input(f"Veuillez entrer un numéro de joueur valide (0-{self.number_players-1}): ")
                    
            #Give the information to the player
            self.give_info(player_num)

        else:
            
            #Loop until the player chooses a valid card and suite
            card_index = input(f"Quelle carte voulez-vous jouer ? (0-{len(self.hand)-1}): ")
            check_index = False
            while not check_index:
                try:
                    card_index=int(card_index)
                    if 0 <= card_index <= len(self.hand) - 1:
                        check_index = True
                    else:
                        card_index = input(f"Veuillez entrer un numéro de carte valide (0-{len(self.hand)-1}): ")
                except:
                    card_index = input(f"Veuillez entrer un numéro de carte valide (0-{len(self.hand)-1}): ")
            
            suite_index = input(f"Dans quelle suite voulez-vous jouer la carte ? (0-{len(self.suites)-1}): ")
            check_index = False
            while not check_index:
                try:
                    suite_index = int(suite_index)
                    if 0 <= suite_index <= len(self.suites) - 1:
                        check_index = True
                    else:
                        suite_index = input(f"Veuillez entrer un numéro de suite valide (0-{len(self.suites)-1}): ")
                except:
                    suite_index = input(f"Veuillez entrer un numéro de suite valide (0-{len(self.suites)-1}): ")
                    
            #Play the card
            self.play_card(card_index, suite_index)

                     
  
    def game_on(self) :
        """
        Main loop of the player
        """
        
        #Connect to the game
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect(("localhost", self.port))
        
        while True :

            #Wait for the lock to be released, it's the player's turn
            self.lock.acquire()

            #Check if the game is over
            if self.tokens["game_over"]:
                
                #Close the socket and break the loop
                self.tcp_socket.close()
                break
            
            #If the game is not over, it's the player's turn
            self.my_turn()