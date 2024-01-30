from classes.game import Game
from multiprocessing import Process
import signal
import os


def get_number_of_players():
    is_a_number = False 
    while not is_a_number:
        try:
            num_players = int(input("Enter the number of players (between 2 and 5): "))
            if num_players >= 2 and num_players <= 5:
                is_a_number = True
            else:
                print("Invalid input. Please enter a number between 2 and 5.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
    return num_players

if __name__ == "__main__":

    num_players = get_number_of_players()
    game = Game(num_players,6659)
    game.start()