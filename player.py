from random import choice
from enum import Enum


class Action(Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all in"


class Player:
    def __init__(self, name=None, money=1000):
        self.money = money
        self.cards = []
        self.name = f"Player {name or choice('♚♛♜♝♞♟♔♕♖♗♘♙')}"

    def bet(self, amount=0):
        bet_amount = min(amount, self.money)
        self.money -= bet_amount
        return bet_amount

    def __repr__(self):
        return f"{self.name}: Cards: {' '.join(self.cards) if self.cards else 'None'}, Money: {str(self.money).rjust(4)}$"

    def __str__(self):
        return self.__repr__()

    def _available_actions(self, turn_bet, player_bet):
        return [
            Action.FOLD if turn_bet > player_bet else None,
            Action.CALL if self._can_call(turn_bet, player_bet) else None,
            Action.BET
            if self.money > 0 and self._can_check(turn_bet, player_bet)
            else None,
            Action.RAISE if self._can_call(turn_bet, player_bet) else None,
            Action.CHECK if self._can_check(turn_bet, player_bet) else None,
            Action.ALL_IN if turn_bet >= player_bet and self.money > 0 else None,
        ]

    def is_all_in(self):
        return self.money == 0

    def _can_call(self, turn_bet, player_bet):
        return turn_bet > player_bet and self.money > turn_bet - player_bet

    def _can_check(self, turn_bet, player_bet):
        return turn_bet == player_bet

    def actions(self, turn_bet, player_bet):
        return [
            action for action in self._available_actions(turn_bet, player_bet) if action
        ]

    def do(self, action, turn_bet, player_bet):
        if action in self._available_actions(turn_bet, player_bet):
            print(f"{self.name} {action.value}ed")
            if action == Action.FOLD:
                self.cards = []
                return -1
            if action == Action.CALL:
                return self.bet(turn_bet - player_bet)
            if action == Action.BET:
                return self.bet(int(input("Bet: ")))
            if action == Action.RAISE:
                return (
                    turn_bet
                    - player_bet
                    + self.bet(int(input(f"Raise: {turn_bet} + ")))
                )
            if action == Action.CHECK:
                return 0
            if action == Action.ALL_IN:
                return self.bet(self.money)
