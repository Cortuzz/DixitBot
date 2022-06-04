import locale
import random
import traceback

import vk_api

import API
from game import Game
from player import Player


class BotInterface:
    def __init__(self, api: API, token, service_token):
        locale.setlocale(locale.LC_ALL, '')
        self.commands = {'старт': self.start_game, 'результаты': self.results}

        vk = vk_api.VkApi(token=service_token)
        self.service_api = vk.get_api()

        self.api = api
        self.admin_id = 375795594
        self.players = dict()
        self.games = []
        self.chat_id = None
        self.token = token

    def try_command(self, chat_id, command, player_id, *args):
        self.chat_id = chat_id

        if player_id not in self.players:
            self.add_player(player_id)

        player = self.get_player(player_id)

        if self.try_parse_album(player, command):
            return

        try:
            method = self.commands[command]
        except KeyError:
            try:
                if int(command) > 0 and not len(args):
                    method = self.check_correct
                    args = [int(command)]
                else:
                    return
            except:
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
        self.players.update({player_id: player})

    def results(self, player):
        if player.game is None:
            return "Вы не находитесь в игре."

        t = "Результаты:\n"
        for pl in player.game.players:
            t += self.get_name(pl) + ": " + str(pl.player_score) + "\n"

        self.api.response(t, player.id, self.chat_id, "", False)

    def get_unique_tags(self, tags):
        map = dict()

        for card_tags_ind in range(len(tags)):
            card_tags = tags[card_tags_ind]
            for tag in card_tags:
                if tag not in map:
                    map.update({tag: [0, card_tags_ind + 1]})

                map[tag][0] += 1

        uniq_tags = []
        for tag in map:
            if map[tag][0] == 1:
                uniq_tags.append([tag, map[tag][1]])

        return uniq_tags

    def get_name(self, player):
        response = self.api.vk_api.users.get(access_token=self.token, user_ids=player.id)
        return response[0]['first_name'] + ' ' + response[0]['last_name']

    def notify_players(self, notif_player, game):
        name = self.get_name(notif_player)

        for player in game.players:
            self.api.response("Игрок " + name + " присоединился!", player.id, self.chat_id, "")

    def show_games(self):
        t = ""
        for i in range(len(self.games)):
            t += "Игра № " + str(i + 1) + " [" + str(len(self.games[i].players)) + "чел.]"

        return t + "\nПрисоединитесь к существующей (пример: старт 1)\n" \
                   "или создайте свою игру (пример: старт " + str(len(self.games) + 1) + ")" if t \
            else "Еще нет игр!\nСоздайте свою, написав старт 1"

    def show_cards(self, game):
        cards = game.take_cards(5)

        cards_names = []
        cards_tags = []
        for card in cards:
            cards_names.append(card[0])
            cards_tags.append(card[1])
        random_tags = self.get_unique_tags(cards_tags)

        random_tag = random.choice(random_tags)

        game.correct_card = random_tag[1]
        parsed_attach = ""
        for attach in cards_names:
            parsed_attach += attach + ","

        parsed_attach = parsed_attach[:-1]

        for player in game.players:
            self.api.response("", player.id, self.chat_id, parsed_attach, False)
            self.api.response(random_tag[0], player.id, self.chat_id, "", True)

    def start_game(self, player, args=[None]):
        args = args[0]
        if args is None and player.game is None:
            return self.show_games()

        if args is None and len(player.game.deck) == 0:
            self.api.response("Не задан набор для игры.\nПопробуйте: vk.com/album-213713475_284294786", player.id, self.chat_id, "")
            return None

        if args is None and player.game.correct_card is None:
            return self.show_cards(player.game)

        if player.game is not None:
            self.api.response("Вы уже в игре.", player.id, self.chat_id, "")
            return None

        if int(args) > len(self.games):
            game = Game(player)
            self.games.append(game)
            player.game = game
            self.api.response("Игра создана.", player.id, self.chat_id, "")
        else:
            self.notify_players(player, self.games[int(args) - 1])
            player.game = self.games[int(args) - 1]
            (self.games[int(args) - 1]).players.append(player)
            self.api.response("Вы присоединились к игре.", player.id, self.chat_id, "", False)

    def try_parse_album(self, player, link):
        try:
            parsed_link = (link.split("album")[1]).split("_")
            owner, album = parsed_link

            album = self.service_api.photos.get(
                owner_id=int(owner),
                album_id=int(album),
            )

            if player.game is None:
                self.api.response("Сначала создайте игру.", player.id, self.chat_id, "")
                return True

            player.game.set_album(album['items'])
            self.api.response("Набор задан.", player.id, self.chat_id, "")
            return True
        except:
            return False

    def check_correct(self, player, card):
        card = card[0]
        if player.game.correct_card is None:
            return "Сначала начните игру."

        if player.answer:
            self.api.response("Вы уже отвечали в этом раунде.", player.id, self.chat_id, "", False)
            return None

        player.answer = True
        if player.game.correct_card == card:
            player.player_score += 3
            self.api.response("Карта угадана!" + "\nВаш счёт: " + str(player.player_score), player.id, self.chat_id, "", False)
            if player.game.check_next_round():
                self.show_cards(player.game)
            return None

        self.api.response("Карта не угадана!" + "\nВаш счёт: " + str(player.player_score), player.id, self.chat_id, "", False)
        if player.game.check_next_round():
            self.show_cards(player.game)
        return None
