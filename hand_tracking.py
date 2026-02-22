import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
import math
import pyautogui

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

camera = cv2.VideoCapture(0)

cam_w = 640
cam_h = 480

camera.set(3, 640)   # width
camera.set(4, 480)   # height


# NOTE:Here I am going to initialize the model
base_options = python.BaseOptions("hand_landmarker.task")

# 2. configure settings
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=2
)

last_pinch = 0

def pinch_dist_calc(ix, iy, tx, ty, move_pos_x, move_pos_y):
    global last_pinch

    threshold = 40
    delay = 1   # seconds between clicks

    dx = tx - ix
    dy = ty - iy
    distance = math.sqrt(dx*dx + dy*dy)

    if distance < threshold:
        cv2.circle(frame, (tx, ty), 10, (0,255,0), -1)

        current_time = time.time()

        if current_time - last_pinch > delay:
            pyautogui.click(1366-move_pos_x, move_pos_y)
            last_pinch = current_time
prev_x = 0
prev_y = 0
alpha = 0.2   # smoothing factor


# 3. create the model (INITIALIZATION)
detector = vision.HandLandmarker.create_from_options(options)
pt1_square = ((cam_w // 2)-150, (cam_h // 2)-150)
pt2_square = ((cam_w // 2)+150, (cam_h // 2)+150)
while True:
    is_captured, frame = camera.read()
    # here frame will be given in to bgr color format.

    if is_captured:
        # for hand detection we need to create an object class hand.
        # converting the images into rgb as hands only take rgb color image.
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # converting into mediapipe images.
        mp_image = mp.Image(image_format= mp.ImageFormat.SRGB,data=frame_rgb)

        """
        we have to provide the millisecond timestamp to the detector because it uses it to track the motion of the hand.
        
        1 second = 1000 milliseconds

        So to convert seconds to milliseconds:
        
        seconds × 1000 = milliseconds
        
        so we are using:
        timestamp_ms = int(time.time() * 1000)
        """

        timestamp_ms = int(time.time() * 1000)
        result = detector.detect_for_video(image=mp_image, timestamp_ms=timestamp_ms)

        # print(result.hand_landmarks)

        # Taking the frame shape
        h, w, channel = frame.shape
        """
        index finger- movement
        index with middle- double click
        index with little- single click
        """

        for i, hand in enumerate(result.hand_landmarks):
            label = result.handedness[i][0].category_name
            index_finger = hand[8]
            middle_finger = hand[12]
            little_finger = hand[20]
            thumb = hand[4]
            if label == 'Right':
                # print(index_finger)
                ix = int(index_finger.x * w)
                iy = int(index_finger.y * h)
                # print(ix, iy)

                if 170<ix<470 and 90<iy<400:

                    cv2.circle(frame, (ix, iy), 5, (0, 0, 255), -1)

                    # mx = int(middle_finger.x * w)
                    # my = int(middle_finger.y * h)
                    #
                    #
                    # cv2.circle(frame, (mx, my), 5, (0, 255, 0), -1)
                    #
                    # lx = int(little_finger.x * w)
                    # ly = int(little_finger.y * h)
                    #
                    #
                    # cv2.circle(frame, (lx, ly), 5, (0, 255, 0), -1)

                    # dist = distance_calc(px, py)
                    """
                    I found the ratio of the screen and rectangle region, 
                    Monitor: w = 1366, h = 768
                    Rectangle: w = 300, h = 300
                    
                    I found the ratio of the width and height, i.e, w = 4.553333333, h = 2.56
                    
                    Now I will assume that the cursor will move w and h times.
                    """

                    # To move x and y position.
                    move_pos_x = (ix-170)*5
                    move_pos_y = (iy-90)*3

                    # print(move_pos_x, move_pos_y)

                    pyautogui.moveTo(1366-move_pos_x, move_pos_y)
                    # pyautogui.moveTo(ix, iy)

                    # Thumb coordinate
                    tx = int(thumb.x * w)
                    ty = int(thumb.y * h)

                    pinch_dist_calc(ix, iy, tx, ty, move_pos_x, move_pos_y)
        # creating a square region for movement.

        # print(pt1_square, pt2_square)
        # (170, 90) (470, 390)
        cv2.rectangle(frame, pt1_square, pt2_square, (255, 0, 0), 2)

        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

camera.release()
cv2.destroyAllWindows()