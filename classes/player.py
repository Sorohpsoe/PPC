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
    