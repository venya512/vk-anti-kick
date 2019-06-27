import requests
import json
from threading import Thread
import sys

print('reading "config.txt"')
i = 0
couple  = [{}, {}]
file = open('config.txt', 'r')
try:
    for line in file:
        couple[i]['id'] = int(line[:9])
        couple[i]['token'] = str(line[10:95])
        i+=1
except:
    print('Invalid id/token\nEdit "config.txt"')
    input('Press [Enter] to exit')
    sys.exit()

def antikick(token, tm_id):
    # get information about the server
    response = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                            method = 'messages.getLongPollServer',
                            params = 'need_pts=0&ip_version=3',
                            token = token)
                            ).json()
    ts = response['response']['ts']
    key = response['response']['key']
    server = response['response']['server']
    print('\nreceived longpool server:\n{server}'.format(server = server))
    while True:
        # connecting to longpool server
        response = requests.get('https://{server}?act=a_check&key={key}&ts={ts}&wait=25&mode=2&version=3'.format(
                                server = server,
                                key = key,
                                ts = ts)
                                ).json()
        # recieve first timestamp
        ts = response['ts']
        # receive events
        for event in response['updates']:
            if event[0] == 52 and event[1] == 8:
                id = event[3]
                chat_id = event[2] - 2000000000
                #print('User id%s has ben kicked from chat %s' % (id, chat_id))
                if id  == tm_id:
                    response = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                                            method = 'messages.addChatUser',
                                            params = 'chat_id={}&user_id={}'.format(chat_id, tm_id),
                                            token = token)
                                            ).json()
                    if response['response'] == 1:
                        print('def %s' % tm_id)

defense_1 = Thread(target = antikick, args = (couple[0]['token'], couple[0]['id']))
defense_2 = Thread(target = antikick, args = (couple[1]['token'], couple[1]['id']))
defense_1.start()
defense_2.start()
