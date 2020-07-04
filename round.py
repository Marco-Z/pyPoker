from player import Player, Action
from poker import Poker
from turn import Status, Blind, Flop, Turn, River
from enum import Enum
from functools import reduce


class Round:
    TEXAS_HOLD_EM_TURNS = lambda small_blind: [
        Blind(small_blind=small_blind),
        Flop(),
        Turn(),
        River(),
    ]

    def __init__(self, players=[Player(), Player()], small_blind=10):
        assert len(players) >= 2
        self.is_finished = False

        self.players = players

        self.dealer = players[0]

        small_blind_player_idx = 1 % len(players)
        self.small_blind_player = players[small_blind_player_idx]
        self.small_blind = small_blind

        big_blind_player_idx = 2 % len(players)
        self.big_blind_player = players[big_blind_player_idx]
        self.big_blind = 2 * small_blind

        self.deck = Poker.DECK
        self.shared_cards = []
        self.turns = Round.TEXAS_HOLD_EM_TURNS(small_blind)
        self.start_list = (
            self.players[small_blind_player_idx:]
            + self.players[:small_blind_player_idx]
        )

    def _start_next_turn(self, players, deck, first_player):
        upcoming_rounds = [
            turn for turn in self.turns if turn.status == Status.UPCOMING
        ]
        if not upcoming_rounds:
            self.showdown()
            self.is_finished = True
            return [], []
        self.current_turn = upcoming_rounds[0]
        self.last_betting_player = self.big_blind_player  # TODO if he's playing
        return self.current_turn.start(players, deck, first_player)

    def showdown(self):
        players = self.in_game_players()
        print("\n".join(["=" * 80, "Showdown", "=" * 80]))
        winners, score, ranks = Poker().showdown(players, self.shared_cards)

        prize = self.get_pot() / len(winners)
        for player in winners:
            player.money += prize

        print(f"Shared cards: {', '.join(self.shared_cards)}")
        print("\n".join(str(p) for p in players))
        print(
            f"The winner {'is' if len(winners) == 1 else 'are'} {' and '.join([p.name for p in winners])} with {Poker.Score(score).name}!"
        )

    def _end_this_turn(self):
        self.current_turn.end()

    def start(self):
        shared_cards, self.deck = self._start_next_turn(self.players, Poker.DECK, None)
        self.shared_cards += shared_cards

    def starting_player(self):
        return next(player for player in self.start_list if player.cards)

    def role(self, player):
        return (
            "☆"
            if player == self.dealer
            else "⛀"
            if player == self.small_blind_player
            else "⛁"
            if player == self.big_blind_player
            else " "
        )

    def get_turn_bet(self, turn=None):
        turn = turn or self.current_turn
        return turn.get_bet()

    def get_turn_bet_of_player(self, player=None, turn=None):
        turn = turn or self.current_turn
        player = player or turn.current_player
        return turn.bets[player]

    def get_total_bet_of_players(self):
        merge = lambda x, y: {k: x.get(k, 0) + y.get(k, 0) for k in set(x) | set(y)}
        return reduce(merge, [turn.bets for turn in self.turns])

    def get_total_bet_of_player(self, player=None):
        player = player or self.current_turn.current_player
        return self.get_total_bet_of_players().get(player)

    def get_pot(self):
        return sum(self.get_total_bet_of_players().values())

    def early_winner(self):
        self.is_finished = True
        in_game_players = self.in_game_players()
        assert len(in_game_players) == 1
        winner = in_game_players[0]
        winner.money += self.get_pot()
        display = [
            "=" * 80,
            "Everybody else folded",
            "=" * 80,
            f"Shared cards: {', '.join(self.shared_cards)}"
            if self.shared_cards
            else None,
            f"The winner is {winner.name}!",
        ]
        print("\n".join([line for line in display if line]))

    def prompt_for_action(self):
        input_action = input(
            f"Actions: [{', '.join(action.value for action in self.actions())}]: "
        )
        if input_action not in [a.value for a in Action]:
            print(f"{input_action} is not a valid action, please try again")
            return self.prompt_for_action()

        self.do(Action(input_action))
        if len(self.in_game_players()) == 1:
            return self.early_winner()
        self.update_turn_status()

    def update_turn_status(self):
        if self.current_turn.is_completed():
            self._end_this_turn()
            shared_cards, self.deck = self._start_next_turn(
                self.in_game_players(), self.deck, self.starting_player()
            )
            self.shared_cards += shared_cards
            if not self.is_finished:
                self.update_turn_status()

    def do(self, action, player=None, turn=None):
        turn = turn or self.current_turn
        player = player or turn.current_player
        turn.do(action, player=player)

    def in_game_players(self):
        return [player for player in self.players if player.cards]

    def actions(self, player=None, turn=None):
        turn = turn or self.current_turn
        player = player or turn.current_player
        return player.actions(
            self.get_turn_bet(turn=turn),
            self.get_turn_bet_of_player(player=player, turn=turn),
        )

    def _standings(self):
        bet = (
            lambda player: f"Bet: {str(self.get_total_bet_of_player(player)).rjust(4)}$"
        )
        return "\n".join(
            [
                " ".join(
                    [
                        "->" if self.current_turn.current_player == player else "  ",
                        self.role(player),
                        str(player),
                        bet(player),
                    ]
                )
                for player in self.in_game_players()
            ]
        )

    def play(self):
        self.start()
        while not self.is_finished:

            print(self)
            print()

            self.prompt_for_action()

    def __str__(self):
        standings = self._standings()
        # last = f"Last betting player: {self.last_betting_player.name}"
        shared = (
            f"Shared cards: {', '.join(self.shared_cards)}"
            if self.shared_cards
            else None
        )
        pot = f"Pot: {self.get_pot()}$"

        info = [value for value in [standings, shared, pot] if value]

        return "\n".join(info)
