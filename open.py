import cv2
import mediapipe as mp
import time
import os

# Mediapipe setup
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

tipIds = [4, 8, 12, 16, 20]

cap = cv2.VideoCapture(0)

# Gesture cooldown timer
lastGestureTime = 0
gestureCooldown = 3  # seconds
spotifyOpened = False

# Helper to detect fingers
def fingersUp(lmList):
    fingers = []
    if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
        fingers.append(1)
    else:
        fingers.append(0)
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
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((id, cx, cy))

    if lmList:
        fingers = fingersUp(lmList)
        totalFingers = fingers.count(1)

        if totalFingers == 5:
            currentTime = time.time()
            if not spotifyOpened and (currentTime - lastGestureTime) > gestureCooldown:
                lastGestureTime = currentTime
                spotifyOpened = True

                # 🎵 Open Spotify (adjust the path if needed)
                try:
                    os.startfile("spotify")  # Works if Spotify is in system PATH
                    print("✅ Spotify launched!")
                except:
                    print("❌ Failed to open Spotify. Check your system PATH or use full path.")
                cv2.putText(img, "Spotify OPENED", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)

    # Show video
    cv2.imshow("Palm = Open Spotify", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
