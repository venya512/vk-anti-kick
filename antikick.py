import requests
import json
from threading import Thread
import sys

def get_id(token, nout=False):
    response = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                            method = 'users.get',
                            params = '',
                            token = token)
                            ).json()
    if 'response' in response.keys():
        id = str(response['response'][0]['id'])
        first_name = response['response'][0]['first_name']
        last_name = response['response'][0]['last_name']
        if nout:
            return (id, first_name, last_name)
        else:
            print('\033[92m [+] Получен id для %s (%s..) - %s \033[0m' % (first_name, token[:10], id))
            return (id, first_name, last_name)
    else:
        print('\033[91m [-] Ответ от сервера не получен; Ошибка: \033[0m')
        print(response['error']['error_msg'])
        if len(token) != 85:
            print('\033[91m [-] Длина токена должна быть = 85 \033[0m' % len(token))
        raise ValueError

def antikick(token, def_id, user):
    owner_id, first_name, last_name = user
    def_id_ = def_id[:]
    def_id_.remove(owner_id)
    # get information about the server
    response = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                            method = 'messages.getLongPollServer',
                            params = 'need_pts=0&ip_version=3',
                            token = token)
                            ).json()
    try:
        ts = response['response']['ts']
        key = response['response']['key']
        server = response['response']['server']
        print('\033[92m [+] Получен longpoll-сервер для {name} - {server} \033[0m'.format(name = first_name, server = server))
        while True:
            response = requests.get('https://{server}?act=a_check&key={key}&ts={ts}&wait=25&mode=2&version=3'.format(
                                    server = server,
                                    key = key,
                                    ts = ts)
                                    ).json()
            ts = response['ts']
            for event in response['updates']:
                if event[0] == 52 and event[1] == 8:
                    id = str(event[3])
                    chat_id = event[2] - 2000000000
                    #print('\033[92m [%s] %s кикнут из беседы %s \033[0m' % (owner_id, id, chat_id))
                    if id in def_id_:
                        response = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                                                method = 'messages.addChatUser',
                                                params = 'chat_id={}&user_id={}'.format(chat_id, id),
                                                token = token)
                                                ).json()
                        if 'response' in response.keys():
                            if response['response'] == 1:
                                print('\033[92m [%s] %s возвращен в беседу \033[0m' % (owner_id, id))
                        else:
                            print('\033[91m [%s] %s уже возвращен \033[0m' % (owner_id, id))
                            continue

    except KeyError as e:
        print('\033[91m [%s] Ошибка в ответе сервера - не хватает данных (ключа) \033[0m' % owner_id)
        print(e)
        print('\n', response)
    except Exception as e:
        print('\033[91m [%s] Неопознанная ошибка \033[0m' % owner_id)
        print(e)
        print('\n', response)

try:
    file = open('config.txt', 'r')
    # Файл уже существует
    print('\033[92m [+] Найден файл конфига \033[0m')
    ffstr = file.readlines()
    #print(ffstr)
    if ffstr == []:
        print('\033[91m [-] Файл пустой \033[0m')
        print('\033[92m [-] Заполняем \033[0m')
        file = open('config.txt', 'w')
        cfg = {}
        def_ids = []
        tokens = []
        ids = []
        for i in range(int(input('Введите кол-во аккаунтов - '))):
            cfg[i] = {}
            cfg[i]['token']  = input('Введите access_token %s-го аккаунта (85 символов) - ' % (i+1))
            cfg[i]['id'], cfg[i]['name'], _  = get_id(cfg[i]['token'])
            def_ids.append(cfg[i]['id'])
            tokens.append(cfg[i]['token'])
            file.write('%s %s\n' % (cfg[i]['id'], cfg[i]['token']))
        for acc in tokens:
            defense = Thread(target = antikick, args = (acc, ids, get_id(acc, nout=True)))
            defense.start()
        file.close()

    elif all([len(line) < 96 for line in ffstr]):
        print('\033[91m [-] Неправильынй формат ввееднных данных \033[0m')
        input('Press Enter to EXIT')
        sys.exit()

    elif len(ffstr) < 2:
        print('\033[91m [-] Сохранен только 1 аккаунт \033[0m')
        input('Press Enter to EXIT')
        sys.exit()

    else:
        tokens = []
        ids = []
        for line in ffstr:
            id, token = line.split()
            ids.append(id)
            tokens.append(token)

        for acc in tokens:
            defense = Thread(target = antikick, args = (acc, ids, get_id(acc, nout=True)))
            defense.start()

# Файл неполный или поврежденный
except FileNotFoundError as e:
    #print(e)
    print('\033[91m [-] Файл не найден или поврежден \033[0m')
    print('\033[92m [+] Запись данных в  "config.txt" \033[0m')
    file = open('config.txt', 'w')
    cfg = {}
    def_ids = []
    tokens = []
    for i in range(int(input('Введите кол-во аккаунтов - '))):
        cfg[i] = {}
        cfg[i]['token']  = input('Введите access_token %s-го аккаунта (85 символов) - ' % i)
        cfg[i]['id'], cfg[i]['name'], _  = get_id(cfg[i]['token'])
        def_ids.append(cfg[i]['id'])
        tokens.append(cfg[i]['token'])
        file.write('%s %s\n' % (cfg[i]['id'], cfg[i]['token']))
    for acc in tokens:
        defense = Thread(target = antikick, args = (acc, def_ids, get_id(acc, nout=True)))
        defense.start()
