import cv2
# from sh import lp
import subprocess

def printPicture(img_counter):
    # lp("pic_{}.jpeg".format(img_counter), "-y", magnify=2)
    subprocess.run(["lp", "pic_{}.jpeg".format(img_counter), "-o", "scaling=75"])

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

cv2.namedWindow("photobooth")

img_counter = 0

while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("photobooth", frame)

    k = cv2.waitKey(1)
    if k%256 == 27: # ESC
        print("Escape hit, closing...")
        break
    elif k%256 == 32: # SPACE
        img_name = "pic_{}.jpeg".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        printPicture(img_counter)
        img_counter += 1

cam.release()
cv2.destroyAllWindows()

