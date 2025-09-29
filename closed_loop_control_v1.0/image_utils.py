import numpy as np
import cv2
from PIL import Image

tennis_ball = [64, 186, 156]

def get_limits(color):
    c = np.uint8([[color]])  # BGR values
    hsvC = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)

    hue = hsvC[0][0][0]  # Get the hue value

    # Handle red hue wrap-around
    if hue >= 165:  # Upper limit for divided red hue
        lowerLimit = np.array([hue - 10, 100, 100], dtype=np.uint8)
        upperLimit = np.array([180, 255, 255], dtype=np.uint8)
    elif hue <= 15:  # Lower limit for divided red hue
        lowerLimit = np.array([0, 100, 100], dtype=np.uint8)
        upperLimit = np.array([hue + 10, 255, 255], dtype=np.uint8)
    else:
        lowerLimit = np.array([hue - 10, 100, 100], dtype=np.uint8)
        upperLimit = np.array([hue + 10, 255, 255], dtype=np.uint8)

    return lowerLimit, upperLimit


def addText(x_center_offset, y_center_offset, height, frame):
    line1 = "Heliospace Stewart Platform"

    if x_center_offset is None:
        line2 = f"X: N/A, Y: N/A"
    else:
        line2 = f"Target X: {x_center_offset:.0f}, Target Y: {y_center_offset:.0f}"

    text_position_line1 = (10, height - 30)  # Adjusted to make space for two lines
    text_position_line2 = (10, height - 10)  # 10 pixels from the left border and 10 pixels from the bottom

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.4
    font_color = (0, 255, 0)
    line_type = 1
    cv2.putText(frame, line1, text_position_line1, font, font_scale, font_color, line_type)
    cv2.putText(frame, line2, text_position_line2, font, font_scale, font_color, line_type)

    return frame

def get_target_position(cap, center_box_size):


    returnValue = False
    x_center_offset = None
    y_center_offset = None

    ret, frame = cap.read()

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

    frame = cv2.rectangle(frame, (int(center_x+(center_box_size/2)), int(center_y+(center_box_size/2))), (int(center_x-(center_box_size/2)), int(center_y-(center_box_size/2))), (139, 139, 0), 1)
    frame = cv2.line(frame, (int(center_x), int(center_y - center_box_size)), (int(center_x), int(center_y + center_box_size)), (139, 139, 0), 1)
    frame = cv2.line(frame, (int(center_x - center_box_size), int(center_y)), (int(center_x + center_box_size), int(center_y)), (139, 139, 0), 1)

    if bbox is not None:
        x1, y1, x2, y2 = bbox
        target_center_x = int(x1 + (x2-x1)/2)
        target_center_y = int(y1 + (y2-y1)/2)
        if ((target_center_x < (center_x+(center_box_size/2))) and (target_center_x > -(center_x+(center_box_size/2)))) and (target_center_y < (center_y+(center_box_size/2))) and (target_center_y > -(center_y+(center_box_size/2))):
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        else:
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        target_x = x1 + ((x2-x1)/2)
        target_y = y1 + ((y2-y1)/2)
        x_center_offset = target_x - center_x
        y_center_offset = center_y - target_y

    frame = addText(x_center_offset, y_center_offset, height, frame)







    cv2.imshow('Stewart Platform', frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        returnValue = True

    return x_center_offset, y_center_offset, returnValue