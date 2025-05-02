import cv2
import numpy as np
import time
import math
import mediapipe as mp
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Pycaw setup for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

# Mediapipe hand detection setup
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

# OpenCV webcam setup
cap = cv2.VideoCapture(0)
pTime = 0

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    lmList = []
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((id, cx, cy))

    if lmList:
        x1, y1 = lmList[4][1], lmList[4][2]   # Thumb tip
        x2, y2 = lmList[8][1], lmList[8][2]   # Index finger tip
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # Draw visuals
        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
        cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

        # Calculate distance
        length = math.hypot(x2 - x1, y2 - y1)

        # Convert distance to volume level
        vol = np.interp(length, [30, 200], [minVol, maxVol])
        volBar = np.interp(length, [30, 200], [400, 150])
        volPer = np.interp(length, [30, 200], [0, 100])

        # Set volume
        volume.SetMasterVolumeLevel(vol, None)

        # Volume bar display
        cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_PLAIN, 2,
                    (0, 0, 255), 3)

    # FPS display
    cTime = time.time()
    fps = 1 / (cTime - pTime) if (cTime - pTime) else 0
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (10, 30),
                cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)

    cv2.imshow("Volume Control", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
