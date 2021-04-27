import requests
import json
import time
import execjs
import hashlib
import re

class StreamPicker:
    def __init__(self, RoomId, skip_verify = False):
        '''
        initialize DouYu streampicker with RoomId
        RoomId:         DouYu-Live room Id
        skip_verify:    skip verification while initializing
        '''
        self.__name = "DouYu"
        self.__RoomId = RoomId
        self.__header_DouYu = {
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

    def __get_uname(self):
        '''
        get nickname of room owner
        valid room return: user nickname
        invalid room return: None
        '''
        url = "https://www.douyu.com/betard/%s" % self.__RoomId
        while True:
            try:
                response = requests.get(url, 
                                        headers = self.__header_DouYu, timeout = 10)
                roominfo_str = response.text
                response.close()
                break
            except:
                continue
        try:
            data = json.loads(roominfo_str)
            return data["room"]["nickname"]
        except:
            return None

    def __get_pc_js(self):
        '''
        NOT MY IDEA, code from https://github.com/wbt5/real-url/blob/master/douyu.py
        OnAir return: [True, StreamURL]
        Not OnAir return: [False, None]
        '''
        did = "10000000000000000000000000001501"
        while True:
            try:
                response = requests.get("https://www.douyu.com/%s" % self.__RoomId,
                                        headers = self.__header_DouYu, timeout = 10)
                content = response.text
                response.close()
                break
            except:
                continue
        result = re.search(r'(vdwdae325w_64we[\s\S]*function ub98484234[\s\S]*?)function', content).group(1)
        ub98484234 = re.sub(r'eval.*?;}', 'strc;}', result)
        ub98484234_modified = execjs.compile(ub98484234)
        res = ub98484234_modified.call('ub98484234')
        tt = str(int(time.time()))
        v = re.search(r'v=(\d+)', res).group(1)
        data = self.__RoomId + did + tt + v
        rb = hashlib.md5(data.encode('utf-8')).hexdigest()

        func_sign = re.sub(r'return rt;}\);?', 'return rt;}', res)
        func_sign = func_sign.replace('(function (', 'function sign(')
        func_sign = func_sign.replace('CryptoJS.MD5(cb).toString()', '"' + rb + '"')

        js = execjs.compile(func_sign)
        params = js.call('sign', self.__RoomId, did, tt)

        params += '&cdn=ws-h5&rate=0'
        while True:
            try:
                response = requests.get("https://www.douyu.com/lapi/live/getH5Play/%s" % self.__RoomId,
                                        params = params, headers = self.__header_DouYu, timeout = 10)
                PlayAPIContent = response.text
                response.close()
                break
            except:
                continue
        try:
            APIdata = json.loads(PlayAPIContent)
            if APIdata["error"] != 0:
                return [False, None]
            else:
                return [True, APIdata["data"]["rtmp_url"] + "/" + APIdata["data"]["rtmp_live"]]
        except:
            return [False, None]

    def getStreamURL(self):
        '''
        try to check live status
        OnAir return: [True, roomid, checktime, roomurl, fullname of output file, nickname, continuous stream url]
        Not OnAir return: [False, roomid, checktime, None, None, None, None]
        '''
        # get live status
        uname = self.__get_uname()
        if not uname:
            raise Exception("Invalid roomid")
        OnAir, stream_url = self.__get_pc_js()
        room_url = "https://www.douyu.com/%s" % (self.__RoomId)
        checktime = time.localtime()
        if not OnAir:
            outfile = None
        else:
            outfile = time.strftime("(%Y-%m-%d-%H%M%S)", checktime) + self.__RoomId + ".flv"
        return [OnAir, self.__RoomId, checktime, room_url, outfile, uname, stream_url]
           