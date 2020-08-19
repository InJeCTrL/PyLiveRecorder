import requests
import json
import time
import base64

class StreamPicker:
    def __init__(self, SId, skip_verify = False):
        '''
        initialize YY streampicker with SId
        SId:            YY-Live room Id(from live room url)
        skip_verify:    skip verification while initializing
        '''
        self.__name = "YY"
        self.__SId = SId
        self.__header_YY = {
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
        except Exception as e:
            print("Input Id or this module is invalid!")
            exit()

    def getStreamURL(self):
        '''
        try to check live status
        OnAir return: [True, roomid, checktime, roomurl, fullname of output file, nickname, continuous stream url]
        Not OnAir return: [False, roomid, checktime, None, None, None, None]
        '''
        # get stream status
        while True:
            try:
                response = requests.post("https://stream-manager.yy.com/v3/channel/streams?uid=0&cid=%s&sid=%s&encode=json" % (self.__SId, self.__SId), 
                                        headers = self.__header_YY, timeout = 10,
                                        data = json.dumps({
                                            'appid': 0,
                                            'cid': int(self.__SId),
                                            'sid': int(self.__SId),
                                            'uid': 0,
                                            'avp_parameter': {
                                                'gear': 5,
                                                'imsi': 0,
                                                'line_seq': -1,
                                                'room_id': int(self.__SId),
                                                'uid': 0,
                                                'version': 1,
                                                'sdk_version': 2006161027
                                                },
                                            'client_attribute': {
                                                'client': "web",
                                                'height': "1080",
                                                'width': "1920"
                                                }
                                            }))
                streaminfo_str = response.text
                response.close()
                break
            except Exception as e:
                continue
        streaminfo = json.loads(streaminfo_str)
        checktime = time.localtime()
        if "avp_payload" not in streaminfo:
            return [False, self.__SId, checktime, None, None, None, None]
        uid = str(streaminfo['channel_stream_info']['streams'][0]['uid'])
        stream_url = str(base64.b64decode(streaminfo['avp_payload']['data']))
        stream_url = stream_url[stream_url.find("http"):]
        stream_url = stream_url[:stream_url.find("\\x00")]
        while True:
            try:
                response = requests.get("https://www.yy.com/api/liveInfoDetail/%s/%s/%s" % (self.__SId, self.__SId, uid), 
                                        headers = self.__header_YY, timeout = 10)
                userinfo_str = response.text
                response.close()
                break
            except:
                continue
        userinfo = json.loads(userinfo_str)
        nickname = userinfo['data']['name']
        return [True, self.__SId, checktime, 
                "https://www.yy.com/" + self.__SId, 
                time.strftime("(%Y-%m-%d-%H%M%S)", checktime) + self.__SId + ".flv", 
                nickname, stream_url]