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
        self.global_board = []

        self.one_true = False
        self.all_true = True

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

        if self.define_key_word(player, command, args):
            return

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

    def get_results(self, game):
        t = "Результаты:\n"
        for pl in game.players:
            t += self.get_name(pl) + ": " + str(pl.player_score) + "\n"
        return t

    def results(self, player):
        if player.game is None:
            return "Вы не находитесь в игре."
        t = self.get_results(player.game)
        self.api.response(t, player.id, self.chat_id, "", False)

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

    def show_board_cards(self, game):
        parsed_attach = []

        for player in game.players:
            parsed_attach.append(player.picked_own_card)

        random.shuffle(parsed_attach)
        self.global_board = parsed_attach.copy()
        parsed_attach = ','.join(parsed_attach)

        for player in game.players:
            if player == game.players[game.lead]:
                continue

            self.api.response("", player.id, self.chat_id, parsed_attach, False)
            self.api.response("Какая из картинок - ведущего?\nКлючевая фраза: " +
                              game.lead_phrase, player.id, self.chat_id, "", False)

    def show_cards(self, game):
        for player in game.players:
            if player == game.players[game.lead]:
                continue

            parsed_attach = ""

            for attach in player.cards:
                parsed_attach += attach + ","

            parsed_attach = parsed_attach[:-1]
            self.api.response("", player.id, self.chat_id, parsed_attach, False)
            self.api.response("Выберите наиболее подходящую картинку под фразу: \n" +
                              game.lead_phrase, player.id, self.chat_id, "", True)

    def define_key_word(self, player, number, word):
        try:
            game = player.game
            if not game or game.players[game.lead] != player or not game.waiting_for_lead:
                return False
            pass
            game.lead_phrase = ' '.join(word)
            game.correct_card = player.cards[int(number) - 1]
            player.picked_own_card = game.correct_card
            player.cards.remove(player.cards[int(number) - 1])
            game.waiting_for_lead = False
            game.waiting_for_pixs = True

            self.show_cards(game)
            return True
        except:
            return False

    def ask_for_word(self, game):
        lead = game.players[game.lead]
        game.waiting_for_lead = True

        self.api.response("", lead.id, self.chat_id, game.players[game.lead].cards, False)
        self.api.response("Вы - ведущий.\nВыберите номер картинки и фразу([номер] [фраза]).", lead.id, self.chat_id, "",
                          False)

    def start_game(self, player, args=[None]):
        args = args[0]
        if args is None and player.game is None:
            return self.show_games()

        if args is None and len(player.game.deck) == 0:
            self.api.response("Не задан набор для игры.\nПопробуйте: vk.com/album-213713475_284294786", player.id,
                              self.chat_id, "")
            return None

        if player.game is not None and player.game.game_started:
            self.api.response("Вы уже в игре.", player.id, self.chat_id, "")
            return None

        if args is None and player.game.correct_card is None:
            for pl in player.game.players:
                pl.cards = player.game.take_cards(5)
                self.api.response("Игра началась!", pl.id, self.chat_id, "")

            player.game.game_started = True
            self.ask_for_word(player.game)
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
            self.api.response("Вы присоединились к игре.", player.id, self.chat_id, "")

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

    def find_player_by_card(self, card, game):
        for player in game.players:
            if player.picked_own_card == card:
                return player

    def calculate_points(self, game):
        if not self.one_true or self.all_true:
            for player in game.players:
                if player == game.players[game.lead]:
                    continue
                player.player_score += 2
            return

        game.players[game.lead].player_score += 2
        for player in game.players:
            if player.is_right:
                player.player_score += 3
                continue
            pl = self.find_player_by_card(player.picked_card, game)
            if pl is not None:
                pl.player_score += 1

        self.check_end(game)

    def finish_game(self, game):
        self.one_true = False
        self.all_true = True
        text = "Игра закончена.\nТаблица рейтинга:\n" + self.get_results(game)

        for player in game.players:
            self.players.pop(player.id)
            self.api.response(text, player.id, self.chat_id, "", None)
        self.games.remove(game)

    def check_end(self, game):
        for player in game.players:
            if player.player_score >= 40:
                self.finish_game(game)
                return

    def check_correct(self, player, card):
        card = card[0]
        if player.game.correct_card is None:
            return "Сначала начните игру."

        if player.answer:
            self.api.response("Вы уже отвечали в этом раунде.", player.id, self.chat_id, "", False)
            return None

        player.answer = True
        if player.game.waiting_for_pixs:
            player.picked_own_card = player.cards[card - 1]
            player.cards.pop(card - 1)
            self.api.response("Карта загадана.", player.id, self.chat_id, "", False)
            if player.game.check_next_round():
                player.game.waiting_for_pixs = False
                self.show_board_cards(player.game)
            return None

        ########################################################
        if self.global_board[card - 1] == player.picked_own_card:
            player.answer = False
            self.api.response("Нельзя выбрать свою карту.", player.id, self.chat_id, "", False)
            return None

        if player.game.correct_card == self.global_board[card - 1]:
            player.is_right = True
            self.one_true = True
            self.api.response("Карта угадана!", player.id, self.chat_id, "", False)
            if player.game.check_next_round():
                self.calculate_points(player.game)
                self.one_true = False
                player.game.waiting_for_lead = True
                player.game.change_lead()
                self.ask_for_word(player.game)
            return None

        self.all_true = False
        player.is_right = False
        player.picked_card = self.global_board[card - 1]
        self.api.response("Карта не угадана.", player.id, self.chat_id, "", False)
        if player.game.check_next_round():
            self.calculate_points(player.game)
            self.all_true = True
            player.game.waiting_for_lead = True
            player.game.change_lead()
            self.ask_for_word(player.game)
        return None
