import telebot
import pymongo

db_client = pymongo.MongoClient('mongodb://localhost:27017/')
current_db = db_client['innopoker']
clct = current_db['users']
bot = telebot.TeleBot(TOKEN)

session = {
    'players': 0,
    'idplayers': [],
    'bank': 0,
    'curbet': 0,
    'started': False
}


@bot.message_handler(commands=['start'])
def start_message(message):
    user = {
        'userid': message.chat.id,
        'username': message.chat.username,
        'balance': 0,
        'games': 0,
        'winned': 0,
        'bet': 0
    }
    findage = clct.find_one({'userid': message.chat.id})
    if findage is None:
        clct.insert_one(user)
    bot.send_message(message.chat.id,
                     "Покер-бот. Сессией управляет @wensiet\nДля того чтобы попасть в бд напиши /get_invite")


@bot.message_handler(commands=['get_invite'])
def get_invite(message):
    findage = clct.find_one({'userid': message.chat.id})
    if findage['balance'] == 0:
        clct.update_one(findage, {'$set': {'balance': 10000}})
        bot.send_message(message.chat.id, "Вы получили стартовый баланс.")
    else:
        bot.send_message(message.chat.id, "Вы уже получали старотвые фишки.")


@bot.message_handler(commands=['get_info'])
def get_info(message):
    findage = clct.find_one({'userid': message.chat.id})
    oup = "Информация по игроку: @" + str(findage['username']) + "\n\nБаланс: " + str(
        findage['balance']) + '\n' + 'Игр всего: ' + str(findage['games']) + '\n' + "Выиграно фишек: " + \
          str(findage['winned'])
    bot.send_message(message.chat.id, oup)


@bot.message_handler(commands=['join_session'])
def get_info(message):
    if session['players'] < 10 and session['started'] is False:
        session['players'] += 1
        session['idplayers'].append(message.chat.id)
        print("Игрок @" + str(message.chat.username) + " подключился к сессии.")
        bot.send_message(message.chat.id, 'Вы подключились к сессии.')
    else:
        bot.send_message(message.chat.id, 'Сессия переполнена либо игра уже идет.')


@bot.message_handler(commands=['start_session'])  # /start_session [min_bet] [bank]
def start_session(message):
    data = str(message.text).split()
    minb = data[1]
    bank = data[2]
    if message.chat.username == 'wensiet':
        full_bank = True
        temp_balance = 0
        for i in session['idplayers']:
            findage = clct.find_one({'userid': i})
            curba = findage['balance']
            idpidora = 0
            if curba < bank:
                full_bank = False
                idpidora = i
                break
        if full_bank is False:
            session['players'] -= 1
            session['idplayers'].remove(idpidora)
            bot.send_message(message.chat.id, 'Сессия не началась @' + idpidora + ' был кикнут из-за нехватки баланса.')



    pass

    # session = {
    #    'players': 0,
    #    'idplayers': [],
    #    'bank': 0,
    #    'curbet': 0,
    #    'started': False
    # }


@bot.message_handler(commands=['check'])
def make_check(message):
    findage = clct.find_one({'userid': message.chat.id})
    if findage['balance'] >= session['curbet']:

        for id in len(session['idplayers']):
            bot.send_message(id, 'Игрок @' + message.chat.username + " отказался от повышения ставки (ЧЕК).")
    else:
        bot.send_message(message.chat.id, 'Вы не можете использовать чек.')


@bot.message_handler(commands=['pass'])
def make_check(message):
    findage = clct.find_one({'userid': message.chat.id})


bot.polling(none_stop=True, interval=0)
