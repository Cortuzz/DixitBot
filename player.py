from random import shuffle


class Player:
    def __init__(self, player_id):
        self.id = player_id
        self.deck = []
        self.card_number = 0

    def parse_deck(self):
        with open("words.txt") as w:
            for line in w:
                self.deck.append(line.split("\t"))

        shuffle(self.deck)

    def take_cards(self, count):
        cards = []

        for i in range(count):
            cards.append(int((self.deck[self.card_number][0]).split(".")[0]))
            self.card_number += 1

            if self.card_number == len(self.deck):
                self.card_number = 0
                shuffle(self.deck)

        return cards
