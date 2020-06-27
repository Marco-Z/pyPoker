from player import Player
from round import Round
from poker import Poker
from random import shuffle, choice


def play_round():
    number_of_players = int(input("How many players? ") or 2)
    game = Round(players=[Player() for _ in range(number_of_players)])
    game.start()

    while not game.is_finished:
        current_bet = game.get_turn_bet()
        current_player_bet = game.get_turn_bet_of_player()

        print(game)
        print()

        game.prompt_for_action()


if __name__ == "__main__":
    play_round()
