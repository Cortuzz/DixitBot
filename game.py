from random import shuffle


class Game:
    def __init__(self, player):
        self.players = [player]
        self.correct_card = None
        self.card_number = 0
        self.deck = []

    def set_album(self, items):
        self.deck = []
        for item in items:
            self.deck.append(["photo" + str(item['owner_id']) + "_" + str(item['id']), item['text'].split(' ')])

        shuffle(self.deck)

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
