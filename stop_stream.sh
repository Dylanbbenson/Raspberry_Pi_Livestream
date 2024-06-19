#!/bin/bash

#find the streaming script PID
STREAM_PID=$(pgrep -f "stream_to_youtube.py")

#check if PID is found and terminate
if [ ! -z "$STREAM_PID" ]; then
    echo "Stopping stream with PID $STREAM_PID"
    kill $STREAM_PID
else
    echo "Stream not running."
fi
