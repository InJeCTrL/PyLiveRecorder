import bs4
import requests
import json
import time

class StreamPicker:
    def __init__(self, MemberId, skip_verify = False):
        '''
        initialize YiZhiBo streampicker with MemberId
        MemberId:       YiZhiBo-Live member Id
        skip_verify:    skip verification while initializing
        '''
        self.__name = "YiZhiBo"
        self.__MemberId = MemberId
        self.__header_YiZhiBo = {
            'Host': 'm.yizhibo.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:76.0) Gecko/20100101 Firefox/76.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
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
                response = requests.get("http://m.yizhibo.com/member/personel/user_works?memberid=" + self.__MemberId, 
                                        headers = self.__header_YiZhiBo, timeout = 10, allow_redirects = False)
                roompage = response.text
                response.close()
                break
            except:
                continue
        page = bs4.BeautifulSoup(roompage, 'html.parser')
        OnAir = False
        # scan all "scid" div
        for dom in page.find_all('div', attrs = {'class':'scid'}):
            while True:
                try:
                    response = requests.get("https://m.yizhibo.com/www/live/get_live_video?scid=" + dom.string, 
                                            headers = self.__header_YiZhiBo, timeout = 10)
                    videoInfoStr = response.text
                    response.close()
                    break
                except:
                    continue
            videoInfo = json.loads(videoInfoStr)
            # video status is live on air
            if videoInfo['data']['info']['status'] == 10:
                OnAir = True
                scid = dom.string
                liveurl = videoInfo['data']['info']['flvurl']
                nickname = videoInfo['data']['info']['nickname']
                break
        checktime = time.localtime()
        if OnAir:
            return [True, scid, checktime, 
                    "https://www.yizhibo.com/l/" + scid + ".html", 
                    time.strftime("(%Y-%m-%d-%H%M%S)", checktime) + self.__MemberId + ".flv",
                    nickname, liveurl]
        else:
            return [False, "", checktime, None, None, None, None]