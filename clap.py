import sounddevice as sd
import numpy as np
import time
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import keyboard  # for simulating media key

# Constants
CLAP_THRESHOLD = 0.6  # Adjust sensitivity
DETECTION_DELAY = 1   # Seconds to wait before detecting next clap

last_clap_time = 0

def detect_clap(indata, frames, time_info, status):
    global last_clap_time
    volume_norm = np.linalg.norm(indata) * 10
    current_time = time.time()

    if volume_norm > CLAP_THRESHOLD and (current_time - last_clap_time) > DETECTION_DELAY:
        print("👏 Clap detected! Toggling play/pause...")
        keyboard.send("play/pause media")  # This works on Windows
        last_clap_time = current_time

print("🎧 Listening for claps... Clap your hands to play/pause the song.")

with sd.InputStream(callback=detect_clap):
    while True:
        time.sleep(0.1)
