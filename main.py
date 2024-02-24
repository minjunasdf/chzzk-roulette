import argparse
import datetime
import logging
import json
import random as rd
from websocket import WebSocket

from chat_cmd import CHAT_CMD
import api

class ChzzkChat:

    def __init__(self, streamer, cookies, logger):

        self.streamer = streamer
        self.cookies = cookies
        self.logger = logger

        self.sid = None
        self.userIdHash = api.fetch_userIdHash(self.cookies)
        self.chatChannelId = api.fetch_chatChannelId(self.streamer)
        self.channelName = api.fetch_channelName(self.streamer)
        self.accessToken, self.extraToken = api.fetch_accessToken(self.chatChannelId, self.cookies)

        self.connect()

    def connect(self):

        sock = WebSocket()
        sock.connect('wss://kr-ss1.chat.naver.com/chat')
        print(f'{self.channelName} 채팅창에 연결 중 .', end="")

        default_dict = {
            "ver": "2",
            "svcid": "game",
            "cid": self.chatChannelId,
        }

        send_dict = {
            "cmd": CHAT_CMD['connect'],
            "tid": 1,
            "bdy": {
                "uid": self.userIdHash,
                "devType": 2001,
                "accTkn": self.accessToken,
                "auth": "SEND"
            }
        }

        sock.send(json.dumps(dict(send_dict, **default_dict)))
        sock_response = json.loads(sock.recv())
        self.sid = sock_response['bdy']['sid']
        print(f'\r{self.channelName} 채팅창에 연결 중 ..', end="")

        send_dict = {
            "cmd": CHAT_CMD['request_recent_chat'],
            "tid": 2,

            "sid": self.sid,
            "bdy": {
                "recentMessageCount": 50
            }
        }

        sock.send(json.dumps(dict(send_dict, **default_dict)))
        sock.recv()
        print(f'\r{self.channelName} 채팅창에 연결 중 ...')

        self.sock = sock
        if self.sock.connected:
            print('연결 완료')
        else:
            raise ValueError('오류 발생')

    def send(self, message: str):

        default_dict = {
            "ver": 2,
            "svcid": "game",
            "cid": self.chatChannelId,
        }

        extras = {
            "chatType": "STREAMING",
            "emojis": "",
            "osType": "PC",
            "extraToken": self.extraToken,
            "streamingChannelId": self.chatChannelId
        }

        send_dict = {
            "tid": 3,
            "cmd": CHAT_CMD['send_chat'],
            "retry": False,
            "sid": self.sid,
            "bdy": {
                "msg": message,
                "msgTypeCode": 1,
                "extras": json.dumps(extras),
                "msgTime": int(datetime.datetime.now().timestamp())
            }
        }

        self.sock.send(json.dumps(dict(send_dict, **default_dict)))

    def run(self):
        while True:
            try:
                try:
                    raw_message = self.sock.recv()
                except:
                    self.connect()
                    raw_message = self.sock.recv()

                raw_message = json.loads(raw_message)
                chat_cmd = raw_message['cmd']

                if chat_cmd == CHAT_CMD['ping']:
                    self.sock.send(
                        json.dumps({
                            "ver": "2",
                            "cmd": CHAT_CMD['pong']
                        })
                    )
                    continue

                if chat_cmd != CHAT_CMD['donation']:
                    continue

                # print(raw_message['bdy'])

                for chat_data in raw_message['bdy']:

                    if chat_data['uid'] == 'anonymous':
                        nickname = '익명의 후원자'

                    else:
                        try:
                            profile_data = json.loads(chat_data['profile'])
                            extra_data = json.loads(chat_data['extras'])
                            nickname = profile_data["nickname"]
                            donated = extra_data["payAmount"]

                        except:
                            print('error')
                            continue

                    now = datetime.datetime.fromtimestamp(chat_data['msgTime'] / 1000)
                    now = datetime.datetime.strftime(now, '%Y-%m-%d %H:%M:%S')

                    self.logger.info(f'[{now}] {nickname} : {chat_data["msg"]} / {donated}')

                    print(donated)

                    #if '룰렛' in chat_data['msg']:
                    rouletteCount=0
                    if donated >= 10000:
                        rouletteCount = donated // 10000
                        for i in range(rouletteCount):
                            result=self.roulette(2)
                            print(result)
                    else:
                        rouletteCount = donated // 1000
                        for i in range(rouletteCount):
                            result=self.roulette(1)
                            print(result)

            except:
                print('error from run function')
                pass

    def roulette(self, rNum):
        randomNum=rd.random()
        if rNum==1:
            selectedDict=r1dict
        else:
            selectedDict=r2dict
        tmpSum=0
        for k, v in selectedDict.items():
            tmpSum+=v
            if randomNum<=tmpSum:
                return k


def get_logger():
    formatter = logging.Formatter('%(message)s')

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler('chat.log', mode="w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


if __name__ == '__main__':
    with open('data.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    parser = argparse.ArgumentParser()
    parser.add_argument('--streamer_id', type=str, default=json_data['streamer_id'])
    args = parser.parse_args()

    cookies = json_data['cookie']

    r1dict=json_data['roulette']['r1dict']
    r2dict=json_data['roulette']['r2dict']

    logger = get_logger()
    chzzkchat = ChzzkChat(args.streamer_id, cookies, logger)

    chzzkchat.run()
