import telebot
from telebot import types

TOKEN = "6099746979:AAHiP1RU2bryVFDIWJnAwaXuz1_4jkCMIFk"
bot = telebot.TeleBot(TOKEN)


def main_keyboard(message):
    markup = types.ReplyKeyboardMarkup()  # создаем тип -  кнопка
    button_1 = types.KeyboardButton("Новая скороговорка")
    # добавляем кнопку c названием
    markup.row(button_1)  # порядок кнопок 1 ряд
    button_2 = types.KeyboardButton("Рейтинг")
    # добавляем кнопку c названием
    button_3 = types.KeyboardButton("Написать тренеру")
    markup.row(button_2, button_3)  # порядок кнопок 2 ряд
    bot.send_message(message.chat.id, 'Давайте заниматься',
                     reply_markup=markup)
    bot.register_next_step_handler(message, on_click)
    # return types.ReplyKeyboardMarkup()


def on_click(message):
    if message.text == "Новая скороговорка":
        bot.send_message(message.chat.id,
                         'На дворе трава на траве дрова не руби дрова на траве двора')
    elif message.text == "Рейтинг":
        bot.send_message(message.chat.id, 'Вы на первом месте',
                         reply_markup=main_keyboard(message))


@bot.message_handler(commands=["start"])
def greeting_user(message):
    bot.send_message(message.chat.id, 'Добрый день! Вы попали в мой бот',
                     reply_markup=main_keyboard(message))


bot.polling(none_stop=True, interval=0)
