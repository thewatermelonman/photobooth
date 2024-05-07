import cv2
import subprocess
from PIL import Image, ImageWin

OVERLAY_FILE = "Konsens.jpg"
TEST_JPG = "pics/test.jpg"

img_counter = 0
img2 = cv2.imread(OVERLAY_FILE)

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
    
    cv2.imshow("photo", img1)
    img_name = "pics/test.jpg".format(img_counter)
    cv2.imwrite(img_name, img1)
    print("[SAVED PICTURE...]")

def printImage():
    print("[PRINTING...]")

print("[STARTING...] (may take a bit)")
cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 2480)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1748)

print("[WEBCAM SETUP COMPLETE... ]")
cv2.namedWindow("livepreview")
cv2.namedWindow("photo")

while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("livepreview", frame)
    k = cv2.waitKey(1)
    if k%256 == 27: # ESC
        print("[EXIT PROGRAMM...]")
        break
    elif k%256 == 32: # SPACE
        print("[TAKING PICTURE...]")
        overlayImage(frame)

cam.release()
cv2.destroyAllWindows()


