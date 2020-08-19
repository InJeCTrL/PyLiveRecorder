import bs4
import requests
import json
import time

class StreamPicker:
    def __init__(self, UserId, skip_verify = False):
        '''
        initialize HuaJiao streampicker with UserId
        UserId:         HuaJiao-Live user Id
        skip_verify:    skip verification while initializing
        '''
        self.__name = "HuaJiao"
        self.__UserId = UserId
        self.__header_HuaJiao = {
            #'Host': 'webh.huajiao.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:76.0) Gecko/20100101 Firefox/76.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection': 'keep-alive',
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
        while True:
            try:
                response = requests.get("https://webh.huajiao.com/User/getUserFeeds?uid=" + self.__UserId, 
                                        headers = self.__header_HuaJiao, timeout = 10)
                userfeeds_str = response.text
                response.close()
                break
            except:
                continue
        userfeeds = json.loads(userfeeds_str)['data']['feeds']
        checktime = time.localtime()
        for userfeed in userfeeds:
            feed = userfeed['feed']
            # find an onair live
            if "replay_status" in feed and feed['replay_status'] == 0:
                roomid = str(feed['relateid'])
                sn = feed['sn']
                # get nickname
                while True:
                    try:
                        response = requests.get("https://www.huajiao.com/user/" + self.__UserId, 
                                                headers = self.__header_HuaJiao, timeout = 10)
                        userInfo_str = response.text
                        response.close()
                        break
                    except:
                        continue
                userInfo_page = bs4.BeautifulSoup(userInfo_str, 'html.parser')
                info = userInfo_page.find_all('div', attrs = {'class':'info'})[0]
                nickname = info.find_all('span')[0].text
                # get stream url
                while True:
                    try:
                        response = requests.get("https://live.huajiao.com/live/substream?encode=h265&sn=" + sn + "&uid=" + self.__UserId + "&liveid=" + roomid, 
                                                headers = self.__header_HuaJiao, timeout = 10)
                        substream_str = response.text
                        response.close()
                        break
                    except Exception as e:
                        print(str(e))
                        continue
                substream = json.loads(substream_str)
                url = substream['data']['main']
                return [True, roomid, checktime, 
                        "https://www.huajiao.com/l/" + roomid, 
                        time.strftime("(%Y-%m-%d-%H%M%S)", checktime) + self.__UserId + ".flv", 
                        nickname, url]
        return [False, "", checktime, None, None, None, None]