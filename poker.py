from collections import Counter
from random import shuffle
from enum import Enum


class Poker:

    RANKS = "23456789➉JQKA"
    SUITS = "♠♣♥♦"
    DECK = [r + s for r in RANKS for s in "♠♣♥♦"]

    class Scores(Enum):
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
        (4, 1): Scores.POKER.value,
        (3, 2): Scores.FULL_HOUSE.value,
        (3, 1, 1): Scores.THREE_OF_A_KIND.value,
        (2, 2, 1): Scores.DOUBLE_PAIR.value,
        (2, 1, 1, 1): Scores.PAIR.value,
        (1, 1, 1, 1, 1): Scores.HIGH_CARD.value,
    }

    def get_score(self, counts, is_straight, is_flush):
        return max(
            self.count_rankings[counts],
            self.Scores.STRAIGH.value * is_straight
            + self.Scores.FLUSH.value * is_flush,
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

    def deal(self, players_count, player_cards=5, shared_cards=0, deck=DECK[:]):
        shuffle(deck)
        return (
            [
                deck[i * player_cards : i * player_cards + player_cards]
                for i in range(players_count)
            ],
            deck[
                players_count * player_cards : players_count * player_cards
                + shared_cards
            ],
            deck[players_count * player_cards + shared_cards :],
        )

    def poker(self, players, player_cards, shared_cards):
        players_cards, shared, _ = self.deal(
            players, player_cards=player_cards, shared_cards=shared_cards
        )
        print("players_cards: ", players_cards)
        print("shared: ", shared)
        hands = [private + shared for private in players_cards]
        winners, (score, ranks) = self.allmax(hands, key=self.hand_rank)
        print(f"The winner is {winners} with {self.Scores(score).name}, {ranks}!")

    def classic_poker(self, players):
        return self.poker(players, player_cards=5, shared_cards=0)

    def hold_em_poker(self, players):
        return self.poker(players, player_cards=2, shared_cards=5)

    def play(self):
        number_of_players = int(input("How many players? ") or 2)

        bet = 0

        players_cards, _, rest_of_the_deck = self.deal(
            number_of_players, player_cards=2
        )

        your_cards, *others_cards = players_cards
        print(f"Your cards are: {' '.join(your_cards)}")

        bet += int(input("Your bet: ") or 0)
        rest_of_the_deck.pop(0)
        flop, rest_of_the_deck = rest_of_the_deck[:3], rest_of_the_deck[3:]
        print(f"The FLOP: {' '.join(flop)}")

        bet += int(input("Your bet: ") or 0)
        rest_of_the_deck.pop(0)
        turn = rest_of_the_deck.pop(0)
        print(f"The TURN: {turn}")

        bet += int(input("Your bet: ") or 0)
        rest_of_the_deck.pop(0)
        river = rest_of_the_deck.pop(0)
        print(f"And the RIVER: {river}")

        bet += int(input("Your bet: ") or 0)
        shared = flop + [turn] + [river]

        your_hand = your_cards + shared
        hands = [private + shared for private in players_cards]
        winners, (score, ranks) = self.allmax(hands, key=self.hand_rank)
        print(f"Other players have: {', '.join(' '.join(cards) for cards in others_cards)}")
        print(
            f"The winner{' is' if len(winners) == 1 else 's are'} {' '.join([' '.join(w[:2]) for w in winners])} with {self.Scores(score).name}!"
        )
        if your_hand in winners:
            print(f"Congratulations! You won ${bet*number_of_players}")
        else:
            print(f"You suck! You lost ${bet}")

Poker().play()
