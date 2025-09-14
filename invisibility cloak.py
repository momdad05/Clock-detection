import cv2
import numpy as np
import sys
import platform

CAM_INDEX = 0            
MIRROR = True            
WIN_NAME = "Invisibility Cloak"
SHOW_HSV = False         
CURRENT_COLOR = "red"    

BACKEND = cv2.CAP_DSHOW if platform.system() == "Windows" else 0

def nothing(_):
    pass

def init_hsv_window():
    cv2.namedWindow("HSV Controls", cv2.WINDOW_AUTOSIZE)
    cv2.createTrackbar("H1 min", "HSV Controls", 0, 180, nothing)
    cv2.createTrackbar("S1 min", "HSV Controls", 120, 255, nothing)
    cv2.createTrackbar("V1 min", "HSV Controls", 70, 255, nothing)
    cv2.createTrackbar("H1 max", "HSV Controls", 10, 180, nothing)
    cv2.createTrackbar("S1 max", "HSV Controls", 255, 255, nothing)
    cv2.createTrackbar("V1 max", "HSV Controls", 255, 255, nothing)
    cv2.createTrackbar("H2 min", "HSV Controls", 170, 180, nothing)
    cv2.createTrackbar("S2 min", "HSV Controls", 120, 255, nothing)
    cv2.createTrackbar("V2 min", "HSV Controls", 70, 255, nothing)
    cv2.createTrackbar("H2 max", "HSV Controls", 180, 180, nothing)
    cv2.createTrackbar("S2 max", "HSV Controls", 255, 255, nothing)
    cv2.createTrackbar("V2 max", "HSV Controls", 255, 255, nothing)
    cv2.createTrackbar("Kernel", "HSV Controls", 3, 15, nothing)   # odd values better: 3,5,7...
    cv2.createTrackbar("Dilate", "HSV Controls", 1, 10, nothing)

def set_preset(color):
    
    presets = {
        "red":  {
            "r1": (0, 120, 70, 10, 255, 255),
            "r2": (170, 120, 70, 180, 255, 255),
            "kernel": 3, "dilate": 1
        },
        "blue": {
            "r1": (94, 80, 2, 126, 255, 255),
            "r2": (0, 0, 0, 0, 0, 0),     # unused second range
            "kernel": 3, "dilate": 1
        },
        "green":{
            "r1": (36, 50, 70, 89, 255, 255),
            "r2": (0, 0, 0, 0, 0, 0),
            "kernel": 3, "dilate": 1
        }
    }
    p = presets[color]
    H1min, S1min, V1min, H1max, S1max, V1max = p["r1"]
    H2min, S2min, V2min, H2max, S2max, V2max = p["r2"]
    cv2.setTrackbarPos("H1 min", "HSV Controls", H1min)
    cv2.setTrackbarPos("S1 min", "HSV Controls", S1min)
    cv2.setTrackbarPos("V1 min", "HSV Controls", V1min)
    cv2.setTrackbarPos("H1 max", "HSV Controls", H1max)
    cv2.setTrackbarPos("S1 max", "HSV Controls", S1max)
    cv2.setTrackbarPos("V1 max", "HSV Controls", V1max)

    cv2.setTrackbarPos("H2 min", "HSV Controls", H2min)
    cv2.setTrackbarPos("S2 min", "HSV Controls", S2min)
    cv2.setTrackbarPos("V2 min", "HSV Controls", V2min)
    cv2.setTrackbarPos("H2 max", "HSV Controls", H2max)
    cv2.setTrackbarPos("S2 max", "HSV Controls", S2max)
    cv2.setTrackbarPos("V2 max", "HSV Controls", V2max)

    cv2.setTrackbarPos("Kernel", "HSV Controls", p["kernel"])
    cv2.setTrackbarPos("Dilate", "HSV Controls", p["dilate"])

def read_hsv_ranges():
    H1min = cv2.getTrackbarPos("H1 min", "HSV Controls")
    S1min = cv2.getTrackbarPos("S1 min", "HSV Controls")
    V1min = cv2.getTrackbarPos("V1 min", "HSV Controls")
    H1max = cv2.getTrackbarPos("H1 max", "HSV Controls")
    S1max = cv2.getTrackbarPos("S1 max", "HSV Controls")
    V1max = cv2.getTrackbarPos("V1 max", "HSV Controls")

    H2min = cv2.getTrackbarPos("H2 min", "HSV Controls")
    S2min = cv2.getTrackbarPos("S2 min", "HSV Controls")
    V2min = cv2.getTrackbarPos("V2 min", "HSV Controls")
    H2max = cv2.getTrackbarPos("H2 max", "HSV Controls")
    S2max = cv2.getTrackbarPos("S2 max", "HSV Controls")
    V2max = cv2.getTrackbarPos("V2 max", "HSV Controls")

    kernel = cv2.getTrackbarPos("Kernel", "HSV Controls")
    if kernel % 2 == 0:  # keep kernel odd
        kernel += 1
    dilate_iter = max(0, cv2.getTrackbarPos("Dilate", "HSV Controls"))

    lower1 = np.array([H1min, S1min, V1min])
    upper1 = np.array([H1max, S1max, V1max])
    lower2 = np.array([H2min, S2min, V2min])
    upper2 = np.array([H2max, S2max, V2max])

    return (lower1, upper1, lower2, upper2, kernel, dilate_iter)

cap = cv2.VideoCapture(CAM_INDEX, BACKEND)
if not cap.isOpened():
    # Try without backend hint
    cap = cv2.VideoCapture(CAM_INDEX)
if not cap.isOpened():
    print("Could not open webcam. Try changing CAM_INDEX (0/1/2) or close other apps using the camera.")
    sys.exit(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

init_hsv_window()
set_preset(CURRENT_COLOR)
if not SHOW_HSV:
    cv2.destroyWindow("HSV Controls")

background = None
font = cv2.FONT_HERSHEY_SIMPLEX

while True:
    ok, frame = cap.read()
    if not ok:
        print("Failed to read frame from camera.")
        break

    if MIRROR:
        frame = cv2.flip(frame, 1)

    display = frame.copy()

    cv2.putText(display, f"[b] capture background   [1] red  [2] blue  [3] green   [h] HSV sliders   [q] quit",
                (12, 28), font, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

    if background is None:
        cv2.putText(display, "Step 1: Clear the frame, then press [b] to capture background.",
                    (12, 58), font, 0.6, (0, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow(WIN_NAME, display)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('h'):
            SHOW_HSV = not SHOW_HSV
            if SHOW_HSV:
                init_hsv_window(); set_preset(CURRENT_COLOR)
            else:
                cv2.destroyWindow("HSV Controls")
        elif key in (ord('1'), ord('2'), ord('3')):
            CURRENT_COLOR = {'1':'red','2':'blue','3':'green'}[chr(key)]
            SHOW_HSV = True
            init_hsv_window(); set_preset(CURRENT_COLOR)
        elif key == ord('b'):
           
            for _ in range(20):
                ok, bg = cap.read()
                if not ok:
                    break
                if MIRROR:
                    bg = cv2.flip(bg, 1)
            background = bg.copy()
            cv2.putText(display, "Background captured",
                        (12, 88), font, 0.7, (0, 200, 0), 2, cv2.LINE_AA)
            cv2.imshow(WIN_NAME, display)
            cv2.waitKey(300)
        continue

    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    try:
        lower1, upper1, lower2, upper2, ksz, dil_iter = read_hsv_ranges()
    except cv2.error:
        
        init_hsv_window()
        set_preset(CURRENT_COLOR)
        lower1, upper1, lower2, upper2, ksz, dil_iter = read_hsv_ranges()
        if not SHOW_HSV:
            cv2.destroyWindow("HSV Controls")

    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)
    mask = cv2.bitwise_or(mask1, mask2)

   
    kernel = np.ones((ksz, ksz), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    if dil_iter > 0:
        mask = cv2.dilate(mask, kernel, iterations=dil_iter)

    mask_inv = cv2.bitwise_not(mask)

    cloak_area = cv2.bitwise_and(background, background, mask=mask)
    rest = cv2.bitwise_and(frame, frame, mask=mask_inv)
    output = cv2.add(cloak_area, rest)

    cv2.putText(output, f"Preset: {CURRENT_COLOR}   (tune with [h])",
                (12, 58), font, 0.6, (0, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow(WIN_NAME, output)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('h'):
        SHOW_HSV = not SHOW_HSV
        if SHOW_HSV:
            init_hsv_window(); set_preset(CURRENT_COLOR)
        else:
            cv2.destroyWindow("HSV Controls")
    elif key in (ord('1'), ord('2'), ord('3')):
        CURRENT_COLOR = {'1':'red','2':'blue','3':'green'}[chr(key)]
        SHOW_HSV = True
        init_hsv_window(); set_preset(CURRENT_COLOR)
    elif key == ord('b'):
       
        for _ in range(20):
            ok, bg = cap.read()
            if not ok:
                break
            if MIRROR:
                bg = cv2.flip(bg, 1)
        background = bg.copy()

cap.release()
cv2.destroyAllWindows()