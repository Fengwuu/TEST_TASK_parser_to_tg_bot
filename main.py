import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import time
import schedule
import sqlite3
import os
from dotenv import load_dotenv, find_dotenv

'''
Some configuration stuff
YOU NEED TO HAVE THE DOTENV INSTALLED (pip install python-dotenv)
'''
load_dotenv(find_dotenv())


bot = telebot.TeleBot(os.environ.get("BOT_API"))
CHANNEL_NAME = os.environ.get("CHANNEL_NAME")
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
LOGIN_URL = 'https://www.tesmanian.com/account/login'
url = "https://www.tesmanian.com/"

'''
Here is the parsing function.
'''
def parse_function():
    session = requests.session()
    response = session.get(url)

    if response.status_code == 401:
        login_data = {'username': USERNAME, 'password': PASSWORD}
        session.post(LOGIN_URL, data=login_data)
        response = session.get(url)


    soup = BeautifulSoup(response.content, 'html.parser')
    articles= soup.find_all('blog-post-card')
    article_for_bot = {}


    for article in articles:
        title = article.find('p').text
        link = article.find('a')['href']
        link = 'https://www.tesmanian.com'+link
        article_for_bot[title] = link 

    return article_for_bot


'''
This function is used to avoid sending already sent news
YOU NEED TO HAVE SQLITE3 INSTALLED (pip install sqlite3)
'''
def get_sent_articles():
    conn = sqlite3.connect('DB.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS articles
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   link TEXT)''')

    cursor.execute('SELECT link FROM articles')
    sent_articles = [row[0] for row in cursor.fetchall()]
    conn.close()
    return sent_articles


'''
Here we save sent functions to the database to use get_sent_articles() function
YOU NEED TO HAVE SQLITE3 INSTALLED (pip install sqlite3)
'''
def add_sent_article(article_link):
    conn = sqlite3.connect('DB.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO articles (link) VALUES (?)', (article_link,))
    conn.commit()
    conn.close()


# Start message handler, need to start bot
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(CHANNEL_NAME, "Приветствую! Этот бот - тестовое задание. Мой телеграм - @feewai. Телеграм бота - @tesla_scanner_tz_bot, в нем описана информация о боте, обо мне и прочее. ")


'''
I decided to use 1 as a trigger to start the bot. Below is the message handler code
'''
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '1':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #ned buttons in chat 
        btn1 = types.KeyboardButton('Что делает этот бот?')
        btn2 = types.KeyboardButton('Мои контакты')
        markup.add(btn1, btn2)
        bot.send_message('@channel_test_task', 'Начинаю свою работу...',) #bot answer
        def send_articles():
            articles = parse_function()
            sent_articles = get_sent_articles()  # Check for new articles in chat
            for key, value in articles.items():
                if value not in sent_articles:
                    bot.send_message('@channel_test_task', f'{key}\n \n \nlink - {value}')
                    add_sent_article(value)
                    time.sleep(1.5)
        while True:
            send_articles()
            time.sleep(15) # parse the articles every 15 seconds

    elif message.text == 'Что делает этот бот?':
        bot.send_message(message.from_user.id, 'Данный бот создан для выполнения ТЗ. Меня зовут Филипп. Вот текст ТЗ:\n  Сайт: https://www.tesmanian.com/ Що треба реалізувати: \n1. Скрипт, який скрапить сайт 24/7 з інтервалом у 15 секунд.\n2. Логін має бути один раз (або коли отримуємо unauthirized error), щоб нас не запідозрили у спамі\n3. На виході мають бути тільки нові результати (у порівняня з попередньою перевіркою 15 сек тому) у телеграм канал. \nВідсилати потрібно title статті і посилання на неї.', parse_mode='Markdown')

    elif message.text == 'Мои контакты':
        bot.send_message(message.from_user.id, 'https://linktr.ee/fengwuu', parse_mode='Markdown')


bot.polling(none_stop=True, interval=0) 
# this string is required to run the bot