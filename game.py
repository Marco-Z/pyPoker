from player import Player
from round import Round


class Game:
    def __init__(self, players, initial_small_blind=10):
        self.players = players
        self.small_blind = 10

    def get_players_with_money(self):
        return [p for p in self.players if p.money > 0]

    def play(self):
        while len(self.get_players_with_money()) > 1:
            poker_round = Round(players=self.players, small_blind=self.small_blind)
            poker_round.play()
            input()


if __name__ == "__main__":
    number_of_players = int(input("How many players? ") or 2)
    game = Game([Player() for _ in range(number_of_players)])
    game.play()
