import cv2
import subprocess
import time
import numpy as np

print("Enter webcam you would like to use (0 or 1): ")
WEBCAM_INDEX = 0 # v4l2-ctl --list-devices
PRINTER = "konsens_printer"
PRINTING_ACTIVE = True
COOLDOWN = 25000
SIZE = "a4"

CONTRAST_VAL = 1.2
BRIGHTNESS_VAL = 60
BRIGHTNESS = 150

OVERLAY_FILE = "Konsens.jpg"
BORDER_FILE = "KonsensBorder.jpg"
TEST_JPG = "pics/test.jpg"
PRINTING_FILE = "Printing.jpg"

img2 = cv2.imread(OVERLAY_FILE)
borderImg = cv2.imread(BORDER_FILE)
printing_message = cv2.imread(PRINTING_FILE)

font = cv2.FONT_HERSHEY_DUPLEX 
org = (500, 510) 
fontScale = 12
color = (195, 22, 161)
thickness = 30

def sleep_seconds(seconds):
    start = time.time()
    while(True):
        k = cv2.waitKey(10)
        if (k%256 == 27):
            import sys
            sys.exit(0)
        now = time.time()
        if (now - start >= seconds):
            break

def overlayImage(img1):
    print("[SAVING PICTURE...]")
    assert img1 is not None, "file could not be read, check with os.path.exists()"
    assert img2 is not None, "file could not be read, check with os.path.exists()"
    rows,cols,channels = img2.shape
    roi = img1[0:rows, 0:cols]
    # Now create a mask of logo and create its inverse mask also
    img2gray = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)
    # Now black-out the area of logo in ROI
    img1_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)
    # Take only region of logo from logo image.
    img2_fg = cv2.bitwise_and(img2,img2,mask = mask)
    # Put logo in ROI and modify the main image
    dst = cv2.add(img1_bg,img2_fg)
    img1[0:rows, 0:cols ] = dst
     
    cv2.imshow("prev", img1)
    cropped = img1[0:720, 100:1180]
    cv2.imwrite(TEST_JPG, cropped)
    print("[SAVED PICTURE...]")

def vconcat_resize_min(im_list, interpolation=cv2.INTER_CUBIC):
    w_min = min(im.shape[1] for im in im_list)
    im_list_resize = [cv2.resize(im, (w_min, int(im.shape[0] * w_min / im.shape[1])), interpolation=interpolation)
                      for im in im_list]
    return cv2.vconcat(im_list_resize)

def setBorderImage(img1):
    print("[SAVING PICTURE...]")
    assert img1 is not None, "file could not be read, check with os.path.exists()"
    assert borderImg is not None, "file could not be read, check with os.path.exists()"
    img1 = cv2.convertScaleAbs(img1, alpha=CONTRAST_VAL, beta=BRIGHTNESS_VAL)
    white_border = 255 * np.ones((60,2480,3), np.uint8)
    final_img = vconcat_resize_min([white_border, borderImg, img1, borderImg]) 
    final_img = cv2.cvtColor(final_img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(TEST_JPG, final_img)
    print("[SAVED PICTURE...]")

def printImage():
    print("[PRINTING...]")
    subprocess.run("lp " + TEST_JPG)

print("[STARTING...] (may take a bit)")
cam = cv2.VideoCapture(WEBCAM_INDEX)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("[WEBCAM SETUP COMPLETE... ]")
cv2.namedWindow("prev", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("prev", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
preparing = False
printing = False
countdown = 3
while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break

    if preparing:
        text_frame = cv2.putText(frame, "{}".format(countdown), org, font, fontScale, color, thickness, cv2.LINE_AA) 
        cv2.imshow("prev", text_frame)
        sleep_seconds(1)
        countdown -= 1
        if (countdown <= 0):
            preparing = False
            countdown = 3
            ret, frame = cam.read()
            if not ret:
                print("failed to grab frame")
                break
            setBorderImage(frame)
            if (PRINTING_ACTIVE):
                subprocess.run(["lp", "-o", "fit-to-page", "-o", "media={}".format(SIZE), "-o", "brightness={}".format(BRIGHTNESS), "-d", PRINTER, TEST_JPG])
            printing = True

    cv2.imshow("prev", frame)
    k = cv2.waitKey(1)
    if k%256 == 27: # ESC
        print("[EXIT PROGRAMM...]")
        break
    elif k%256 == 32 and not preparing and not printing: # f18
        preparing = True
    elif printing:
        print("[PRINTED...]")
        cv2.imshow("prev", printing_message)
        printing = False
        sleep_seconds(20)
    else:
        cv2.imshow("prev", frame)


cam.release()
cv2.destroyAllWindows()


