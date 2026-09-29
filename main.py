import os
import random

import telebot

from json_core import read_json, write_json


TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Переменная окружения BOT_TOKEN не задана.")

bot = telebot.TeleBot(TOKEN)


def get_user_words(chat_id):
    data = read_json()
    return data.get(str(chat_id), {})


def save_user_word(chat_id, word, translation):
    data = read_json()
    user_words = data.setdefault(str(chat_id), {})
    user_words[word] = translation
    write_json(data)


def send_start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Я бот для изучения корейского языка.\n"
        "Добавляй слова в свой словарь и тренируй перевод."
    )


@bot.message_handler(commands=["start"])
def handle_start(message):
    send_start(message)


@bot.message_handler(commands=["help"])
def handle_help(message):
    bot.send_message(
        message.chat.id,
        "Доступные команды:\n"
        "/addword слово перевод — добавить слово в словарь\n"
        "/learn 5 — потренировать 5 слов\n"
        "/help — показать эту справку"
    )


@bot.message_handler(commands=["addword"])
def handle_addword(message):
    parts = message.text.split(maxsplit=2)

    if len(parts) != 3:
        bot.send_message(
            message.chat.id,
            "Формат команды: /addword 안녕하세요 здравствуйте"
        )
        return

    word, translation = parts[1].strip().lower(), parts[2].strip().lower()

    if not word or not translation:
        bot.send_message(message.chat.id, "Слово и перевод не должны быть пустыми.")
        return

    save_user_word(message.chat.id, word, translation)
    bot.send_message(message.chat.id, f"Слово «{word}» добавлено в словарь.")


@bot.message_handler(commands=["learn"])
def handle_learn(message):
    parts = message.text.split()

    if len(parts) != 2 or not parts[1].isdigit() or int(parts[1]) <= 0:
        bot.send_message(message.chat.id, "Используйте команду так: /learn 5")
        return

    words_number = int(parts[1])
    words = get_user_words(message.chat.id)

    if not words:
        bot.send_message(
            message.chat.id,
            "Твой словарь пока пуст. Добавь слова командой /addword."
        )
        return

    words_number = min(words_number, len(words))
    ask_translation(message.chat.id, words_number)


def ask_translation(chat_id, words_left):
    if words_left == 0:
        bot.send_message(chat_id, "Тренировка закончена!")
        return

    words = get_user_words(chat_id)
    word = random.choice(list(words))
    translation = words[word]

    bot.send_message(chat_id, f"Как переводится «{word}»?")
    bot.register_next_step_handler_by_chat_id(
        chat_id,
        check_translation,
        translation,
        words_left,
    )


def check_translation(message, expected_translation, words_left):
    user_translation = message.text.strip().lower()

    if user_translation == expected_translation.lower():
        bot.send_message(message.chat.id, "Правильно! 🎉")
    else:
        bot.send_message(
            message.chat.id,
            f"Пока не получилось. Правильный ответ: «{expected_translation}».",
        )

    ask_translation(message.chat.id, words_left - 1)


@bot.message_handler(func=lambda message: True)
def handle_unknown_message(message):
    bot.send_message(
        message.chat.id,
        "Я понимаю команды /addword, /learn и /help. Попробуй /help."
    )


if __name__ == "__main__":
    bot.infinity_polling()
