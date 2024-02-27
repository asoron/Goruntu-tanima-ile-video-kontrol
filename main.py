import cv2 
import mediapipe as mp
import time
import numpy as np
import math
import keyboard as kb
from pynput.keyboard import Key, Controller

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
keyboard = Controller()


class handDedector():
    def __init__(self, mode=False, maxHands=2, modelComplexity=1, dedectionCon=.5, trackCon=.5):
        self.mode = mode
        self.maxHands = maxHands
        self.modelComplex = modelComplexity
        self.dedectionCon = dedectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            self.mode, self.maxHands, self.modelComplex, self.dedectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(
                        img, handLms, self.mpHands.HAND_CONNECTIONS)

        return img

    def findPosition(self, img, handNo=0, draw=True):

        lmList = []

        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]

            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (0, 0, 0), cv2.FILLED)

        return lmList


def main():

    pTime = 0
    cTime = 0

    handmovements = 0
    fingerStartPos = True
    tt = 0

    cap = cv2.VideoCapture(0)

    hd = handDedector()

    while True:
        success, img = cap.read()
        img = hd.findHands(img)
        lmList = hd.findPosition(img, draw=False)
        if kb.is_pressed('q'):
            fingerStartPos = True
            tt = 0
            handmovements += 1
            if handmovements > 2:
                handmovements = 0
            time.sleep(1)
            print(handmovements)
        if len(lmList) != 0:
            match handmovements:
                case 0:
                    pass
                case 1:

                    x1, y1 = lmList[8][1], lmList[8][2]
                    x2, y2 = lmList[12][1], lmList[12][2]
                    cx, cy = lmList[0][1], lmList[0][2]
                    coml = math.hypot(x2-x1, y2-y1)
                    l = math.hypot(x2-cx, y2-cy)
                    print(l)
                    print(coml)
                    if coml < 25:
                        if fingerStartPos:
                            fingerStartPos = False
                            tt = time.time()
                        if not l < 50:
                            print("asdfdsfasdfsdfad")
                            if tt + 1 < time.time():
                                x1, y1 = lmList[8][1], lmList[8][2]
                                if cx < x1:
                                    keyboard.press(Key.left)
                                    keyboard.release(Key.left)
                                elif cx > x1:
                                    keyboard.press(Key.right)
                                    keyboard.release(Key.right)
                                tt = time.time()
                        elif tt + 1 < time.time():
                            keyboard.press(Key.space)
                            keyboard.release(Key.space)
                            tt = time.time()
                        print(handmovements)

                case 2:
                    x1, y1 = lmList[8][1], lmList[8][2]
                    x2, y2 = lmList[12][1], lmList[12][2]
                    coml = math.hypot(x2-x1, y2-y1)
                    print(coml)
                    if coml < 25:
                        x1, y1 = lmList[4][1], lmList[4][2]
                        x2, y2 = lmList[8][1], lmList[8][2]
                        cx, cy = (x1 + x2) // 2, (y1+y2) // 2
                        l = math.hypot(x2-x1, y2-y1)
                        vol = np.interp(l, [20, 100], [-30, 0])
                        volume.SetMasterVolumeLevel(vol, None)
                    print(handmovements)

        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
