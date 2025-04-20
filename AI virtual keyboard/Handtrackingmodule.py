import time
import cv2
import numpy as np
from pynput.keyboard import Controller

class Key:
    def __init__(self, x, y, w, h, text):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text

    def drawKey(self, img, text_color=(255, 255, 255), bg_color=(0, 0, 0), alpha=0.5,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8, thickness=2):
        # Draw the box
        bg_rec = img[self.y: self.y + self.h, self.x: self.x + self.w]
        white_rect = np.ones(bg_rec.shape, dtype=np.uint8) * 25
        white_rect[:] = bg_color
        res = cv2.addWeighted(bg_rec, alpha, white_rect, 1 - alpha, 1.0)
        img[self.y: self.y + self.h, self.x: self.x + self.w] = res

        # Put the letter
        text_size = cv2.getTextSize(self.text, fontFace, fontScale, thickness)
        text_pos = (int(self.x + self.w / 2 - text_size[0][0] / 2),
                    int(self.y + self.h / 2 + text_size[0][1] / 2))
        cv2.putText(img, self.text, text_pos, fontFace, fontScale, text_color, thickness)

    def isOver(self, x, y):
        return (self.x < x < self.x + self.w) and (self.y < y < self.y + self.h)


# Utility functions
def getMousePos(event, x, y, flags, param):
    global clickedX, clickedY, mouseX, mouseY
    if event == cv2.EVENT_LBUTTONUP:
        clickedX, clickedY = x, y
    if event == cv2.EVENT_MOUSEMOVE:
        mouseX, mouseY = x, y


def calculateIntDistance(pt1, pt2):
    return int(((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)**0.5)


# Main application
def main():
    global clickedX, clickedY, mouseX, mouseY

    clickedX, clickedY = 0, 0
    mouseX, mouseY = 0, 0
    keyboard = Controller()
    w, h = 80, 60
    startX, startY = 40, 200

    # Define keys
    keys = []
    letters = list("QWERTYUIOPASDFGHJKLZXCVBNM")
    for i, l in enumerate(letters):
        if i < 10:
            keys.append(Key(startX + i * w + i * 5, startY, w, h, l))
        elif i < 19:
            keys.append(Key(startX + (i - 10) * w + i * 5, startY + h + 5, w, h, l))
        else:
            keys.append(Key(startX + (i - 19) * w + i * 5, startY + 2 * h + 10, w, h, l))

    keys.append(Key(startX + 25, startY + 3 * h + 15, 5 * w, h, "Space"))
    keys.append(Key(startX + 8 * w + 50, startY + 2 * h + 10, w, h, "clr"))
    keys.append(Key(startX + 5 * w + 30, startY + 3 * h + 15, 5 * w, h, "<--"))

    # Initialize OpenCV window
    cv2.namedWindow('video')
    cv2.setMouseCallback('video', getMousePos)

    # Camera setup
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    frameHeight, frameWidth, _ = frame.shape

    ptime = 0
    show = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (int(frameWidth * 1.5), int(frameHeight * 1.5)))

        # Draw keys
        for key in keys:
            alpha = 0.5
            if key.isOver(mouseX, mouseY):
                alpha = 0.1
            key.drawKey(frame, alpha=alpha)

        ctime = time.time()
        fps = int(1 / (ctime - ptime))
        cv2.putText(frame, f"{fps} FPS", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        ptime = ctime

        cv2.imshow('video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


