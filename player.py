from random import shuffle


class Player:
    def __init__(self, player_id):
        self.id = player_id
        self.player_score = 0
        self.game = None
        self.answer = False
        self.is_right = False
        self.picked_own_card = None
        self.picked_card = None
        self.cards = []


