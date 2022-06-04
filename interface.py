import locale
import traceback
from player import Player


class BotInterface:
    def __init__(self):
        locale.setlocale(locale.LC_ALL, '')
        self.commands = {'старт': self.get_cards}

        self.admin_id = 375795594
        self.players = dict()

    def try_command(self, command, player_id, *args):
        if player_id not in self.players:
            self.add_player(player_id)

        player = self.get_player(player_id)
        try:
            method = self.commands[command]
        except KeyError:
            return

        try:
            if len(args):
                return method(player, args)

            return method(player)
        except TypeError:
            return f"Ошибка при выполнении команды {command}\n" \
                   f"Аргументы: {args}\n{traceback.format_exc()}"

    def get_player(self, player_id) -> Player:
        return self.players[player_id]

    def add_player(self, player_id):
        player = Player(player_id)
        player.parse_deck()
        self.players.update({player_id: player})

    def get_cards(self, player):
        return "", player.take_cards(5)
