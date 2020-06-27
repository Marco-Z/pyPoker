from player import Player
from poker import Poker
from enum import Enum


class Statuses(Enum):
    UPCOMING = "upcoming"
    ONGOING = "ongoing"
    COMPLETED = "completed"


class Turns(Enum):
    BLIND = "blind"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"


class PokerTurn:
    def __init__(self, name):
        self.name = name
        self.status = Statuses.UPCOMING
        self.bets = {}

    def start(self, players, deck, first_player):
        self.deck = deck
        self.players = players
        assert first_player in players
        self.first_player = first_player
        self.status = Statuses.ONGOING
        self.bets = {player: 0 for player in self.players}
        self.current_player = self.first_player
        self.calling_players = set()

        return [], deck

    def end(self):
        self.status = Statuses.COMPLETED

    def get_bet(self):
        return max(bet for player, bet in self.bets.items())

    def in_game_players(self):
        return [player for player in self.players if player.cards]

    def is_even(self):
        return (
            len(
                {
                    bet
                    for player, bet in self.bets.items()
                    if player in self.in_game_players()
                }
            )
            == 1
        )

    def is_completed(self):
        return self.is_even() and set(self.in_game_players()) == self.calling_players

    def do(self, action, player=None):
        player = player or self.current_player
        turn_bet = self.get_bet()
        bet = player.do(action, turn_bet, self.bets[player])
        if bet is None:
            print("Unavailable action, try again")
            return

        all_in_call = action == Player.Actions.ALL_IN and self.bets[player] + bet == turn_bet

        if action in [Player.Actions.CALL, Player.Actions.CHECK] or all_in_call:
            self.calling_players.add(player)
        if action in [
            Player.Actions.CALL,
            Player.Actions.RAISE,
            Player.Actions.BET,
            Player.Actions.ALL_IN,
        ]:
            self.bets[player] += bet

        if self.bets[player] > turn_bet:
            self.calling_players = set([player])
        self.finish_player_turn()

    def finish_player_turn(self):
        self.current_player = self.next_player()

    def next_player(self):
        in_game_players_and_current = [
            player
            for player in self.players
            if player == self.current_player or player.cards
        ]
        return in_game_players_and_current[
            (in_game_players_and_current.index(self.current_player) + 1)
            % len(in_game_players_and_current)
        ]


class Blind(PokerTurn):
    def __init__(self):
        super().__init__(Turns.BLIND)

    def start(self, players, deck, first_player, dealer=None, small_blind=10):
        self.dealer = dealer or players[0]
        assert self.dealer in players
        dealer_idx = players.index(self.dealer)

        small_blind_player_idx = (dealer_idx + 1) % len(players)
        self.small_blind_player = players[small_blind_player_idx]
        self.small_blind = small_blind

        big_blind_player_idx = (dealer_idx + 2) % len(players)
        self.big_blind_player = players[big_blind_player_idx]
        self.big_blind = 2 * small_blind

        rest_of_the_deck = Poker.deal(players, deck=deck)

        first_player = players[(big_blind_player_idx + 1) % len(players)]
        super().start(players, rest_of_the_deck, first_player=first_player)

        self.bets[self.small_blind_player] += self.small_blind_player.bet(
            self.small_blind
        )
        self.bets[self.big_blind_player] += self.big_blind_player.bet(self.big_blind)

        print("\n".join(["=" * 80, "Place your bets!", "=" * 80]))

        return [], rest_of_the_deck


class Flop(PokerTurn):
    def __init__(self):
        super().__init__(Turns.FLOP)

    def start(self, players, deck, first_player):
        super().start(players, deck, first_player=first_player)

        deck.pop(0)  # Discard one
        self.flop, rest_of_the_deck = deck[:3], deck[3:]

        print("\n".join(["=" * 80, "The flop", "=" * 80]))

        return self.flop, rest_of_the_deck


class Turn(PokerTurn):
    def __init__(self):
        super().__init__(Turns.TURN)

    def start(self, players, deck, first_player):
        super().start(players, deck, first_player=first_player)

        deck.pop(0)  # Discard one
        self.turn = [deck.pop(0)]

        print("\n".join(["=" * 80, "The turn", "=" * 80]))

        return self.turn, deck


class River(PokerTurn):
    def __init__(self):
        super().__init__(Turns.RIVER)

    def start(self, players, deck, first_player):
        super().start(players, deck, first_player=first_player)

        deck.pop(0)  # Discard one
        self.river = [deck.pop(0)]

        print("\n".join(["=" * 80, "And the river!", "=" * 80]))

        return self.river, deck


TEXAS_HOLD_EM_TURNS = [Blind(), Flop(), Turn(), River()]
