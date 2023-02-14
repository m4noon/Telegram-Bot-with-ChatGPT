import openai
import telebot
from decouple import config

openai.api_key = config("OPENAI.API_KEY")

bot_api = config("BOT_API")
bot = telebot.TeleBot(bot_api, parse_mode=None)

authorized_users = config("AUTHORIZED_USERS").split()
authorized_users = list(map(int, authorized_users))


def is_authorized(user_id):
    return user_id in authorized_users


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if is_authorized(message.from_user.id):
        bot.send_message(chat_id=message.from_user.id,
                         text=f'Вы имеете доступ {message.from_user.username}')
        bot.send_message(chat_id=message.from_user.id, text=f'Напиши что-нибудь')
        log = open(str(message.from_user.username), 'a+')
        log.close()
    else:
        print(f'New user? {message.from_user.username} and ID: {message.from_user.id}')
        bot.send_message(chat_id=message.from_user.id,
                         text=f'Вы не имеете доступа {message.from_user.username}')


@bot.message_handler(func=lambda _: True)
def chatgpt(message):
    if is_authorized(message.from_user.id):
        log = open(str(message.from_user.username), 'a+')
        print(f'Message from {message.from_user.username} and message:: {message.text}')
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=message.text,
            temperature=0.5,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0.5,
            presence_penalty=0.0,
        )
        chat = response['choices'][0]['text']
        log.write(f'Message = {message.text}\n'
                  f'And Response = {chat}\n')
        print(f'Response:: {chat}')
        bot.send_message(chat_id=message.from_user.id, text=response['choices'][0]['text'])
    else:
        bot.send_message(chat_id=message.from_user.id,
                         text=f'Вы не имеете доступа {message.from_user.username}')


bot.infinity_polling()
