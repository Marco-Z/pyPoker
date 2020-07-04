from player import Player
from round import Round
from math import floor


class Game:
    def __init__(self, players, initial_small_blind=10):
        self.players = players
        self.small_blind = 10
        self.rounds_played = 0
        self.dealer = self.players[0]

    def get_players_with_money(self):
        return [p for p in self.players if p.money > 0]

    def get_small_blind(self):
        return self.small_blind * 2 ** floor(self.rounds_played / len(self.players))

    def get_next_dealer(self):
        possible_dealers = [p for p in self.players if p.money > 0 or p == self.dealer]
        assert len(possible_dealers) > 1
        dealer_index = possible_dealers.index(self.dealer)
        possible_dealers = (
            possible_dealers[dealer_index:] + possible_dealers[:dealer_index]
        )
        return next(p for p in possible_dealers[1:])

    def finish_round(self):
        input()
        self.rounds_played += 1
        players = self.get_players_with_money()
        assert len(players) >= 1
        if len(players) <= 1:
            self.display_winner()
        else:
            self.dealer = self.get_next_dealer()


    def play(self):
        while len(self.get_players_with_money()) > 1:
            poker_round = Round(
                players=self.get_players_with_money(),
                small_blind=self.get_small_blind(),
                dealer=self.dealer,
            )
            poker_round.play()
            self.finish_round()


if __name__ == "__main__":
    number_of_players = int(input("How many players? ") or 2)
    game = Game([Player() for _ in range(number_of_players)])
    game.play()
