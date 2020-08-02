import requests
import threading
import time
import subprocess

__version__ = "1.4"

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

    def __rawread(self, source, n_bytes):
        '''
        read n bytes from source
        '''
        read_data = bytearray()
        while n_bytes > 0:
            chunk = source.read(n_bytes)
            sz_chunk = len(chunk)
            if sz_chunk == 0:
                raise Exception()
            read_data += chunk
            n_bytes -= sz_chunk

        return read_data

    def __downloadLive(self):
        '''
        download live stream to file
        '''
        try:
            # download HLS video depending on external FFmpeg
            if self.__liveurl.endswith(".m3u8") or self.__liveurl.find(".m3u8?") != -1:
                proc = subprocess.Popen("\"ffmpeg.exe\" -loglevel quiet -headers \"User-Agent: Mozilla/5.0 (Windows NT 6.1; rv:76.0) Gecko/20100101 Firefox/76.0\" " + 
                                    "-i \"%s\" %s" % (self.__liveurl, self.__filename), 
                                    shell = False, stdout = subprocess.DEVNULL, 
                                    stderr = subprocess.DEVNULL, stdin = subprocess.PIPE)
                while True:
                    if proc.poll() != None:
                        break
                    self.__wannastop.wait(10)
                    with self.__m_ws:
                        if self.__wannastop.isSet():
                            proc.communicate('q'.encode("GBK"))
                            break
            else:
                with requests.get(self.__liveurl, timeout = 10, stream = True, 
                                  headers = {
                                      'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:76.0) Gecko/20100101 Firefox/76.0'
                                      }) as response:
                    with open(self.__filename, "wb") as fout:
                        # download flv stream by frames
                        if self.__liveurl.endswith(".flv") or self.__liveurl.find(".flv?") != -1:
                            source = response.raw
                            sz = 0
                            # read header
                            tag = self.__rawread(source, 9)
                            sz_tag = self.__rawread(source, 4)
                            if sz == int.from_bytes(sz_tag, 'big'):
                                fout.write(tag)
                                fout.write(sz_tag)
                                fout.flush()
                                # read tags and tag pointers
                                FirstVideoFrame = True
                                while True:
                                    tag_without_data = self.__rawread(source, 11)
                                    # metadata(script tag) not the first tag
                                    if tag_without_data[0] == 0x12 and sz != 0:
                                        print("split by metadata")
                                        break
                                    sz_tagdata = int.from_bytes(tag_without_data[1:4], 'big')
                                    tag_data = self.__rawread(source, sz_tagdata)
                                    # AVC packet not the first video tag
                                    if tag_without_data[0] == 0x9 and (tag_data[0] & 0x0f) == 7 and tag_data[1] == 0:
                                        if not FirstVideoFrame:
                                            print("split by AVC sequence header")
                                            break
                                        else:
                                            FirstVideoFrame = False
                                    sz_tag = self.__rawread(source, 4)
                                    sz = 11 + sz_tagdata
                                    if sz == int.from_bytes(sz_tag, 'big'):
                                        fout.write(tag_without_data)
                                        fout.write(tag_data)
                                        fout.write(sz_tag)
                                        fout.flush()
                                    # tag size not match
                                    else:
                                        break
                                    with self.__m_ws:
                                        if self.__wannastop.isSet():
                                            break
                        # download other continuous stream directly
                        else:
                            for chunk in response.iter_content(chunk_size = 819200):
                                if chunk:
                                    fout.write(chunk)
                                    fout.flush()
                                else:
                                    break
                                with self.__m_ws:
                                    if self.__wannastop.isSet():
                                        break
        except KeyboardInterrupt:
            exit()
        except:
            print("Download Error...Retry")
        
    def __loopMonitor(self):
        '''
        loop monitor the performer
        '''
        while True:
            with self.__m_ws:
                if self.__wannastop.isSet():
                    break
            # try at most 3 times
            for try_time in range(3):
                try:
                    self.__OnAir, self.__RoomId, self.__checktime, self.__roomurl, self.__filename, self.__nickname, self.__liveurl = self.__StreamPicker.getStreamURL()
                    break
                except Exception as e:
                    print("Fatal Error: StreamPicker(try time: %d)" % (try_time + 1))
                    print(str(e))
                    if try_time == 2:
                        print("Monitor has been exited!(try exceeds)")
                        with self.__m_r:
                            self.__isRunning = False
                            exit()
            if self.__OnAir:
                print("\rOnAir: %s" % (time.strftime("%Y-%m-%d %H:%M:%S", self.__checktime)))
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

    def getInfo(self):
        '''
        get infomation about monitor, streampicker and noticeware
        '''
        return {
            "StreamPicker": self.__StreamPicker.getName(),
            "NoticeWare": [NoticeWare.getName() for NoticeWare in self.__NoticeWares],
            "Monitor Status": {
                "Running": self.__isRunning,
                "OnAir": self.__OnAir if "_Monitor__OnAir" in locals() else False,
                "Lastest checktime": time.strftime("%Y-%m-%d %H:%M:%S", self.__checktime) if "_Monitor__checktime" in locals() else None,
                "RoomId": self.__RoomId if "_Monitor__RoomId" in locals() else None,
                "RoomURL": self.__roomurl if "_Monitor__roomurl" in locals() else None,
                "NickName": self.__nickname if "_Monitor__nickname" in locals() else None, 
                "LiveURL": self.__liveurl if "_Monitor__liveurl" in locals() else None
                }
            }