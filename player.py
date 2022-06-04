from random import shuffle


class Player:
    def __init__(self, player_id):
        self.id = player_id
        self.player_score = 0
        self.game = None
        self.answer = False


