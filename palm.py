import cv2
import mediapipe as mp
import numpy as np
import time
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Pycaw setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol, maxVol = volRange[0], volRange[1]

# Mediapipe setup
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
pTime = 0

# Finger tip landmark IDs
tipIds = [4, 8, 12, 16, 20]

# Helper function to detect fingers up
def fingersUp(lmList):
    fingers = []

    # Thumb
    if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other 4 fingers
    for id in range(1, 5):
        if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers

# Initialize volume
currentVol = volume.GetMasterVolumeLevel()

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
        fingerStatus = fingersUp(lmList)
        totalFingers = fingerStatus.count(1)

        if totalFingers == 5:
            # Open Palm: Increase volume
            currentVol += 1.5  # You can adjust the step size
            currentVol = min(currentVol, maxVol)
            volume.SetMasterVolumeLevel(currentVol, None)
            cv2.putText(img, "Palm Open - Volume UP", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        elif totalFingers == 0:
            # Fist: Decrease volume
            currentVol -= 1.5
            currentVol = max(currentVol, minVol)
            volume.SetMasterVolumeLevel(currentVol, None)
            cv2.putText(img, "Fist - Volume DOWN", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    # FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime) if (cTime - pTime) else 0
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (10, 30),
                cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)

    cv2.imshow("Palm Volume Control", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
