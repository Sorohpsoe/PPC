from classes.game import Game


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

    num_players = 2
    game = Game(num_players,6659)
    game.suites[0]=[0,1,2,3,4]
    game.suites[1]=[5,6,7,8]
    game.hands[0]=[9,1,2,1,5]
    
    
    game.start()