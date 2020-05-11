import telebot
#import config
import requests
from bs4 import BeautifulSoup
import pandas as pd
from telebot import types
import random
import os


TKNg=str(os.environ.get('TKN'))
bot = telebot.TeleBot(TKNg)

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
        lst=[url1+i.get('href') for i in soup.find_all('table', {'class':'menuanekdot'})[0].find_all('a', {'class':'menuanekdot'})]
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


@bot.message_handler(commands=['start'])
def hello(message):
    markup = types.ReplyKeyboardMarkup()
    markup.row('Расскажи анекдот')
    markup.row('Кто на свете всех милее, всех румяней и белее?')
    bot.send_message(message.chat.id, "Добрый день, я x-temp-bot2. \n"
                                      "База данных  по температуре в процессе наполнения и настройки. \n"
                                      "Чтобы занять время, пока хозяин допишет работу с базой и отрисовку графиков, \n"
                                      "Я могу поразвлекать вас анекдотами с anekdotov.net, \n"
                                      "Выберите вопрос", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text=='Кто на свете всех милее, всех румяней и белее?')
def Xen(message):
    bot.send_message(message.chat.id, f'На свете всех милее и румяней и белее - {str(message.from_user.first_name)}')


@bot.message_handler(func=lambda message: message.text=='Расскажи анекдот')
def getcats(message):
    markup1 = types.ReplyKeyboardMarkup()
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

print ('Bot has started')
if __name__ == '__main__':
    #bot.polling(none_stop=True)
    bot.infinity_polling()

print ('Done')