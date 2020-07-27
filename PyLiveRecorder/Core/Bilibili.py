import requests
import json
import time

class StreamPicker:
    def __init__(self, RoomId):
        '''
        initialize Bilibili streampicker with RoomId
        RoomId:     Bilibili-Live room Id
        '''
        self.__RoomId = RoomId
        self.__header_Bilibili = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:76.0) Gecko/20100101 Firefox/76.0',
            'Cache-Control': 'no-cache'
            }
        self.__verify()

    def __verify(self):
        '''
        verify if Id or this module is valid
        '''
        try:
            self.getStreamURL()
        except:
            print("Input Id or this module is invalid!")
            exit()

    def getStreamURL(self):
        '''
        try to check live status
        OnAir return: [True, roomid, checktime, roomurl, fullname of output file, nickname, stream(flv) url]
        Not OnAir return: [False, roomid, checktime, None, None, None, None]
        '''
        # get live status
        while True:
            try:
                response = requests.get("https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id=" + self.__RoomId, 
                                        headers = self.__header_Bilibili, timeout = 10)
                roominfo_str = response.text
                response.close()
                break
            except:
                continue
        roominfo = json.loads(roominfo_str)
        OnAir = True if roominfo['data']['room_info']['live_status'] == 1 else False
        checktime = time.localtime()
        if not OnAir:
            return [False, self.__RoomId, checktime, None, None, None, None]
        nickname = roominfo['data']['anchor_info']['base_info']['uname']
        while True:
            try:
                response = requests.get("https://api.live.bilibili.com/xlive/web-room/v1/playUrl/playUrl?platform=web&quality=0&cid=" + self.__RoomId, 
                                        headers = self.__header_Bilibili, timeout = 10)
                liveinfo_str = response.text
                response.close()
                break
            except:
                continue
        liveinfo = json.loads(liveinfo_str)
        durl = liveinfo['data']['durl'][0]['url']
        return [True, self.__RoomId, checktime, 
                "https://live.bilibili.com/" + self.__RoomId, 
                time.strftime("(%Y-%m-%d-%H%M%S)", checktime) + self.__RoomId + ".flv", 
                nickname, durl]
           