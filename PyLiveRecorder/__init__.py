import requests
import threading
import time

__version__ = "1.0"

class Monitor:
    '''
    Monitor the live room, and record while onair
    '''
    def __init__(self, StreamPicker, gap = 30, NoticeWares = []):
        '''
        initialize Monitor
        StreamPicker:     function to fetch stream url
        gap:              time gap(seconds) between two rounds
        NoticeWares:      NoticeWare list
        '''
        # gap of each check round(seconds)
        self.__gap = gap
        self.__StreamPicker = StreamPicker
        self.__NoticeWares = NoticeWares
        # mutex of wannastop flag
        self.__m_ws = threading.Lock()
        # whether to stop monitor
        self.__wannastop = threading.Event()
        # mutex of monitor status
        self.__m_r = threading.Lock()
        # status of monitor
        self.__isRunning = False

    def __downloadLive(self):
        '''
        download live stream to file
        '''
        try:
            with requests.get(self.__liveurl, timeout = 10, stream = True, 
                              headers = {
                                  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:76.0) Gecko/20100101 Firefox/76.0'
                                  }) as response:
                with open(self.__filename, "wb") as fout:
                    for chunk in response.iter_content(chunk_size = 819200):
                        if chunk:
                            fout.write(chunk)
                        with self.__m_ws:
                            if self.__wannastop.isSet():
                                break
        except KeyboardInterrupt:
            exit()
        except:
            print("\nDownload Error...Retry")
        
    def __loopMonitor(self):
        '''
        loop monitor the performer
        '''
        while True:
            with self.__m_ws:
                if self.__wannastop.isSet():
                    break
            try:
                self.__OnAir, self.__RoomId, self.__checktime, self.__roomurl, self.__filename, self.__nickname, self.__liveurl = self.__StreamPicker.getStreamURL()
            except Exception as e:
                print("Fatal Error: StreamPicker")
                print(str(e))
                exit()
            if self.__OnAir:
                print("\rOnAir: %s" % (time.strftime("%Y-%m-%d %H:%M:%S", self.__checktime)), end = '', flush = True)
                # OnAir notice
                for nw in self.__NoticeWares:
                    try:
                        nw.send(self.__nickname, self.__roomurl)
                    except:
                        print("Error: NoticeWare(OnAir notice) - %s" % (nw.getName()))
                self.__downloadLive()
                # OffAir notice
                for nw in self.__NoticeWares:
                    try:
                        nw.remove()
                    except:
                        print("Error: NoticeWare(OffAir notice) - %s" % (nw.getName()))
            else:
                print("\rIDLE: %s" % (time.strftime("%Y-%m-%d %H:%M:%S", self.__checktime)), end = '', flush = True)
                self.__wannastop.wait(self.__gap)

    def start(self):
        '''
        start monitor
        '''
        with self.__m_r:
            if not self.__isRunning:
                self.__isRunning = True
                self.__th_monitor = threading.Thread(target = self.__loopMonitor, daemon = True)
                self.__th_monitor.start()

    def stop(self):
        '''
        terminate monitor
        '''
        with self.__m_ws:
            self.__wannastop.set()
        self.__th_monitor.join()
        with self.__m_ws:
            self.__wannastop.clear()
        with self.__m_r:
            if self.__isRunning:
                self.__isRunning = False