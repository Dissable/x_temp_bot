import telebot
import config
import requests
from bs4 import BeautifulSoup
import pandas as pd
from telebot import types
import random


def get_anek():
    page = random.randrange(1, 500, 1)
    url1 = f'http://anekdotov.net/anekdot/family/index-page-{page}.html'
    website = requests.get(url1)
    website.encoding = 'cp1251'
    website_url = website.text
    if str(website)=='<Response [200]>':
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(website_url, 'lxml')
        lst=[i.text for i in soup.find_all('table', {'class':'maintbl'})[0].find_all('form', {'method':'post'})[0].find_all('p') if (len(i.text) > 10 and 'Ч И Т А Т Ь' not in i.text)]
        if len(lst) > 0:
            anekn=random.randrange(0,len(lst),1)
            return(lst[anekn])
        else:
            return('— Ты где был? — С собакой гулял. — У нас же нет собаки. — А мы с ней на улице познакомились.')
    else:
        return('anekdotov.net спалил парсер')


bot = telebot.TeleBot(config.token)
@bot.message_handler(commands=['start'])
def hello(message):
    markup = types.ReplyKeyboardMarkup()
    markup.row('Расскажи анекдот')
    markup.row('Кто на свете всех милее, всех румяней и белее?')
    bot.send_message(message.chat.id, "Выберите вопрос", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text=='Кто на свете всех милее, всех румяней и белее?')
def Xen(message):
    bot.send_message(message.chat.id, 'На свете всех милее и румяней и белее - Ксенюшка!!!')

@bot.message_handler(func=lambda message: message.text=='Расскажи анекдот')
def anek(message):
    bot.send_message(message.chat.id, get_anek())

@bot.message_handler(func=lambda message: message.text.lower().strip()!='start')
def echo(message):
    bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
    #bot.polling(none_stop=True)
    bot.infinity_polling()

def stat(tag=0):
    '''
    Достали статистику по короновирусу в pd.DataFrame
    :param tag:
    :return:
    '''
    url = 'https://www.worldometers.info/coronavirus/'
    website_url = requests.get(url).text
    soup = BeautifulSoup(website_url, 'lxml')
    table = soup.find_all('table')[tag]
    rows = table.find_all('tr')
    field_list = []
    for i in range(12):
        col = []
        col.append(rows[0].find_all('th')[i].get_text().strip())  # отдельно добавляем заголовок
        for row in rows[1:]:  # начинаем со второго ряда таблицы, потому что 0 уже обработали выше
            r = row.find_all('td')  # находим все теги td для строки таблицы
            col.append(r[i].get_text().strip())  # сохраняем данные в наш список
        field_list.append(col)
    d = dict()
    for i in range(12):
        d[field_list[i][0]] = field_list[i][1:]

    df = pd.DataFrame(d)
    df = df.rename(columns={'Country,Other': 'Country', 'Serious,Critical': 'SeriousCritical'})
    return df



print ('Done')