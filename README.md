# PyLiveRecorder

> Live stream monitor module

## Introduction

An easy template to help you build a Live monitor which will loop check the live room status.

Why not support websocket?
> Although using websocket to establish the live room is an efficient method, it is hard to find universal parts among many live platforms, and some platforms don't even support websocket, so I decided to use loop check method to monitor. If you know how to use websocket to monitor a specific live platform, I think the best way is to develop your dedicate tool.

Why not support HLS (*.m3u8)?
> It means the program will loop check the remote *.m3u8 file while live is on air to keep downloading the live stream, I think it's not so efficient. What's more, HLS cut the whole live stream into many *.ts files, combining these file into a single file toughly(copy /b ...) may cause other problems(timestamp err...), and using ffmpeg to remix media stream will add external dependencies.

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
|       __init__.py
|
\---NoticeWare
        Bilibili.py
        __init__.py
```

## Install

You can use pip to install this module from Pypi:

```
pip install pyliverecorder
```

Or use pip to install .whl file downloaded from releases.

## Usage

For example, we can use built-in StreamPickers and Noticewares to build a Live monitor like this:

```python
from PyLiveRecorder import Monitor
from PyLiveRecorder.Core.Bilibili import StreamPicker
from PyLiveRecorder.NoticeWare.Bilibili import Notice

m = Monitor(StreamPicker("roomId here"), 
            gap = 60,  # loop check the live room per minute
            NoticeWares = [Notice("Bilibili session here")])
m.start()
while True:
    if input() == "stop":
        m.stop()
        break
```

Also we can develop our own StreamPicker like this: (3 functions below are necessary)

```python
class StreamPicker:
    def __init__(self, RoomId):
        '''
        initialize xxx streampicker with RoomId
        RoomId:     xxx-Live room Id
        '''
        self.__RoomId = RoomId
        pass
        self.__verify()

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
        OnAir return: [True, roomid, checktime, roomurl, fullname of output file, nickname, stream(flv) url]
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