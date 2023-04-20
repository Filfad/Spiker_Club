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
import json

logging.basicConfig(filename='example.log', level=logging.INFO)
# запись в реестр
logfile = str(datetime.date.today()) + '.log'
# формируем имя лог-файла
bot = telebot.TeleBot(settings.TOKEN_TELEGRAM_BOT)
global twister
twister = random_twister()
twister_lib = {
    "twister1": "на дворе трава на траве дрова не руби дрова на траве двора",
    "twister2": "карл у клары украл кораллы клара у карла украла кларнет",
    "twister3": "корабли лавировали лавировали да не вылавировали",
    "twister4": "в недрах тундры выдры в гетрах тырят в вёдра ядра кедров",
    "twister5": "у четырех черепашек четыре черепашонка",
    "twister6": "шла саша по шоссе и сосала сушку"
    }


def random_twister():
    twister = random.choice(list(twister_lib))
    return twister


def photo(message):
    global twister
    twister = random_twister()
    file = open("images/" + twister + ".jpg", "rb")
    # обращаемся к текущей папке к файлу 1.jpg, rb - открываем для чтения
    bot.send_photo(message.from_user.id, file)
    return message


def main_keyboard(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = types.KeyboardButton("Новая скороговорка")
    markup.row(button_1)
    button_2 = types.KeyboardButton("Рейтинг")
    button_3 = types.KeyboardButton("Написать тренеру")
    markup.row(button_2, button_3)
    msg = bot.send_message(message.from_user.id, 'Давайте заниматься',
                           reply_markup=markup)
    """Хочу убрать текст Давайте заниматься """
#bot.register_next_step_handler(msg, on_click)


@bot.message_handler(content_types=["text"])
def on_click(message):
    if message.text == "Новая скороговорка":
        photo(message)
    if message.text == "Рейтинг":
        rating_list()


def rating_list(message):
    bot.send_message(message.from_user.id, "ты первый")


@bot.message_handler(commands=["start"])  # декоратор обрабатывает старт
def greeting_user(message):
    bot.send_message(message.from_user.id, "Привет я бот <b>SpikerClub</b>\n"
                     "помогаю тренировать речь с помощью скороговорок,\n"
                     "что бы начать нажмите\n <b>Новая скороговорка</b>",
                     parse_mode="html",
                     reply_markup=main_keyboard(message))


@bot.message_handler(content_types=['voice'])
def get_audio_messages(message):
    # принимает аудиосообщение
    try:
        print("Started recognition...")
        file_info = bot.get_file(message.voice.file_id)
        path = file_info.file_path  # путь до файла
        fname = os.path.basename(path)  # Преобразуем путь в имя файла
        doc = requests.get(
            'https://api.telegram.org/file/bot{0}/{1}'
            .format(settings.TOKEN_TELEGRAM_BOT, file_info.file_path))
        # Получаем аудиосообщение
        with open(fname+'.oga', 'wb') as f:
            f.write(doc.content)
            # Сохраняем аудиосообщение
        process = subprocess.run(['ffmpeg', '-i', fname+'.oga', fname+'.wav'])
        # ffmpeg, для конвертации .oga в .vaw
        result = audio_to_text(fname+'.wav')
        # Вызов функции для перевода аудио в текст
        bot.send_message(
            message.from_user.id,
            f"{difference_three(result.strip(),twister_lib[twister].strip())}"
            f"Вы произнесли:\n<b>{result.capitalize()}</b>\nДолжно быть:\n"
            f"<b>{twister_lib[twister].capitalize()}</b>\n"
            f"{user}",
            parse_mode="html",
            reply_markup=main_keyboard(message))
        # Отправляем пользователю, сравнениее аудио и скороговорки
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
    r = sr.Recognizer()
    # читаем наш .vaw файл
    message = sr.AudioFile(dest_name)
    with message as source:
        audio = r.record(source)
    result = r.recognize_google(audio, language="ru_RU").lower()
    return result
    # используя возможности библиотеки распознаем текст,
    # можно изменять язык распознавания


def difference_three(txt1, txt2):
    # разрешает сделать 2 ошибки
    # сравнивает посимвольно строку и если
    count = 0
    rating = 0
    if len(txt1)+3 >= len(txt2):
        for i in range(0, len(txt1)):
            if txt1[i] == txt2[i]:
                count = count + 1
    if count+3 >= len(txt1):
        rating += 1
        return f"все верно!\nваш рейтинг {rating} "

    else:
        return "Не верно, попробуйте еще раз\n"


def add_rating():
    rating = 0
    rating = rating + 1
    return rating


def save_rating(data, rating_file):
    data = json.dumps(data)
    data = json.loads(str(data))

    with open(rating_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


data = {
    "users": []
}

data["users"].append({
    "name": "message.from_user.first_name",
    "chat_id": "message.from_user.id",
    "rating": add_rating()
})

save_rating(data, "rating_file.json")


def read_rating(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        return json.load(file)


users = read_rating("rating_file.json")
for user in users["users"]:
    print(user)


bot.polling(none_stop=True, interval=0)
# повторяем обращение к telegram
