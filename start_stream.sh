#!/bin/bash

#find the streaming script PID
STREAM_PID=$(pgrep -f "stream_to_youtube.py")

#check if PID is found and restart
if [ ! -z "$STREAM_PID" ]; then
    echo "Stopping and restarting stream..."
    kill $STREAM_PID
    nohup python3 ./stream_to_youtube.py > ./log/youtube_stream.log 2>&1 &
else
    nohup python3 ./stream_to_youtube.py > ./log/youtube_stream.log 2>&1 &
    echo "starting stream now..."
fi
