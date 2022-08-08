import requests
import threading
import time
import subprocess
import os

__version__ = "1.7.6"

class Monitor:
    '''
    Monitor the live room, and record while onair
    '''
    def __init__(self, StreamPicker, gap = 30, total_try = 3, NoticeWares = []):
        '''
        initialize Monitor
        StreamPicker:     function to fetch stream url
        gap:              time gap(seconds) between two rounds
        NoticeWares:      NoticeWare list
        '''
        # gap of each check round(seconds)
        self.__gap = gap
        # total try times of StreamPicker
        self.__total_try = total_try
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
                proc = subprocess.Popen("\"ffmpeg\" -loglevel quiet -headers \"User-Agent: Mozilla/5.0 (Windows NT 6.1; rv:76.0) Gecko/20100101 Firefox/76.0\" " + 
                                    "-i \"%s\" -c copy -bsf:a aac_adtstoasc %s" % (self.__liveurl, self.__filename), 
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
                                AVCseqhRecved = False
                                AACconfRecved = False
                                MediaFrameRecvedFirst = False
                                MediaFrameRecvedSecond = False
                                starttime = 0
                                while True:
                                    tag_without_data = self.__rawread(source, 11)
                                    # metadata(script tag) not the first tag
                                    if tag_without_data[0] == 0x12 and sz != 0:
                                        print("split by metadata")
                                        break
                                    sz_tagdata = int.from_bytes(tag_without_data[1:4], 'big')
                                    tag_data = self.__rawread(source, sz_tagdata)
                                    # AVC sequence header
                                    if tag_without_data[0] == 0x9 and (tag_data[0] & 0x0f) == 7 and tag_data[1] == 0:
                                        # AVC sequence header after second media frame or
                                        # meet second AVC sequence header
                                        if AVCseqhRecved or MediaFrameRecvedSecond:
                                            print("split by AVC sequence header")
                                            break
                                        else:
                                            AVCseqhRecved = True
                                            # set timestamp of AVC sequence header to 0
                                            tag_without_data[4:8] = [0] * 4
                                    # AAC config packet
                                    elif tag_without_data[0] == 0x8 and (tag_data[0] & 0xf0) >> 4 == 0xa and tag_data[1] == 0:
                                        # AAC config packet not before all media frames or
                                        # meet second AAC config packet
                                        if AACconfRecved or MediaFrameRecvedSecond:
                                            print("split by AAC specific config")
                                            break
                                        else:
                                            AACconfRecved = True
                                            # set timestamp of AAC config packet to 0
                                            tag_without_data[4:8] = [0] * 4
                                    # video tag but not AVC sequence header or
                                    # audio tag but not AAC config packet
                                    # (normal media frame)
                                    elif (tag_without_data[0] == 0x9 and ((tag_data[0] & 0x0f) != 7 or tag_data[1] != 0)) or\
                                        (tag_without_data[0] == 0x8 and ((tag_data[0] & 0xf0) >> 4 != 0xa or tag_data[1] != 0)):
                                        if MediaFrameRecvedFirst:
                                            MediaFrameRecvedSecond = True
                                        # receive the first normal media frame then
                                        # record the start time
                                        if not MediaFrameRecvedFirst:
                                            MediaFrameRecvedFirst = True
                                            starttime = (tag_without_data[4] << 16) | (tag_without_data[5] << 8) | (tag_without_data[6])
                                            starttime |= (tag_without_data[7] << 24)
                                            tag_without_data[4:8] = [0] * 4
                                        # real timestamp = timestamp recved - starttime
                                        else:
                                            recvtime = (tag_without_data[4] << 16) | (tag_without_data[5] << 8) | (tag_without_data[6])
                                            recvtime |= (tag_without_data[7] << 24)
                                            realtime = recvtime - starttime
                                            tag_without_data[4] = (realtime & 0x00ff0000) >> 16
                                            tag_without_data[5] = (realtime & 0x0000ff00) >> 8
                                            tag_without_data[6] = (realtime & 0x000000ff)
                                            tag_without_data[7] = (realtime & 0xff000000) >> 24
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
        if os.path.exists(self.__filename) and os.path.isfile(self.__filename) and os.path.getsize(self.__filename) == 0:
            os.remove(self.__filename)
        
    def __loopMonitor(self):
        '''
        loop monitor the performer
        '''
        while True:
            # check to exit
            with self.__m_ws:
                if self.__wannastop.isSet():
                    break
            # try StreamPicker at most {total_try} times
            try_time = 0
            while True:
                try:
                    self.__OnAir, self.__RoomId, self.__checktime, self.__roomurl, self.__filename, self.__nickname, self.__liveurl = self.__StreamPicker.getStreamURL()
                    break
                except Exception as e:
                    try_time += 1
                    print("Fatal Error: StreamPicker(try time: %d)" % (try_time))
                    print(str(e))
                    if try_time == self.__total_try:
                        print("Monitor has been exited!(try exceeds)")
                        with self.__m_r:
                            self.__isRunning = False
                            exit()
                    # retry after 5 seconds
                    else:
                        self.__wannastop.wait(5)
                        with self.__m_ws:
                            if self.__wannastop.isSet():
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
                "OnAir": self.__OnAir if "_Monitor__OnAir" in vars(self) else False,
                "Lastest checktime": time.strftime("%Y-%m-%d %H:%M:%S", self.__checktime) if "_Monitor__checktime" in vars(self) else None,
                "RoomId": self.__RoomId if "_Monitor__RoomId" in vars(self) else None,
                "RoomURL": self.__roomurl if "_Monitor__roomurl" in vars(self) else None,
                "NickName": self.__nickname if "_Monitor__nickname" in vars(self) else None,
                "LiveURL": self.__liveurl if "_Monitor__liveurl" in vars(self) else None
                }
            }
