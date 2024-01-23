from multiprocessing import Array ,Value


class Player :
    def __init__(self,id,hands,lock,suites,draw_pile,discard_pile):

        self.id=id
        self.hand=hands[id]
        self.lock=lock
        self.suites=suites
        self.draw_pile=draw_pile
        self.discard_pile=discard_pile
        

    def discard(self,index):
        if self.hand[index]!=-1:
            card=self.hand[index]
            self.discard_pile.append(card)
            self.hand[index]=-1
            print(f"La carte :{card} a ete defaussee")
        else :
            print(f"La carte n'existe pas")
        self.draw_card(index)

        

    def ask_info(self,neighbor):
        pass

    def play_card(self,index_card,index_suites):
        
        """
        Plays a card from the player's hand and adds it to the specified suite if possible, else it discards it. 

        Args:
            index_card (int): The index of the card to be played from the player's hand.
            index_suites (int): The index of the suite where the card will be added.

        Returns:
            None
        """
        
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
                




           


    def draw_card(self,index):
        pass        

        
    