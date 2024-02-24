# 치지직 도네이션 룰렛

[kimcore](https://github.com/kimcore)님의 [치지직 api](https://github.com/kimcore/chzzk)와 [Buddha7771](https://github.com/Buddha7771)님의 [치지직 채팅 크롤링](https://github.com/Buddha7771/ChzzkChat) 코드를 참고하여 제작하였습니다.

## 설치

```bash
$ git clone https://github.com/Malloc314159/chzzk-roulette
$ cd chzzk-roulette

$ conda create -n chzzk python=3.11
$ conda activate chzzk

$ pip install websocket
$ pip install websocket-client
$ pip install requests
```

## 쿠키 값 찾는 법

1. [치지직](https://chzzk.naver.com) 접속
2. F12를 눌러 개발자 도구 접속 후 쿠키 탭에 들어가 'NID_AUT'와 'NID_SES' 값을 찾습니다.
3. 해당 값을 main.py에 붙여 넣습니다.

## 실행

```commandline
python main.py

python main.py --streamer_id (스트리머 ID)
```
