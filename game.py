from random import shuffle


class Game:
    def __init__(self, player):
        self.players = [player]
        self.pixs_root = 457239017 - 1
        self.correct_card = None
        self.card_number = 0
        self.deck = []

        self.parse_deck()

    def parse_deck(self):
        with open("words.txt") as w:
            for line in w:
                self.deck.append(line.split("\t"))

        shuffle(self.deck)

    def set_album(self, owner, album):
        pass


    def take_cards(self, count):
        cards = []

        for i in range(count):
            cards.append(self.deck[self.card_number])
            self.card_number += 1

            if self.card_number == len(self.deck):
                self.card_number = 0
                shuffle(self.deck)

        return cards

    def check_next_round(self):
        for player in self.players:
            if not player.answer:
                return False

        for player in self.players:
            player.answer = False
        return True
