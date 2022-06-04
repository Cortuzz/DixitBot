from vk_api import vk_api

from bot import Bot

api_data = open("api_data.txt")

group_id = int(api_data.readline())
token = api_data.readline().replace("\n", "")
service_token = api_data.readline()
debug_mode = False

bot = Bot(group_id, token, service_token, debug_mode)

if __name__ == "__main__":
    bot.run()