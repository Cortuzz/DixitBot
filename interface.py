import locale
import random
import traceback

import vk_api

import API
from player import Player


class BotInterface:
    def __init__(self, api: API):
        locale.setlocale(locale.LC_ALL, '')
        self.commands = {'старт': self.get_cards}

        self.api = api
        self.admin_id = 375795594
        self.cards_bias = 457239017 - 1
        self.players = dict()
        self.chat_id = None

    def try_command(self, chat_id, command, player_id, *args):
        self.chat_id = chat_id

        if player_id not in self.players:
            self.add_player(player_id)

        player = self.get_player(player_id)
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
        player.parse_deck()
        self.players.update({player_id: player})

    def get_unique_tags(self, tags, names):
        map = dict()

        for card_tags_ind in range(len(tags)):
            card_tags = tags[card_tags_ind]
            for tag in card_tags:
                if tag not in map:
                    map.update({tag: [0, names[card_tags_ind]]})

                map[tag][0] += 1

        uniq_tags = []
        for tag in map:
            if map[tag][0] == 1:
                uniq_tags.append([tag, map[tag][1]])

        return uniq_tags

    def get_cards(self, player):
        cards = player.take_cards(5)

        cards_names = []
        cards_tags = []
        for card in cards:
            card_name, card_tag = card
            cards_names.append(int(card_name.split(".")[0]))
            card_tag = card_tag.split(" ")

            for i in range(len(card_tag)):
                card_tag[i] = card_tag[i].replace("\n", "")

            cards_tags.append(card_tag)

        random_tags = self.get_unique_tags(cards_tags, cards_names)
        random_tag = random.choice(random_tags)

        player.correct_card = random_tag[1]

        parsed_attach = ""
        for attach in cards_names:
            parsed_attach += "photo-" + str(self.api.id) + "_" + str(attach + self.cards_bias) + ","

        parsed_attach = parsed_attach[:-1]

        self.api.response("", player.id, self.chat_id, parsed_attach)
        return random_tag[0], ""

    def check_correct(self, player, card):
        card = card[0]
        if player.correct_card is None:
            return "Сначала вытяните карты."

        if player.correct_card == card:
            player.correct_card = None
            player.player_score += 3
            return "Карта угадана!" + "\nВаш счёт: " + str(player.player_score)

        player.correct_card = None
        return "Карта не угадана, попробуйте снова." + "\nВаш счёт: " + str(player.player_score)