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
base_options = python.BaseOptions(model_asset_path = "hand_landmarker.task", delegate = python.BaseOptions.Delegate.CPU)

# 2. configure settings
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=2,
)

last_pinch_index_thumb = 0

def pinch_dist_calc(index_x, index_y, thumb_x, thumb_y, move_pos_x_click, move_pos_y_click):

    """
    We added global because we made the last_pinch in global but when we use last_pinch inside the function then it thinks that it is new variable so we need to tell that take the last_pinch from global
    """
    global last_pinch_index_thumb

    threshold = 40
    delay = 1   # seconds between clicks

    dx = thumb_x - index_x
    dy = thumb_y - index_y
    distance = math.sqrt(dx*dx + dy*dy)

    if distance < threshold:
        cv2.circle(frame, (thumb_x, thumb_y), 10, (0,255,0), -1)

        current_time = time.time()

        if current_time - last_pinch_index_thumb > delay:
            pyautogui.click(move_pos_x_click, move_pos_y_click)
            last_pinch_index_thumb = current_time

alpha = 0.2   # smoothing factor

# NOTE: hereI I am using same last pinch.
# This is for double click
last_pinch_thumb_middle = 0
def thumb_middle(middle_x, middle_y, thumb_x, thumb_y, move_pos_x_click, move_pos_y_click):
    """
    Here we are calculating the distance between thumb and middle finger so that we can doubleclick
    """
    global last_pinch_thumb_middle
    # calculating the distance....
    dx = middle_x-thumb_x
    dy = middle_y-thumb_y

    delay = 1

    # threshold is the minimum length/distance that will be measured.
    threshold = 40
    distance = math.sqrt(dx*dx + dy*dy)

    if distance<threshold:
        # doubleclick at the position of the index finger top.
        cv2.circle(frame, (middle_x, middle_y), 10, (0,255,0), -1)
        current_time = time.time()
        if current_time-last_pinch_thumb_middle > delay:
            pyautogui.doubleClick(x=move_pos_x_click, y=move_pos_y_click)
            last_pinch_thumb_middle = current_time

# This is for the right click
last_pinch_thumb_ring = 0
def thumb_ring(ring_x, ring_y, thumb_x, thumb_y, move_pos_x_click, move_pos_y_click):
    """
    Here we are calculating the distance between thumb and middle finger so that we can doubleclick
    """
    global last_pinch_thumb_ring
    # calculating the distance....
    dx = ring_x-thumb_x
    dy = ring_y-thumb_y

    delay = 1

    # threshold is the minimum length/distance that will be measured.
    threshold = 40
    distance = math.sqrt(dx*dx + dy*dy)

    if distance<threshold:
        # doubleclick at the position of the index finger top.
        cv2.circle(frame, (ring_x, ring_y), 10, (0,255,0), -1)
        current_time = time.time()
        if current_time-last_pinch_thumb_ring > delay:
            pyautogui.rightClick(x=move_pos_x_click, y=move_pos_y_click)
            last_pinch_thumb_ring = current_time

# This function is for the calculating the distance between previous position for smoothness.
prev_x = 0
prev_y = 0
def cursor_smoothness(current_x, current_y):

    global prev_y, prev_x

    threshold = 0.2
    dx = current_x-prev_x
    dy = current_y-prev_y

    distance = math.sqrt(dx*dx + dy*dy)
    if distance>threshold:
        pyautogui.moveTo(current_x, current_y)
        prev_x = current_x
        prev_y = current_y

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
        # we are indexing, the list, from 0
        for i, hand in enumerate(result.hand_landmarks):
            label = result.handedness[i][0].category_name
            index_finger = hand[8]
            middle_finger = hand[12]
            little_finger = hand[20]
            ring_finger = hand[16]
            thumb = hand[4]
            if label == 'Right':
                # print(index_finger)
                ix = int(index_finger.x * w)
                iy = int(index_finger.y * h)

                # This is tip of middle finger
                mx = int(middle_finger.x * w)
                my = int(middle_finger.y * h)
                # print(ix, iy)

                # this is tip of ring finger
                rx = int(ring_finger.x*w)
                ry = int(ring_finger.y*w)

                """
                (150, 70)
                (490, 410)
                """

                if 150<ix<490 and 70<iy<410:
                    cv2.circle(frame, (ix, iy), 5, (0, 0, 255), -1)

                    """
                    I found the ratio of the screen and rectangle region, 
                    Monitor: w = 1366, h = 768
                    Rectangle: w = 300, h = 300
                    
                    I found the ratio of the width and height, i.e, w = 4.553333333, h = 2.56
                    
                    Now I will assume that the cursor will move w and h times.
                    """
                    
                    # To move x and y position.
                    """
                    Here I am subtracting the 1366 that is my screen x axis, because the camera is showing the mirror image, so i am making it opposite.
                    """
                    move_pos_x = 1366-(ix-170)*5
                    move_pos_y = (iy-90)*3

                    # print(move_pos_x, move_pos_y)

                    # calculating that the current position
                    cursor_smoothness(move_pos_x, move_pos_y)

                    # pyautogui.moveTo(move_pos_x, move_pos_y)
                    # pyautogui.moveTo(ix, iy)

                    # Thumb coordinate
                    tx = int(thumb.x * w)
                    ty = int(thumb.y * h)

                    pinch_dist_calc(ix, iy, tx, ty, move_pos_x, move_pos_y)

                    # calling the double click functions
                    thumb_middle(mx, my, tx, ty, move_pos_x, move_pos_y)

                    # calling this for right click functionality
                    thumb_ring(rx, ry, tx, ty, move_pos_x, move_pos_y)

        # creating a square region for movement.

        # print(pt1_square, pt2_square)
        # (170, 90) (470, 390)
        cv2.rectangle(frame, pt1_square, pt2_square, (255, 0, 0), 2)

        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

camera.release()
cv2.destroyAllWindows()