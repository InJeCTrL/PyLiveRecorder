import requests
import json
import time

class StreamPicker:
    def __init__(self, UserId, skip_verify = False):
        '''
        initialize LongZhu streampicker with UserId
        UserId:         LongZhu-Live user Id
        skip_verify:    skip verification while initializing
        '''
        self.__name = "LongZhu"
        self.__UserId = UserId
        self.__header_LongZhu = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:76.0) Gecko/20100101 Firefox/76.0',
            'Cache-Control': 'no-cache'
            }
        if not skip_verify:
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
        # get live status by userid
        while True:
            try:
                response = requests.get("http://userapi.longzhu.com/user/spaceheader?userid=" + self.__UserId, 
                                        headers = self.__header_LongZhu, timeout = 10)
                userinfo_str = response.text
                response.close()
                break
            except:
                continue
        userinfo = json.loads(userinfo_str)
        checktime = time.localtime()
        if userinfo['room']['isLive'] == False:
            return [False, "", checktime, None, None, None, None]
        nickname = userinfo['user']['nickname']
        roomId = str(userinfo['room']['id'])
        # get stream url
        while True:
            try:
                response = requests.get("http://livestream.longzhu.com/live/getlivePlayurl?hostPullType=2&isAdvanced=true&playUrlsType=1&roomId=" + roomId, 
                                        headers = self.__header_LongZhu, timeout = 10)
                streaminfo_str = response.text
                response.close()
                break
            except Exception as e:
                continue
        streaminfo = json.loads(streaminfo_str)
        url = streaminfo['playLines'][0]['urls'][len(streaminfo['playLines'][0]['urls']) - 1]['securityUrl']
        roomurl = streaminfo['liveUrl']
        return [True, roomId, checktime, 
                roomurl, 
                time.strftime("(%Y-%m-%d-%H%M%S)", checktime) + self.__UserId + ".flv", 
                nickname, url]