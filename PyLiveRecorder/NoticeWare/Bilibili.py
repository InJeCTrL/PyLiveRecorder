import requests
import threading
import json

class Notice:
    def __init__(self, bili_session, ex_content = "For more details, check https://github.com/InJeCTrL/PyLiveRecorder"):
        '''
        initialize Bilibili NoticeWare with Bilibili session and extra message
        '''
        # name of noticeware
        self.__name = "Bilibili Dynamic"
        self.__header_Bili = {
            'Host': 'api.vc.bilibili.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:76.0) Gecko/20100101 Firefox/76.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'SESSDATA=' + bili_session,
            'Origin': 'https://t.bilibili.com'
            }
        self.__ex_content = ex_content
        self.__m_Id = threading.Lock()
        self.__dynamicId = None

    def getName(self):
        '''
        return name of this
        '''
        return self.__name

    def send(self, nickname, roomurl):
        '''
        send notice to bili-dynamic
        nickname:       nickname of performer
        roomurl:        link to live room
        '''
        payload =  {
            'dynamic_id': '0',
            'type': '4',
            'rid': '0',
            'content': 'Live On Air Now!\nNickName: %s\nURl: %s\n\n%s' % (nickname, roomurl, self.__ex_content),
            'extension': json.dumps({'from': {
                'emoji_type': 1
                }}, ensure_ascii = False).encode('utf-8'),
            'at_uids': None,
            'ctrl': '[]'
            }
        while True:
            try:
                response = requests.post("https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/create", data = payload, headers = self.__header_Bili)
                data_raw = response.text
                response.close()
                break
            except:
                continue
        data = json.loads(data_raw)
        if data['code'] == 0:
            print('\nBilibili Push Successfully!')
            with self.__m_Id:
                self.__dynamicId = data['data']['dynamic_id_str']
        else:
            print('\nBilibili Push Failed!')

    def remove(self):
        '''
        delete Bilibili dynamic
        '''
        with self.__m_Id:
            if self.__m_Id:
                while True:
                    try:
                        response = requests.post("https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/rm_dynamic", 
                                                 data = {'dynamic_id': self.__dynamicId}, headers = self.__header_Bili)
                        data_raw = response.text
                        response.close()
                        break
                    except:
                        continue
                data = json.loads(data_raw)
                if data['code'] == 0:
                    print('\nBilibili Dynamic Delete Successfully!')
                    self.__dynamicId = None
                else:
                    print('\nBilibili Dynamic Delete Failed!')