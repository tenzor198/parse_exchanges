import telebot
from telebot import types
import regex
import json
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
bot = telebot.TeleBot('5486292384:AAGVB3T_uvfF75KcrMJ2k-Yww4Pr2GW_XCA')


def corona_curs():

    params = {
        'sendingCountryId': 'RUS',
        'sendingCurrencyId': '810',
        'receivingCountryId': 'KAZ',
        'receivingCurrencyId': '398',
        'paymentMethod': 'debitCard',
        'receivingAmount': '100000',
        'receivingMethod': 'cash',
        'paidNotificationEnabled': 'true',
    }
    headers = {
        'User-Agent': UserAgent().random,
        'Accept': 'application/vnd.cft-data.v2.86+json',
        'Accept-Language': 'en',
        'x-application': 'Qpay-Web/3.0',
        'x-csrf-token': '1fa0cd2ff26e77b9046d17f979af5655',
        'Connection': 'keep-alive',
        'Referer': 'https://koronapay.com/transfers/online/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }
    response = requests.get('https://koronapay.com/transfers/online/api/transfers/tariffs',
                            params=params,
                            headers=headers)
    response.json()
    return round(1 / response.json()[0]['exchangeRate'], 3)


def kurs_kz():

    headers = {
        'User-Agent': UserAgent().random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://kurs.kz/',
        'Connection': 'keep-alive',
        # Requests sorts cookies= alphabetically
        # 'Cookie': 'PHPSESSID=lm0occj10cm1l5nbn54mh6g2ma; __utma=155015202.585920995.1664831714.1664831714.1664831714.1; __utmb=155015202.2.10.1664831714; __utmc=155015202; __utmz=155015202.1664831714.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmt=1; _ym_uid=1664831714707133073; _ym_d=1664831714; _ym_isad=1; _zero_cc=f8996bd75cbf24; _zero_ss=633b50e2d5cb7.1664831715.1664832096.2; _ym_visorc=w',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        # Requests doesn't support trailers
        # 'TE': 'trailers',
    }

    response_kurs = requests.get('https://kurs.kz/', headers=headers)

    soup = BeautifulSoup(response_kurs.text, 'html.parser')
    scripts = soup.select('script')
    pattern = regex.compile(r'\{(?:[^{}]|(?R))*\}')
    result = []
    rub_currency = []
    for script in scripts:
        jsons_soup = pattern.findall(str(script))
        for exchanges in jsons_soup:
            try:
                json_cat = json.loads(exchanges)
                result.append([json_cat['name'], json_cat['address'], json_cat['data']['RUB'][0]])
                rub_currency.append(json_cat['data']['RUB'][0])
            except:
                pass
    rub_currency_max = max(rub_currency)
    exchanges = list(filter(lambda x: x[2] == rub_currency_max, result))
    output = []
    for exchange in exchanges:
        output.append(': '.join(str(x) for x in exchange) + '\n')
    return rub_currency_max, '\n'.join(output[:20])


@bot.message_handler(commands=['start'])
def start(message):
    corona = corona_curs()
    exchanges_max, exchanges = kurs_kz()
    output_message = f"""
    <u>Курс рубля в тенге:</u>
    <i><b>Золотая корона: {corona}</b></i>
    <b>Контак:≈ {corona+0.13}</b>
    <b>В обменниках: {exchanges_max}</b>\n
    {exchanges}
    """
    bot.send_message(message.chat.id, output_message, parse_mode='html')
    # if len(output_message) > 4096:
    #     for x in range(0, len(output_message), 4096):
    #         bot.send_message(message.chat.id, output_message[x:x + 4096], parse_mode='html')
    # else:
    #     bot.send_message(message.chat.id, output_message, parse_mode='html')
    # bot.send_message(message.chat.id, 'Hello press button', parse_mode='html')


# @bot.message_handler(commands=['help'])
# def website(message):
#     markup = types.ReplyKeyboardMarkup()
#     website = types.KeyboardButton('Курс рубля в тенге')
#
#     markup.add(website)
#     bot.send_message(message.chat.id, corona_curs(), reply_markup=markup)
#

bot.polling(none_stop=True)