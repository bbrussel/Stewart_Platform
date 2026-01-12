import cv2
from PIL import Image
import datetime

from util import get_limits


tennis_ball = [64, 186, 156]  # BGR colorspace

cap = cv2.VideoCapture(0)

frame_counter = 0
processed_frames = 0
initial_frame_skip = 80

while True:
    ret, frame = cap.read()

    frame_copy = frame.copy()

    processed_frames += 1

    if processed_frames >= initial_frame_skip:

        blurred = cv2.GaussianBlur(frame, (11, 11), 0)

        hsvImage = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)


        lowerLimit, upperLimit = get_limits(color=tennis_ball)
        mask = cv2.inRange(hsvImage, lowerLimit, upperLimit)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        
        mask_ = Image.fromarray(mask)
        bbox = mask_.getbbox()

        height, width = frame.shape[:2]

        center_x = width/2
        center_y = height/2
        if bbox is not None:
            x1, y1, x2, y2 = bbox
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

            target_x = x1 + ((x2-x1)/2)
            target_y = y1 + ((y2-y1)/2)
            x_center_offset = target_x - center_x
            y_center_offset = center_y - target_y

            print("")
            print("x: " + str(target_x))
            print("y: " + str(target_y))
            print("x offset from center: " + str(x_center_offset))
            print("y offset from center: " + str(y_center_offset))



    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()

cv2.destroyAllWindows()