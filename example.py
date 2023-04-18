import logging
import os
import telebot
from telebot import types
import requests
import speech_recognition as sr
import subprocess
import settings
import random
import datetime
from utils import random_twister


logging.basicConfig(filename='example.log', level=logging.INFO)
# запись в реестр
logfile = str(datetime.date.today()) + '.log'
# формируем имя лог-файла
bot = telebot.TeleBot(settings.TOKEN_TELEGRAM_BOT)
twister = random_twister()
twister_lib = {
    "twister1": "на окошке крошку мошку ловко ловит лапой кошка",
    "twister2": "хорош у ежа пирожок внутри пирожка творожок",
    "twister3": "дельфин учил дельфинёнка свистеть тонко претонко",
    "twister4": "у ежа и ёлки иголки колки у ежа ежата у ужа ужата",
    "twister5": "пыхтит как пышка пухлый мишка",
    "twister6": "шесть шустрых мышат в камышах шуршат"
    }


def random_twister():

    twister = random.choice(list(twister_lib))
    return twister


@bot.message_handler(commands=["start"])  # декоратор обрабатывает старт
def greeting_user(message):
    markup = types.InlineKeyboardMarkup()  # создаем тип -  кнопка
    button_1 = types.InlineKeyboardButton(
        "Новая скороговорка", callback_data="new"
        )
    # добавляем кнопку c названием
    markup.row(button_1)  # порядок кнопок 1 ряд
    button_2 = types.InlineKeyboardButton(
        "Рейтинг", callback_data="rating"
        )
    # добавляем кнопку c названием
    markup.row(button_2)  # порядок кнопок 2 ряд
    button_3 = types.InlineKeyboardButton(
        "Написать тренеру", url="https://t.me/natalia_latfullina"
        )
    markup.row(button_3)
    bot.send_message(message.from_user.id, "Привет я бот <b>SpikerClub</b>\n"
                     "помогаю тренировать речь с помощью скороговорок,\n"
                     "что бы начать нажмите <b>Новая скороговорка</b>",
                     parse_mode="html",
                     reply_markup=markup)
# форматирование текста в формате html parse_mode = "html"


@bot.callback_query_handler(func=lambda callback: True)
# анонимная лямда функция, если будет пустойто возвращаем True
def send_twister(callback):
    if callback.data == "new":
        file = open("images/" + twister + ".jpg", "rb")
        # обращаемся к текущей папке к файлу 1.jpg, rb - открываем для чтения
        bot.send_photo(callback.message.chat.id, file)


# def rating():
#   pass


@bot.message_handler(content_types=['voice'])
def get_audio_messages(message):
    # принимает аудиосообщение
    try:
        print("Started recognition...")
        file_info = bot.get_file(message.voice.file_id)
        path = file_info.file_path  # путь до файла
        fname = os.path.basename(path)  # Преобразуем путь в имя файла
        doc = requests.get(
            'https://api.telegram.org/file/bot{0}/{1}'.format(settings.TOKEN_TELEGRAM_BOT, file_info.file_path))
        # Получаем аудиосообщение
        with open(fname+'.oga', 'wb') as f:
            f.write(doc.content)
            # Сохраняем аудиосообщение
        process = subprocess.run(['ffmpeg', '-i', fname+'.oga', fname+'.wav'])
        # ffmpeg, для конвертации .oga в .vaw
        result = audio_to_text(fname+'.wav')
        # Вызов функции для перевода аудио в текст
        bot.send_message(message.from_user.id, format(result))
        # Отправляем пользователю, приславшему файл, его текст
    except sr.UnknownValueError as e:
        # Ошибка возникает, если сообщение не удалось разобрать.
        # В таком случае отсылается ответ пользователю и заносим запись в лог
        bot.send_message(message.from_user.id,
                         "Извините, я не разобрал сообщение или оно поустое")
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':'
                    + str(message.from_user.id) + ':'
                    + str(message.from_user.first_name) + '_'
                    + str(message.from_user.last_name) + ':'
                    + str(message.from_user.username) + ':'
                    + str(message.from_user.language_code)
                    + ':Message is empty.\n')
    except Exception as e:
        # В случае возникновения любой другой ошибки,
        # отправляется  сообщение пользователю и заносится запись в лог
        bot.send_message(message.from_user.id,  "Что-то пошло не так")
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':'
                    + str(message.from_user.id) + ':'
                    + str(message.from_user.first_name) + '_'
                    + str(message.from_user.last_name) + ':'
                    + str(message.from_user.username) + ':'
                    + str(message.from_user.language_code) + ':'
                    + str(e) + '\n')
    finally:
        # В любом случае удаляем временные файлы с аудио сообщением
        os.remove(fname+'.wav')
        os.remove(fname+'.oga')





def audio_to_text(dest_name: str):
    # Функция для перевода аудио, в формате ".vaw" в текст
    rating = 0
    r = sr.Recognizer()
    # читаем наш .vaw файл
    message = sr.AudioFile(dest_name)
    with message as source:
        audio = r.record(source)
    result = r.recognize_google(audio, language="ru_RU").lower()
    return difference_three(result.strip(), twister_lib[twister].strip())

    # используя возможности библиотеки распознаем текст,
    # можно изменять язык распознавания
"""if result.strip() == twister_lib[twister].strip():
        rating = + 1
        return f"Вы произнесли '{result}' все верно\nВаш рейтинг {rating}"
    elif result.strip() != twister_lib[twister].strip():
        return f"Вы произнесли '{result}' не верно, а должно быть'{twister_lib[twister]}'"
"""


def difference_three(txt1, txt2):
 # разрешает сделать 2 ошибки
 # сравнивает посимвольно строку и если
    count = 0
    if len(txt1) == len(txt2):
        for i in range(0, len(txt1)):
            if txt1[i] == txt2[i]:
                count = count + 1
    if count+2 >= len(txt1):
        return "все верно\nВаш рейтинг"
    else:
        return "Не верно!"


bot.polling(none_stop=True, interval=0)
# повторяем обращение к telegram
