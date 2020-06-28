from collections import Counter
from random import shuffle, choice
from enum import Enum


class Poker:

    RANKS = "23456789➉JQKA"
    SUITS = "♠♣♥♦"
    DECK = [r + s for r in RANKS for s in "♠♣♥♦"]

    class Score(Enum):
        ROYAL_FLUSH = 9
        POKER = 7
        FULL_HOUSE = 6
        FLUSH = 5
        STRAIGH = 4
        THREE_OF_A_KIND = 3
        DOUBLE_PAIR = 2
        PAIR = 1
        HIGH_CARD = 0

    count_rankings = {
        (4, 1): Score.POKER.value,
        (3, 2): Score.FULL_HOUSE.value,
        (3, 1, 1): Score.THREE_OF_A_KIND.value,
        (2, 2, 1): Score.DOUBLE_PAIR.value,
        (2, 1, 1, 1): Score.PAIR.value,
        (1, 1, 1, 1, 1): Score.HIGH_CARD.value,
    }

    def get_score(self, counts, is_straight, is_flush):
        return max(
            self.count_rankings[counts],
            self.Score.STRAIGH.value * is_straight + self.Score.FLUSH.value * is_flush,
        )

    def limit_counts(self, counts, n=5):
        res = []
        for c in counts:
            if n - c > 0:
                res += [c]
                n -= c
            elif n - c == 0:
                return tuple(res + [c])
            else:
                return tuple(res + [n])
        return tuple(res)

    def unzip(self, groups, playable_cards=5):
        ranks, counts = zip(*groups)
        return ranks[:5], self.limit_counts(counts)

    def hand_rank(self, hand):
        groups = Counter(
            sorted((f"--{Poker.RANKS}".index(r) for r, s in hand), reverse=True)
        ).most_common(5)
        ranks, counts = self.unzip(groups)
        if ranks == (14, 5, 4, 3, 2):
            ranks = (5, 4, 3, 2, 1)
        is_straight = len(ranks) == 5 and max(ranks) - min(ranks) == 4
        is_flush = len({s for r, s in hand}) == 1
        return self.get_score(counts, is_straight, is_flush), ranks

    def allmax(self, iterable, key=lambda x: x):
        best_score = max((key(e) for e in iterable))
        return [el for el in iterable if key(el) == best_score], best_score

    @staticmethod
    def deal(players, player_cards=2, deck=DECK[:]):
        shuffle(deck)
        hands = [
            deck[i * player_cards : i * player_cards + player_cards]
            for i in range(len(players))
        ]

        for player, hand in zip(players, hands):
            player.cards = hand

        rest_of_the_deck = deck[len(players) * player_cards :]
        return rest_of_the_deck

    def poker(self, players, player_cards, shared_cards):
        players_cards, shared, _ = self.deal(
            players, player_cards=player_cards, shared_cards=shared_cards
        )
        print("players_cards: ", players_cards)
        print("shared: ", shared)
        hands = [private + shared for private in players_cards]
        winners, (score, ranks) = self.allmax(hands, key=self.hand_rank)
        print(f"The winner is {winners} with {self.Score(score).name}, {ranks}!")

    def showdown(self, players, shared_cards):
        players_by_cards = {
            tuple(player.cards + shared_cards): player for player in players
        }
        winner_hands, (score, ranks) = self.allmax(
            players_by_cards.keys(), key=self.hand_rank
        )
        winners = [players_by_cards[tuple(winner_hand)] for winner_hand in winner_hands]
        return winners, score, ranks

    def classic_poker(self, players):
        return self.poker(players, player_cards=5, shared_cards=0)

    def hold_em_poker(self, players):
        return self.poker(players, player_cards=2, shared_cards=5)
