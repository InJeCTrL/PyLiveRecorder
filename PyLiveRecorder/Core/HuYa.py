import bs4
import requests
import json
import time

class StreamPicker:
    def __init__(self, RoomId):
        '''
        initialize HuYa streampicker with RoomId
        RoomId:     HuYa-Live room Id
        '''
        self.__name = "HuYa"
        self.__RoomId = RoomId
        self.__header_HY = {
            'Host': 'm.huya.com',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
            }
        self.__verify()

    def getName(self):
        '''
        return name of this
        '''
        return self.__name

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
        OnAir return: [True, roomid, checktime, roomurl, fullname of output file, nickname, continuous stream url]
        Not OnAir return: [False, roomid, checktime, None, None, None, None]
        '''
        while True:
            try:
                response = requests.get("https://m.huya.com/" + self.__RoomId, 
                                        headers = self.__header_HY, timeout = 10)
                roompage = response.text
                response.close()
                break
            except:
                continue
        page = bs4.BeautifulSoup(roompage, 'html.parser')
        for scriptTag in page.find_all('script', attrs = {'data-fixed':"true"}):
            content = scriptTag.string
            if content and content.find("//全局js") != -1:
                streamTag = scriptTag.string
                break
        pattern = "var ISLIVE ="
        OnAir = streamTag[streamTag.find(pattern) + len(pattern):]
        OnAir = OnAir[:OnAir.find(";")].strip()
        checktime = time.localtime()
        if OnAir != "true":
            return [False, self.__RoomId, checktime, None, None, None, None]
        pattern = "var ANTHOR_NICK = '"
        nickname = streamTag[streamTag.find(pattern) + len(pattern):]
        nickname = nickname[:nickname.find("'")].strip()
        pattern = "hasvedio: '"
        url = streamTag[streamTag.find(pattern) + len(pattern):]
        url = url[:url.find("'")].strip()
        url = "https:" + url.replace("hls.huya.com", "flv.huya.com").replace(".m3u8", ".flv").replace("_2000", "")
        return [True, self.__RoomId, checktime, 
                "https://www.huya.com/" + self.__RoomId, 
                time.strftime("(%Y-%m-%d-%H%M%S)", checktime) + self.__RoomId + ".flv", 
                nickname, url]

class StreamPicker_HLS:
    def __init__(self, RoomId):
        '''
        initialize HuYa streampicker with RoomId
        RoomId:     HuYa-Live room Id
        '''
        self.__name = "HuYa"
        self.__RoomId = RoomId
        self.__header_HY = {
            'Host': 'm.huya.com',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
            }
        self.__verify()

    def getName(self):
        '''
        return name of this
        '''
        return self.__name

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
        OnAir return: [True, roomid, checktime, roomurl, fullname of output file, nickname, HLS(*.m3u8) url]
        Not OnAir return: [False, roomid, checktime, None, None, None, None]
        '''
        while True:
            try:
                response = requests.get("https://m.huya.com/" + self.__RoomId, 
                                        headers = self.__header_HY, timeout = 10)
                roompage = response.text
                response.close()
                break
            except:
                continue
        page = bs4.BeautifulSoup(roompage, 'html.parser')
        for scriptTag in page.find_all('script', attrs = {'data-fixed':"true"}):
            content = scriptTag.string
            if content and content.find("//全局js") != -1:
                streamTag = scriptTag.string
                break
        pattern = "var ISLIVE ="
        OnAir = streamTag[streamTag.find(pattern) + len(pattern):]
        OnAir = OnAir[:OnAir.find(";")].strip()
        checktime = time.localtime()
        if OnAir != "true":
            return [False, self.__RoomId, checktime, None, None, None, None]
        pattern = "var ANTHOR_NICK = '"
        nickname = streamTag[streamTag.find(pattern) + len(pattern):]
        nickname = nickname[:nickname.find("'")].strip()
        pattern = "hasvedio: '"
        url = streamTag[streamTag.find(pattern) + len(pattern):]
        url = url[:url.find("'")].strip()
        url = "https:" + url.replace("_2000", "")
        return [True, self.__RoomId, checktime, 
                "https://www.huya.com/" + self.__RoomId, 
                time.strftime("(%Y-%m-%d-%H%M%S)", checktime) + self.__RoomId + ".mp4", 
                nickname, url]