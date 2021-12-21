import numpy as np
import cv2

# Create a VideoCapture object and read from input file
# Video source - can be camera index number (0, 1, 2,...) given by 'ls /dev/video*
# or can be a video file, e.g. cv2.VideoCapture('~/Video.avi')
cap = cv2.VideoCapture(0)  # cap is a VideoCapture object from cv2 lib

# Check if camera opened successfully
if not cap.isOpened():
    print("Error opening video stream or file")

while cap.isOpened():

    # Capture frame-by-frame
    # returns tuple: ret (bool)- is there a captured frame?, frame - image data
    ret, frame = cap.read()

    if ret:

        # Our operations on the frame come here
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Display the resulting frame in a window
        cv2.imshow('Live Webcam', frame)  # 'Live Webcam' - window name, frame - displayed image

        if cv2.waitKey(1) & 0xFF == ord(
                'q'):  # argument in waitKey in ms (between frames), ord() - returns int as Unicode
            break

    else:
        break

# When everything done, release the capture
cap.release()  # close IO device, i.e. camera
cv2.destroyAllWindows()  # close windows (out of loop)
