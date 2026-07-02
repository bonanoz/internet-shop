import os
import re

import telebot
from django.utils.text import slugify

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
CHAT_ID = os.environ.get('CHAT_ID')

PHONE_RE = re.compile(r'^\+?[78][\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$')

# Транслитерация кириллицы в латиницу для человекочитаемых ASCII-slug
# (URL вида /product/kreslo-kokon/, как на estivo63.ru — /kreslo, /divan).
_TRANSLIT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}


def ru_slugify(value):
    """Транслитерирует кириллицу и возвращает ASCII-slug."""
    value = (value or '').lower()
    transliterated = ''.join(_TRANSLIT.get(ch, ch) for ch in value)
    return slugify(transliterated)


def notify_telegram(text):
    """Отправляет сообщение в Telegram-чат менеджера. Не бросает исключений —
    заявка должна сохраняться в БД независимо от доступности Telegram API.
    """
    try:
        bot.send_message(CHAT_ID, text)
        return True
    except Exception:
        return False


def clean_phone_number(value):
    """Простая проверка на российский номер телефона. Возвращает исходную
    строку без изменений (валидация, не нормализация форматов ввода).
    """
    value = (value or '').strip()
    if not PHONE_RE.match(value):
        raise ValueError('Введите номер телефона в формате +7 XXX XXX-XX-XX')
    return value
