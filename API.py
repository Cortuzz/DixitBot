import random
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from keyboards import start_keyboard, game_keyboard

class VkAPI:
    def __init__(self, group_id, token, debug_mode=False):
        self.id = group_id
        self.token = token
        self.debug_mode = debug_mode

        self.vk = vk_api.VkApi(token=self.token)
        self.long_poll = VkBotLongPoll(self.vk, self.id)
        self.vk_api = self.vk.get_api()

    def handle_request(self, request):
        if request.type == VkBotEventType.MESSAGE_NEW:
            return request.object.text

        raise ValueError()

    def get_user_id(self, request):
        return request.object.from_id

    def get_chat_id(self, request):
        return request.chat_id

    def get_handler(self):
        return self.long_poll.listen()

    def response(self, text, user_id, chat_id, attach, flag=None):
        payload = None
        if flag is None:
            payload = start_keyboard
        elif flag:
            payload = game_keyboard

        self.vk_api.messages.send(random_id=random.randint(-2000000, 2000000),
                                  user_id=user_id,
                                  message=text,
                                  attachment=attach,
                                  keyboard=payload)


class DebugAPI:
    def __init__(self, group_id, token, debug_mode=False):
        self.id = group_id
        self.token = token
        self.debug_mode = debug_mode

    def handle_request(self, request):
        return request

    def get_user_id(self, request):
        return 375795594

    def get_chat_id(self, request):
        return -1

    def handler(self):
        while True:
            yield input()

    def get_handler(self):
        return self.handler()

    def response(self, text, user_id, chat_id, attach):
        print(text, "\nAttach: ", attach)