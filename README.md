# Raspberry_Pi_Livestream
This is the code I use to stream live footage from my Raspberry Pi to Youtube. To replicate this project, you'll need to set your environment variables for your YouTube stream URL and Key. If you want to include music, just replace the sample directory with the location of your audio file. I also included a requirements.txt file to download the necessary python packages.

- stream_to_youtube.py: python script to stream footage to Youtube using ffmpeg and Picamera2.
- start_stream.sh: simple bash script to start the stream/restart the stream if already running.
- stop_stream.sh: bash script to stop the stream while its running.
