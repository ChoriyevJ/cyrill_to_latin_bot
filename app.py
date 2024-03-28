import time

from telebot import TeleBot, types
from dotenv import load_dotenv
from translate import to_cyrillic, to_latin
from database import db, cursor
from utils import create_json_file
import os

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def command_start(message: types.Message):

    chat_id = message.chat.id
    first_name = message.from_user.first_name
    username = message.from_user.username
    text = f"Assalomu alaykum, {first_name}"
    bot.send_message(
        chat_id=chat_id,
        text=text
    )
    user_id = cursor.execute("select id from user where user_id = ?", (chat_id,)).fetchone()

    if not user_id:
        cursor.execute("""
            INSERT INTO user (user_id, first_name, username) VALUES (?, ?, ?);
        """, (chat_id, first_name, username))
        db.commit()


@bot.message_handler(commands=['admin'])
def command_admin(message: types.Message):
    chat_id = message.chat.id

    if int(chat_id) != int(os.getenv('ADMIN_ID')):
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        bot.send_message(chat_id=chat_id, text="Ukam sen admin emassan!")
        return

    user_messages_dict = dict()

    users = cursor.execute("""
    select id, first_name from user;
    """).fetchall()

    messages = cursor.execute(
        """
        select content, translated_content, user_id from message;
        """
    ).fetchall()

    for user_id, first_name in users:
        u_m = list()
        for message in messages:
            if int(message[2]) == int(user_id):
                u_m.append({message[0]: message[1]})
        user_messages_dict[first_name] = u_m

    text = ""
    for user, messages in user_messages_dict.items():
        text += f"{user}"
        for message in messages:
            text += f"\n{message}"
        text += "\n============================\n"

    create_json_file(f'statistics', user_messages_dict)
    with open('messages/statistics.json', mode='rb') as json_file:
        content = json_file.read()

    bot.send_message(chat_id=chat_id, text=text)
    bot.send_document(chat_id, content, visible_file_name="statistics")


@bot.message_handler()
def translate_text(message: types.Message):
    chat_id = message.chat.id
    user_id = int(cursor.execute("select id from user where user_id = ?", (chat_id,)).fetchone()[0])
    # video = open('C:/Users/user/Videos/for.mp4', mode='rb')
    #
    # bot.reply_to(message,  message.text)
    # bot.send_video(message.chat.id,
    #                video=video)
    # video.close()

    text = message.text
    message_id = message.message_id
    translated_text = to_latin(text)
    if text.isascii():
        translated_text = to_cyrillic(text)
    bot.reply_to(message, translated_text)

    cursor.execute(
        """
        insert into message (message_id, content, translated_content, user_id) values (?, ?, ?, ?)
        """, (message_id, text, translated_text, user_id)
    )
    db.commit()


while True:
    try:
        print('Bot start...')
        bot.polling(none_stop=True, skip_pending=True)
    except Exception as e:
        print(e)
        time.sleep(5)
        print('Bot is works...')

