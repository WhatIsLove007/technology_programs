import telebot
import config
import random
from telebot import types


bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    sti = open('static/welcome.webp', 'rb')
    bot.send_sticker(message.chat.id, sti)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("🗺 Карта КПИ")
    item2 = types.KeyboardButton("📖 Помочь узнать расписание")

    markup.add(item1, item2)


    bot.send_message(message.chat.id, "Приветствую, <b>{0.first_name}</b>! Зови меня - <b>{1.first_name}</b>, и я помогу тебе узнать расписания предметов и сессии КПИ!\nЧтобы узнать все возможности бота напиши /info.".format(message.from_user,
    bot.get_me()), parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['map'])
def welcome(message):
    photo = open('static/map.jpg', 'rb')
    bot.send_photo(message.chat.id, photo)


@bot.message_handler(commands=['info'])
def welcome(message):
    bot.send_message(message.chat.id, "/map - выдать карту КПИ.\n/info - показать все команды бота.\n/weather - перейти по ссылке и посмотреть погоду в Киеве.\n/creator - обратная связь.\n\n🤖 Этот бот будет и дальше поддерживаться и улучшаться.".format(message.from_user, bot.get_me()))


@bot.message_handler(commands=['weather'])
def creator(message):
    bot.send_message(message.chat.id,
                     "https://meteo.ua/34/kiev".format(
                         message.from_user, bot.get_me()))


@bot.message_handler(commands=['creator'])
def creator(message):
    bot.send_message(message.chat.id,
                     "Вот линк на разработчика: @NVV007".format(
                         message.from_user, bot.get_me()))


@bot.message_handler(content_types=['text'])
def lalala(message):
    if message.chat.type == 'private':
        if message.text == '🗺 Карта КПИ':
            photo = open('static/map.jpg', 'rb')
            bot.send_photo(message.chat.id, photo)
        elif message.text == '📖 Помочь узнать расписание':
            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("IOS", callback_data='ios')
            item2 = types.InlineKeyboardButton("Android", callback_data='android')
            item3 = types.InlineKeyboardButton("Смотреть в браузере", callback_data='web')
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, 'Вот, пользуйся из оффициальных источников:', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Я даже и не знаю что ответить, по крайней мере меня этому ещё не учили 😢')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'ios':
                bot.send_message(call.message.chat.id, 'https://apps.apple.com/ru/app/kpi-schedule/id1455536065')
            elif call.data == 'android':
                bot.send_message(call.message.chat.id, 'https://play.google.com/store/apps/details?id=com.goldenpiedevs.schedule.app&hl=ru')
            elif call.data == 'web':
                bot.send_message(call.message.chat.id, 'http://rozklad.kpi.ua/Schedules/ScheduleGroupSelection.aspx')

    except Exception as e:
        print(repr(e))


bot.polling(none_stop=True)
