import argparse
import datetime
import logging
import json
import random as rd
from websocket import WebSocket

from chat_cmd import CHAT_CMD
import api

from flask import Flask,render_template


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
                        extra_data = json.loads(chat_data['extras'])
                        donated = extra_data["payAmount"]

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


                    # 대충 룰렛 로그 적어두기
                    # self.logger.info(f'[{now}] {nickname} : {chat_data["msg"]} / {donated}')

                    print(donated)

                    # if '룰렛' in chat_data['msg']:
                    for k in roulettelist:
                        rouletteCount = donated // k
                        donated -= rouletteCount*k
                        for i in range(rouletteCount):
                            result = self.roulette(k)
                            print(result)
                    

            except:
                print('error from run function')

    def roulette(self, rNum):
        selectedDict = json_data['roulette'][str(rNum)]
        return rd.choices(list(selectedDict.keys()), weights=list(selectedDict.values()), k=1)[0]



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

app = Flask(__name__)

@app.route("/")
def web_roulette():
    return "<p>hello</p>"

@app.route("/<string:streamer_id>/")
def roulette(streamer_id):
    return render_template('roulette.html')

if __name__ == '__main__':
    with open('data.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    parser = argparse.ArgumentParser()
    parser.add_argument('--streamer_id', type=str, default=json_data['streamer_id'])
    args = parser.parse_args()

    cookies = json_data['cookie']

    roulettelist = sorted(list(map(int, list(json_data['roulette'].keys()))), reverse=True)

    logger = get_logger()
    chzzkchat = ChzzkChat(args.streamer_id, cookies, logger)
    
    app.run()

    chzzkchat.run()
