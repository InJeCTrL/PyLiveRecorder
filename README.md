# PyLiveRecorder

> Live stream monitor module

## Introduction

An easy template to help you build a Live monitor which will loop check the live room status.

Why not support websocket?
> Although using websocket to establish the live room is an efficient method, it is hard to find universal parts among many live platforms, and some platforms don't even support websocket, so I decided to use loop check method to monitor. If you know how to use websocket to monitor a specific live platform, I think the best way is to develop your dedicate tool.

## Features

Monitor processes flv stream by frames from v1.3, this method will probably reduce live video damages like video garbled due to a new video configuration followed by the old one.

Monitor downloads hls(*.m3u8) by using external FFmpeg from v1.5, please make sure FFmpeg binary file named `ffmpeg. *` with your python script under the same folder.

## Folder Structure

```
PyLiveRecorder
|   __init__.py
|
+---Core
|       Bilibili.py
|       HuaJiao.py
|       HuYa.py
|       YiZhiBo.py
|       LongZhu.py
|       YY.py
|       __init__.py
|
\---NoticeWare
        Bilibili.py
        __init__.py
```

## Installation

You can use pip to install this module from Pypi:

```
pip install pyliverecorder
```

Or use pip to install .whl file downloaded from releases.

## Usage

For example, we can use built-in StreamPickers and Noticewares to build a Live monitor to download continuous stream like this:

```python
from PyLiveRecorder import Monitor
from PyLiveRecorder.Core.Bilibili import StreamPicker
from PyLiveRecorder.NoticeWare.Bilibili import Notice

sp = StreamPicker("roomId here")
m = Monitor(sp, 
            gap = 60,  # loop check the live room per minute
            total_try = 5, # try StreamPicker for 5 times
            NoticeWares = [Notice("Bilibili session here")])
m.start()
while True:
    cmd = input()
    # stop the monitor and exit
    if cmd == "stop":
        m.stop()
        break
    # check information about monitor (include streampicker and noticewares used)
    elif cmd == "minfo":
        print(m.getInfo())
    # output name of streampicker
    elif cmd == "spname":
        print(sp.getName())
```

Or another Live monitor to download HLS like this:

```python
from PyLiveRecorder import Monitor
from PyLiveRecorder.Core.HuYa import StreamPicker_HLS

sp = StreamPicker_HLS("roomId here")
m = Monitor(sp, 
            gap = 60,  # loop check the live room per minute
            )
m.start()
while True:
    cmd = input()
    # stop the monitor and exit
    if cmd == "stop":
        m.stop()
        break
    # check information about monitor (include streampicker and noticewares used)
    elif cmd == "minfo":
        print(m.getInfo())
    # output name of streampicker
    elif cmd == "spname":
        print(sp.getName())
```

Also we can develop our own StreamPicker like this: (4 functions below are necessary)

```python
class StreamPicker:
    def __init__(self, RoomId, skip_verify = False):
        '''
        initialize xxx streampicker with RoomId
        RoomId:     	xxx-Live room Id
        skip_verify:    skip verification while initializing
        '''
        self.__name = "xxx"
        self.__RoomId = RoomId
        pass
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
        pass
        if True:
            return [False, self.__RoomId, checktime, None, None, None, None]
        else:
            return [True, self.__RoomId, checktime, roomurl, filename, nickname, url]
```

And more, a noticeware: (4 functions below are necessary)

```python
class Notice:
    def __init__(self, ...):
        '''
        initialize xxx NoticeWare
        '''
        # name of noticeware
        self.__name = "xxx"
        pass

    def getName(self):
        '''
        return name of this
        '''
        return self.__name

    def send(self, nickname, roomurl):
        '''
        send notice to xxx
        nickname:       nickname of performer
        roomurl:        link to live room
        '''
        pass

    def remove(self):
        '''
        delete notice from xxx
        '''
        pass
```