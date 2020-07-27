import bs4
import base64
import requests
import random
import json
import time

class StreamPicker:
    def __init__(self, RoomId):
        '''
        initialize HuYa streampicker with RoomId
        RoomId:     HuYa-Live room Id
        '''
        self.__RoomId = RoomId
        self.__header_HY = {
            'Host': 'www.huya.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:76.0) Gecko/20100101 Firefox/76.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection': 'keep-alive',
            'TE': 'Trailers',
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
        while True:
            try:
                # add random to avoid cache from proxy server
                response = requests.get("https://www.huya.com/" + self.__RoomId + "?t=" + str(random.uniform(10, 100)), 
                                        headers = self.__header_HY, timeout = 10)
                roompage = response.text
                response.close()
                break
            except:
                continue
        page = bs4.BeautifulSoup(roompage, 'html.parser')
        streamTag = page.select("body script")[6].string
        begin_pt = streamTag.find('"stream": ')
        end_pt = streamTag.find('window.TT_LIVE_TIMING = {};')
        streamInfo_str = streamTag[begin_pt : end_pt]
        streamInfo_str = streamInfo_str.replace('\n', '').replace(' ', '').replace('"stream":', '')[:-3]
        checktime = time.localtime()
        if streamInfo_str == 'null':
            return [False, self.__RoomId, checktime, None, None, None, None]
        else:
            streamInfo_str = base64.b64decode(streamInfo_str)
            streamInfo = json.loads(streamInfo_str)
            nickname = streamInfo['data'][0]['gameLiveInfo']['nick']
            url = streamInfo['data'][0]['gameStreamInfoList'][0]['sFlvUrl'] + '/' + streamInfo['data'][0]['gameStreamInfoList'][0]['sStreamName'] + '.flv?' +  streamInfo['data'][0]['gameStreamInfoList'][0]['sFlvAntiCode'].replace('amp;', '')
            return [True, self.__RoomId, checktime, 
                    "https://www.huya.com/" + self.__RoomId, 
                    time.strftime("(%Y-%m-%d-%H%M%S)", checktime) + self.__RoomId + ".flv", 
                    nickname, url]
           