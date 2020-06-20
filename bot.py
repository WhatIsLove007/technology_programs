import telebot
import sqlite3
import datetime
import requests
import random
from telebot import types



TOKEN = '1287390579:AAG3EUanWJGFNaIp4E_6x1YCOM-QbuM3u64'
bot = telebot.TeleBot(TOKEN)
RusArr= {1:2, 2:3, 3:4 , 4:5 , 5:6 ,6:7, 7:1}
today = datetime.datetime.today().weekday()


def user_chat_id_try(message):
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    user_chat_id = message.chat.id

    chat_id_try = cursor.execute("SELECT * FROM `users` WHERE user_chat_id =(?)", (user_chat_id,)).fetchone()
    if chat_id_try == None:
        cursor.execute("INSERT INTO users (user_chat_id,username) VALUES ('%s','%s')" % (user_chat_id, message.chat.username))

    notification_try = cursor.execute("SELECT * FROM `notification` WHERE user_chat_id =(?)", (user_chat_id,)).fetchone()
    if notification_try == None:
        cursor.execute("INSERT INTO notification (user_chat_id) VALUES ('%s')" % (user_chat_id,))

    conn.commit()
    conn.close()
    return user_chat_id



def showDay(day, user_chat_id) :
    if day >6 :
        day=1
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    user_group = ((cursor.execute("SELECT user_group  FROM `users` WHERE user_chat_id =(?)", (user_chat_id,))).fetchone())[0]
    user_group_lessons = requests.get('https://api.rozklad.org.ua/v2/groups/{0}/timetable'.format(user_group)).json()
    if (user_group_lessons["statusCode"] == 200):
        week = requests.get('http://api.rozklad.org.ua/v2/weeks').json()
        lessons_day = user_group_lessons["data"]["weeks"][str(week['data'])]["days"][str(day)]
        text_for_send = "<b>{0}:</b>\n\n".format(lessons_day["day_name"])
        for lesson in lessons_day["lessons"]:
            text_for_send += "<b>{0}) {1}</b>  \n".format(lesson["lesson_number"], lesson["lesson_name"])
            text_for_send += "{0} {1}".format(lesson["lesson_type"], lesson["lesson_room"])
            if len(lesson["teachers"]) != 0:
                teacher = lesson["teachers"][0]
                text_for_send += " {0}\n".format(teacher["teacher_name"])
    else:
        text_for_send = 'Выберите группу с помощью команды: "/set IV-73" или "/set ІВ-73".'
    conn.close()
    return text_for_send


@bot.message_handler(commands=['monday','tuesday','wednesday','thursday','friday','saturday'])
def handle_monday(message):
    user_chat_id = user_chat_id_try(message)
    dictOfDays = {'monday':1,'tuesday':2 ,'wednesday':3,'thursday':4,'friday':5 ,'saturday':6 }
    bot.send_message(message.chat.id, showDay(dictOfDays[message.text[1:]], user_chat_id), parse_mode="HTML")


@bot.message_handler(commands=['all'])
def handle_all(message):
    user_chat_id = user_chat_id_try(message)
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    user_group = ((cursor.execute("SELECT user_group  FROM `users` WHERE user_chat_id =(?)", (user_chat_id,))).fetchone())[0]
    user_group_lessons = requests.get('https://api.rozklad.org.ua/v2/groups/{0}/timetable'.format(user_group))
    user_group_lessons = user_group_lessons.json()
    if( user_group_lessons['statusCode'] == 200):
        for week in range(1,3):
            text = '<b>Расписание для группы {0}:</b>\n'.format(user_group_lessons['data']['group']['group_full_name'], )
            text +='<b>Неделя {0}</b>.'.format(week) +'\n'
            lessons_days = user_group_lessons['data']['weeks'][str(week)]['days']
            for day in range(1,7):
                lessons_day = lessons_days[str(day)]
                lessons = lessons_day['lessons']
                if len(lessons)== 0 :
                    continue
                text += '\n<b>' + lessons_day['day_name'] + ':</b>\n'
                for lesson in lessons:
                    text += "<b>{0}) {1}</b>\n".format(lesson["lesson_number"],lesson["lesson_name"])
                    text += "{0} {1}".format(lesson["lesson_type"],lesson["lesson_room"])
                    if len(lesson["teachers"])!=0:
                       teacher = lesson["teachers"][0]
                       text += " {0}\n".format(teacher["teacher_name"])

            text += '\n'
            bot.send_message(user_chat_id, text, parse_mode="HTML")
    else:
        text = 'Визначте свою групу за домомогою команди -<code> /set </code> \nФормат  -<code> /set БС-62 </code>'
        bot.send_message(user_chat_id, text, parse_mode="HTML")
    conn.close()

@bot.message_handler(commands=['today'])
def handle_all(message):
    user_chat_id  = user_chat_id_try(message)
    text =showDay(RusArr[today] , user_chat_id )
    bot.send_message(user_chat_id ,text, parse_mode= "HTML")


@bot.message_handler(commands=['tomorrow'])
def handle_all(message):
    user_chat_id = user_chat_id_try(message)
    text =showDay(RusArr[today+1] ,  user_chat_id)
    bot.send_message( user_chat_id,text, parse_mode= "HTML")



@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, '/all - показать полное расписание для группы. \n/monday - расписание в понедельник. \n/tuesday - расписанние во вторник. '
                                      '\n/wednesday - расписание во в среду. \n/thursday  - расписание в четверг.'
                                      '\n/friday - расписание в пятницу.\n/saturday - расписание в субботу.'
                                      '\n/map - выдать карту КПИ.\n/help - показать все команды бота.'
                                      '\n/weather - перейти по ссылке и посмотреть погоду в Киеве.\n/coin - подбросить монету и решить спорную ситуацию.'
                                      '\n/creator - обратная связь.\n\n🤖 Этот бот будет поддерживаться и улучшаться.')



@bot.message_handler(commands=['map'])
def welcome(message):
    photo = open('static/map.jpg', 'rb')
    bot.send_photo(message.chat.id, photo)


@bot.message_handler(commands=['weather'])
def weather(message):
    bot.send_message(message.chat.id,
                     "https://meteo.ua/34/kiev".format(
                         message.from_user, bot.get_me()))


@bot.message_handler(commands=['creator'])
def creator(message):
    bot.send_message(message.chat.id,
                     "Вот линк на разработчика: @NVV007".format(
                         message.from_user, bot.get_me()))



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



@bot.message_handler(commands=['set'])
def handle_sunday(message):
    user_chat_id = user_chat_id_try(message)
    group_name = message.text[5:]
    if group_name == '' or None :
        bot.send_message(user_chat_id,'Группа не введена\n Формат -<code> /set БС-62 </code>',parse_mode= "HTML")
    else:
        group_inf = requests.get('http://api.rozklad.org.ua/v2/groups/{0}'.format(group_name))
        group_inf = group_inf.json()
        if group_inf['statusCode'] == 200 :
            conn = sqlite3.connect('schedule.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET user_group ='{0}' WHERE user_chat_id='{1}'".format(group_inf['data']['group_id'],user_chat_id))
            bot.send_message(user_chat_id,'Выбранная группа: <b>{0}</b>\nДля смены группы примени команду: /set.'
                                          '\nВ формате: "/set ІВ-73" или "/set IV-73".'.format(group_inf['data']['group_full_name'].upper(), ),parse_mode="HTML")
            conn.commit()
            conn.close()
        else:
            bot.send_message(user_chat_id,'Группу <b>"{0}"</b> не найдено. \nПроверьте введённые данные.'.format(group_name, ), parse_mode="HTML")




@bot.message_handler(commands=['start'])
def handle_start(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, True)
    user_markup.row('🗺 Карта КПИ', '📖 Помочь узнать расписание')
    user_markup.row('Понедельник', 'Вторник')
    user_markup.row('Среда', 'Четверг')
    user_markup.row('Пятниця', 'Суббота ')

    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    user_chat_id = user_chat_id_try(message)
    user_inf = cursor.execute("SELECT *  FROM `users` WHERE user_chat_id =(?)",(user_chat_id,))
    group_id = user_inf.fetchone()[2]
    if group_id == None or group_id=='' :
        group_name = 'Группа не выбрана.'
    else :
        group_inf = requests.get('http://api.rozklad.org.ua/v2/groups/{0}'.format(group_id))
        group_inf = group_inf.json()
        if group_inf['statusCode'] == 200 :
            group_name = group_inf["data"]["group_full_name"]
            group_name = 'Твоя выбранная группа: <b>{0}</b>.'.format(group_name.upper(),)
        else:
            group_name= 'Группа не выбрана.'
    txt = 'Приветствую, <b>'+'{0.first_name}'.format(message.from_user,bot.get_me())+'</b>!  Зови меня Хелпером! \n{1}\nДля смены группы примени команду /set.' \
          '\nНапример: "/set IV-73" или "/set ІВ-73".'.format(message.chat.username, group_name )
    sti = open('static/welcome.webp', 'rb')
    bot.send_sticker(message.chat.id, sti)
    bot.send_message(user_chat_id,txt,reply_markup=user_markup ,parse_mode= "HTML")
    conn.close()




@bot.message_handler(commands=['coin'])
def handle_start(message):
    coin = random.randint(0, 1)
    if coin == 0:
        bot.send_message(message.chat.id,"💰 Орёл.")
    else:
        bot.send_message(message.chat.id,"💰 Решка.")



@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_chat_id = user_chat_id_try(message)
    RusArr= {'Понедельник':1, 'Вторник': 2, 'Среда':3 ,'Четверг': 4, 'Пятниця' :5, 'Суббота':6}
    if (message.text in RusArr.keys()) :
        bot.send_message(user_chat_id, showDay(RusArr[message.text], user_chat_id), parse_mode="HTML")
    elif message.text == '🗺 Карта КПИ':
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
        bot.send_message(user_chat_id,
                         '<b>"{0}"</b>? Я даже и не знаю что ответить, по крайней мере меня этому ещё не учили 😢'.format(message.text, ),parse_mode="HTML")




bot.polling(none_stop=True)