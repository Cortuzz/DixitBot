from random import shuffle


class Game:
    def __init__(self, player):
        self.game_started = False
        self.players = [player]
        self.lead = 0
        self.correct_card = None
        self.waiting_for_lead = True
        self.waiting_for_pixs = False
        self.lead_phrase = None
        self.card_number = 0
        self.deck = []

    def set_album(self, items):
        self.deck = []
        for item in items:
            self.deck.append("photo" + str(item['owner_id']) + "_" + str(item['id']))

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
            if not player.answer and player != self.players[self.lead]:
                return False

        for player in self.players:
            player.answer = False

        return True

    def change_lead(self):
        self.lead = (self.lead + 1) % len(self.players)

        for pl in self.players:
            pl.cards.append(self.take_cards(1)[0])
