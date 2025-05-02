import cv2
import mediapipe as mp
import numpy as np
import time
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# -------------------- Setup Volume Control --------------------
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol, maxVol = volRange[0], volRange[1]

# -------------------- Setup Mediapipe --------------------
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
pTime = 0

# Tip landmark IDs
tipIds = [4, 8, 12, 16, 20]

# Gesture state memory
lastGesture = None
gestureCooldown = 1.0  # seconds
lastGestureTime = 0

# Detect fingers up
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
        fingers = fingersUp(lmList)
        totalFingers = fingers.count(1)

        currentTime = time.time()

        # Play/Pause (palm open/closed)
        if currentTime - lastGestureTime > gestureCooldown:
            if totalFingers == 5:
                print("▶️ Play")
                lastGestureTime = currentTime
                lastGesture = "play"
                cv2.putText(img, "PLAY", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)
            elif totalFingers == 0:
                print("⏸️ Pause")
                lastGestureTime = currentTime
                lastGesture = "pause"
                cv2.putText(img, "PAUSE", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)

        # Volume control (thumb + index only)
        if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            x1, y1 = lmList[4][1], lmList[4][2]   # Thumb tip
            x2, y2 = lmList[8][1], lmList[8][2]   # Index tip
            cx, cy = (x1 + x2)//2, (y1 + y2)//2

            length = math.hypot(x2 - x1, y2 - y1)
            vol = np.interp(length, [30, 200], [minVol, maxVol])
            volume.SetMasterVolumeLevel(vol, None)

            # Draw volume line
            cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'Volume: {int(np.interp(length, [30, 200], [0, 100]))}%', 
                        (40, 450), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

    # FPS display
    cTime = time.time()
    fps = 1 / (cTime - pTime) if (cTime - pTime) else 0
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (10, 30),
                cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)

    cv2.imshow("Gesture Volume + Play/Pause", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
