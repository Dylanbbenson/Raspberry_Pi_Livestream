from time import sleep
import subprocess
import logging
from picamera2 import Picamera2, Preview
from decouple import config
from dotenv import load_dotenv

#load environment variables
load_dotenv(dotenv_path='./config/config.env')
YOUTUBE_URL = config('YOUTUBE_URL')
YOUTUBE_KEY = config('YOUTUBE_KEY')
MUSIC_FILE = "path/to/musicfile"

#logging
logging.basicConfig(level=logging.INFO, filename='streaming.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

#manually configured camera settings
RESOLUTION = (1280, 720)
FRAMERATE = 23  #optimal frame rate to match LED light

#construct ffmpeg command 
stream_cmd = [
    'ffmpeg',
    '-f', 'rawvideo',
    '-pix_fmt', 'rgb24',
    '-s', f'{RESOLUTION[0]}x{RESOLUTION[1]}',
    '-r', f'{FRAMERATE}',
    '-i', '-',
    '-stream_loop', '-1',
    '-i', MUSIC_FILE,
    '-f', 'lavfi',
    '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-preset', 'veryfast',
    '-g', '50',
    '-b:v', '2500k',
    '-c:a', 'aac',
    '-b:a', '128k',
    '-ar', '44100',
    '-f', 'flv',
    f'{YOUTUBE_URL}/{YOUTUBE_KEY}'
]

def setup_camera() -> camera:
    camera = Picamera2()
    camera_config = camera.create_video_configuration(main={"size": RESOLUTION, "format": "RGB888"})
    camera.configure(camera_config)
    camera.set_controls({"FrameRate": FRAMERATE})
    camera.start()
    sleep(2)
    return camera

def start_ffmpeg():
    log_file = open('ffmpeg_log.txt', 'w')
    logging.info(f"Starting ffmpeg with command: {' '.join(stream_cmd)}")
    try:
        stream_pipe = subprocess.Popen(stream_cmd, stdin=subprocess.PIPE, stderr=log_file)
    except Exception as err:
        logging.error(f"Failed to start ffmpeg: {err}")
        log_file.close()
        raise
    return stream_pipe, log_file

#write frame data to ffmpeg 
def write_frame(request, stream_pipe, camera, log_file) -> None:
    try:
        frame = request.make_array("main")
        stream_pipe.stdin.write(frame.tobytes())
    except BrokenPipeError:
        logging.error("Broken pipe: fmpeg process terminated.")
        cleanup(camera, stream_pipe, log_file)
        raise

#clean up resources post-stream
def cleanup(camera, stream_pipe, log_file) -> None:
    if camera:
        camera.stop()
        camera.close()
    if stream_pipe.stdin:
        stream_pipe.stdin.close()
    if stream_pipe:
        stream_pipe.wait()
    if log_file:
        log_file.close()
    logging.info("Stopped recording and cleaned up resources.")

def main():
    try:
        camera = setup_camera()
        stream_pipe, log_file = start_ffmpeg()
        camera.post_callback = lambda request: write_frame(request, stream_pipe, camera, log_file)
        logging.info("Started recording and streaming.")
        while True:
            sleep(60)
    except KeyboardInterrupt:
        logging.info("Interrupted by user.")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        cleanup(camera, stream_pipe, log_file)

        logging.info("Restarting stream...")
        sleep(5)

        #read ffmpeg log file
        with open('ffmpeg_log.txt', 'r') as log_file:
            ffmpeg_logs = log_file.read()
            logging.info(f"FFmpeg logs:\n{ffmpeg_logs}")


if __name__ == '__main__':
    main()
