import cv2
import subprocess
import time
import numpy as np
import sys
from PIL import ImageFont, ImageDraw, Image

WEBCAM_INDEX = 0 # v4l2-ctl --list-devices
PRINTER = "konsens_printer"
PRINTING_ACTIVE = False
COOLDOWN = 25
COUNTDOWN_LEN = 3
PRINTING_PAPER_SIZE = "a5"
PRINT_COMMAND_KEY = 32 # 32 = space

CONTRAST_VAL = 1.2
BRIGHTNESS_VAL = 60
PRINTER_BRIGHTNESS = 150

OVERLAY_FILE = "Konsens.jpg"
BORDER_FILE = "KonsensBorder.jpg"
OUTPUT_FILE = "pics/test.jpg"
PRINTING_FILE = "Printing.jpg"
FONT_FILE = "Modak-Regular.ttf"

overlay_img = cv2.imread(OVERLAY_FILE)
border_img = cv2.imread(BORDER_FILE)
printing_message = cv2.imread(PRINTING_FILE)

font = cv2.FONT_HERSHEY_DUPLEX 
position = (500, 20)
color = (195, 22, 161)
fontScale = 32
org = (500, 510) 
thickness = 30

#DEFINITIONS:

def sleep_of_seconds(seconds):
    start = time.time()
    while(True):
        k = cv2.waitKey(10)
        if (k%256 == 27):
            sys.exit(0)
        now = time.time()
        if (now - start >= seconds):
            break

def add_text(img, text):
    cv2_im_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(cv2_im_rgb)
    draw = ImageDraw.Draw(pil_im)  
    font = ImageFont.truetype(FONT_FILE, 500)  
    draw.text(position, text, font=font, fill=color, font_size=fontScale)
    cv2_im_processed = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
    return cv2_im_processed

def save_image(out):
    cv2.imwrite(OUTPUT_FILE, out)
    print("[SAVED PICTURE...]")

def vconcat_resize_min(im_list, interpolation=cv2.INTER_CUBIC):
    w_min = min(im.shape[1] for im in im_list)
    im_list_resize = [cv2.resize(im, (w_min, int(im.shape[0] * w_min / im.shape[1])), interpolation=interpolation)
                      for im in im_list]
    return cv2.vconcat(im_list_resize)

def setBorderImage(img1):
    assert img1 is not None, "file could not be read, check with os.path.exists()"
    assert border_img is not None, "file could not be read, check with os.path.exists()"
    img1 = cv2.convertScaleAbs(img1, alpha=CONTRAST_VAL, beta=BRIGHTNESS_VAL)
    white_border = 255 * np.ones((60,2480,3), np.uint8)
    flippedVertical = cv2.flip(border_img, 1)
    borderFlipped = cv2.flip(flippedVertical, 0)
    final_img = vconcat_resize_min([white_border, border_img, img1, borderFlipped]) 
    final_img = cv2.cvtColor(final_img, cv2.COLOR_BGR2GRAY)
    return final_img

def read_frame():
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
    return frame

# MAIN:

print("[STARTING...] (may take a bit)")
cam = cv2.VideoCapture(WEBCAM_INDEX)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("[WEBCAM SETUP COMPLETE... ]")
cv2.namedWindow("prev", cv2.WND_PROP_FULLSCREEN)

printing = False
fullscreen = False
while True:
    frame = read_frame()

    if printing:
        for countdown in range(COUNTDOWN_LEN):
            for i in range(10):
                frame = read_frame()
                text_frame = add_text(frame, "{}".format(COUNTDOWN_LEN - countdown))
                cv2.imshow("prev", text_frame)
                sleep_of_seconds(0.1)
        frame = read_frame()
        print("[COMPOSITING PICTURE...]")
        save_image(setBorderImage(frame))
        if (PRINTING_ACTIVE):
            subprocess.run([
                "lp", "-o", "fit-to-page", 
                "-o", "media={}".format(PRINTING_PAPER_SIZE), 
                "-o", "brightness={}".format(PRINTER_BRIGHTNESS), 
                "-d", PRINTER, OUTPUT_FILE])
            print("[PRINT-JOB SENT...]")
        printing = True
        cv2.imshow("prev", printing_message)
        printing = False
        sleep_of_seconds(COOLDOWN)

    cv2.imshow("prev", frame)
    k = cv2.waitKey(1)
    if k%256 == 27: # ESC
        print("[EXIT PROGRAMM...]")
        break
    elif k%256 == PRINT_COMMAND_KEY and not printing: # f18
        printing = True
    elif k%256 == 102: # f
        if not fullscreen:
            print("[resize FULLSCREEN]")
            cv2.setWindowProperty("prev", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            fullscreen = True
        else:
            print("[resize NORMAL]")
            cv2.destroyAllWindows()
            cv2.namedWindow("prev", cv2.WND_PROP_FULLSCREEN)
            fullscreen = False

cam.release()
cv2.destroyAllWindows()



# OLD/UNUSED

def overlayImage(original_image, overlay_image):
    assert original_image is not None, "file could not be read, check with os.path.exists()"
    assert overlay_image is not None, "file could not be read, check with os.path.exists()"
    rows,cols,channels = overlay_image.shape
    roi = original_image[0:rows, 0:cols]
    # Now create a mask of logo and create its inverse mask also
    overlay_imagegray = cv2.cvtColor(overlay_image,cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(overlay_imagegray, 10, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)
    # Now black-out the area of logo in ROI
    original_image_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)
    # Take only region of logo from logo image.
    overlay_image_fg = cv2.bitwise_and(overlay_image,overlay_image,mask = mask)
    # Put logo in ROI and modify the main image
    dst = cv2.add(original_image_bg,overlay_image_fg)
    original_image[0:rows, 0:cols ] = dst
     
    cv2.imshow("prev", original_image)
    cropped = original_image[0:720, 100:1180]
    return cropped
