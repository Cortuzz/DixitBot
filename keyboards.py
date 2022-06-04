import json

start_keyboard = {
    "inline": True,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "payload": "{\"button\": \"1\"}",
                "label": "старт"
            },
            "color": "positive"
        },
        ]
    ]
}

start_keyboard = json.dumps(start_keyboard, ensure_ascii=False).encode('utf-8')
start_keyboard = str(start_keyboard.decode('utf-8'))

game_keyboard = {
    "inline": True,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "payload": "{\"button\": \"1\"}",
                "label": "1"
            },
            "color": "positive"
        },
{
            "action": {
                "type": "text",
                "payload": "{\"button\": \"1\"}",
                "label": "2"
            },
            "color": "negative"
        },
{
            "action": {
                "type": "text",
                "payload": "{\"button\": \"1\"}",
                "label": "3"
            },
            "color": "primary"
        },
{
            "action": {
                "type": "text",
                "payload": "{\"button\": \"1\"}",
                "label": "4"
            },
            "color": "positive"
        },
{
            "action": {
                "type": "text",
                "payload": "{\"button\": \"1\"}",
                "label": "5"
            },
            "color": "negative"
        },
        ]
    ]
}

game_keyboard = json.dumps(game_keyboard, ensure_ascii=False).encode('utf-8')
game_keyboard = str(game_keyboard.decode('utf-8'))
