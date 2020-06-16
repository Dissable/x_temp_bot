import telebot
from telebot import types
#import config
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import random
import os
import psycopg2
from contextlib import closing
from telebot import apihelper


try:
    with open('E:\\Agnbad\\Sunny\\Pyton\\HSE\\Homework\\x-temp-bot2\\token.txt') as f:
        TKNg=f.read()
except:
    TKNg=str(os.environ.get('TKN'))
bot = telebot.TeleBot(TKNg)

# if local_start:
if False:
    ip = '195.201.137.246'
    ip='1.70.64.230'
    ip='212.170.18.65'
    port = '1080'
    port='28643'
    port='4145'
    apihelper.proxy = {'https': 'socks5://{}:{}'.format(ip, port)}
    # apihelper.proxy = {'https': 'socks5://138.36.21.75:9913'}


global catdict
catdict={}
def get_catdict():
    page = random.randrange(1, 500, 1)
    url1 = f'http://anekdotov.net'
    website = requests.get(url1)
    website.encoding = 'cp1251'
    website_url = website.text
    if len(str(website.text))>100:
        soup = BeautifulSoup(website_url, 'lxml')
        lst=[url1+i.attrs['href'] for i in soup.find_all('table', {'class':'menuanekdot'})[0].find_all('a', {'class':'menuanekdot'})]
        lstnames=[i.text for i in soup.find_all('table', {'class':'menuanekdot'})[0].find_all('a', {'class':'menuanekdot'})]
        catdict=dict(zip(lstnames, lst))
        return(catdict)
    else:
        return('Ошибка получения категорий')


def get_anek(url1):
    website = requests.get(url1)
    website.encoding = 'cp1251'
    website_url = website.text
    if len(str(website.text))>100:
        soup = BeautifulSoup(website_url, 'lxml')
        lst=[i.text for i in soup.find_all('table', {'class':'maintbl'})[0].find_all('div', {'class':'anekdot'})]
        if len(lst) > 0:
            anekn=random.randrange(0,len(lst),1)
            return(lst[anekn])
        else:
            return('Парсер не смог найти анекдот')
    else:
        return('Сайт не ответил')


def db_insert_temp(TEMP, MUSER_ID: int, DATA=datetime.datetime.today().strftime('%Y-%m-%d')):
    with closing(get_connec()) as conn:
        with conn.cursor() as cursor:
            sql=f'''INSERT INTO "TBTEMPERATURE" ("DATA", "MUSER_ID", "TEMP") VALUEs ('{DATA}', {MUSER_ID}, {TEMP}) ON CONFLICT ("DATA", "MUSER_ID") DO UPDATE SET "TEMP"={TEMP} '''
            print(sql)
            cursor.execute(sql)
        conn.commit()
        print(f'temp {TEMP} inserted into {DATA}')


@bot.message_handler(commands=['start'])
def hello(message):
    inline_kb1 = types.InlineKeyboardMarkup()
    inline_btn_1 = types.InlineKeyboardButton('Кто на свете всех милее, всех румяней и белее?', callback_data='button1')
    inline_btn_2 = types.InlineKeyboardButton('Расскажи анекдот', callback_data='button2')
    inline_btn_temp = types.InlineKeyboardButton('Внести температуру', callback_data='btn_temp')
    inline_kb1.add(inline_btn_1)
    inline_kb1.add(inline_btn_2)
    inline_kb1.add(inline_btn_temp)

    bot.send_message(message.chat.id, "Добрый день, я x-temp-bot2. \n"
                                       "Мой код доступен на https://github.com/Dissable/x_temp_bot, \n"
                                       "База данных  по температуре в процессе наполнения и настройки. \n"
                                       "Чтобы занять время, пока хозяин допишет работу с базой и отрисовку графиков, \n"
                                       "Я могу поразвлекать вас анекдотами с anekdotov.net, \n"
                                       "Выберите вопрос", reply_markup=inline_kb1)


@bot.callback_query_handler(func=lambda c: c.data == 'button1')
def process_callback_button1(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    bot.send_message(callback_query.from_user.id, f'На свете всех милее и румяней и белее - {str(callback_query.from_user.first_name)}')


@bot.callback_query_handler(func=lambda c: c.data == 'button2')
def process_callback_button2(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    inline_kb_anek = types.InlineKeyboardMarkup()
    global catdict
    catdict = get_catdict()
    if type(catdict)==dict:
        for i in list(get_catdict())[:-2]:
            inline_kb_anek.add(types.InlineKeyboardButton(i, callback_data=i))
        bot.send_message(callback_query.from_user.id, "Выберите категорию, или можно вернуться в начало "+'/start', reply_markup=inline_kb_anek)
    else:
        bot.send_message(callback_query.from_user.id, 'Ошибка'+str(catdict))
    # bot.send_message(callback_query.from_user.id, 'Нажата вторая кнопка!')


@bot.callback_query_handler(func=lambda c: c.data in [i for i in catdict])
# def anek(message):
def process_callback_button3(callback_query: types.CallbackQuery):
    print(catdict)
    bot.send_message(callback_query.from_user.id, get_anek(catdict[callback_query.data]) +     #message.text[1:]
                                        '\n-------------------------------------------------'+
                                        '\n еще один, или вернуться в начало /start')


inline_temp1 = types.InlineKeyboardMarkup()
inline_temp_today = types.InlineKeyboardButton('Записать на сегодня', callback_data='btn_temp_today')
inline_temp_select_day = types.InlineKeyboardButton('Выбрать другой день', callback_data='btn_temp_select_day')
inline_temp1.add(inline_temp_today)
inline_temp1.add(inline_temp_select_day)


#нажали первую нопку ввода температуры
@bot.callback_query_handler(func=lambda c: c.data == 'btn_temp')
def process_callback_btn_temp(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    bot.send_message(callback_query.from_user.id, 'Введите температуру...', reply_markup=inline_temp1)


@bot.callback_query_handler(func=lambda c: c.data == 'btn_temp')
def process_callback_button2(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query, callback_query.from_user.id)
    bot.send_message(callback_query.from_user.id, f'{muser_temp[callback_query.from_user.id]} записана на сегодня для пользователя {callback_query.from_user.id}')




###############      ниже оставили кусочек старого кода, оттуда копируем то, что нам надо      ##############
@bot.message_handler(func=lambda message: message.text=='Кто на свете всех милее, всех румяней и белее?')
def Xen(message):
    bot.send_message(message.chat.id, f'На свете всех милее и румяней и белее - {str(message.from_user.first_name)}')


@bot.message_handler(func=lambda message: message.text=='Расскажи анекдот')
def getcats(message):
    markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    global catdict
    catdict = get_catdict()
    if type(catdict)==dict:
        for i in list(get_catdict())[:-2]:
            markup1.row('/'+i)
        bot.send_message(message.chat.id, "Выберите категорию, или можно вернуться в начало "+'/start', reply_markup=markup1)
    else:
        bot.send_message(message.chat.id, 'Ошибка'+str(catdict))


@bot.message_handler(func=lambda message: message.text in ['/'+i for i in catdict])
def anek(message):
    bot.send_message(message.chat.id, get_anek(catdict[message.text[1:]]) +
                                        '\n-------------------------------------------------'+
                                        '\n еще один, или вернуться в начало /start')


@bot.message_handler(func=lambda message: message.text.lower().strip()!='start')
def echo(message):
    bot.send_message(message.chat.id, message.text)
##################         код выше будет заменен        #####################


print ('Bot has started')
if __name__ == '__main__':
    #bot.polling(none_stop=True)
    bot.infinity_polling()

print ('Done')