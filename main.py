# Importing the Libraries and Keep the directkeys.py File in your Work(Project) Folder to Import the Keys
# Created By: Aadil Tajani
from directkeys import W, A, S, D, PressKey, ReleaseKey
import cv2
import math
import time

# Start Video Capture
cap = cv2.VideoCapture(0)
print('Starting in...')
for i in range(3):
    print(3-i)
    time.sleep(1)

# Apply the program on every Frame
while True:

    # Getting Frame from Camera
    _, img = cap.read()
    img = cv2.flip(img, 1)

    # Getting Video Frame Dimensions
    h = int(img.shape[0])
    w = int(img.shape[1])

    # Initializing dimensions for the Acceleration and Braking Zones
    ah = h // 2 - 21
    bh = h // 2 + 21

    # Showing lines to separate Zones
    cv2.line(img, tuple([0, ah]), tuple([w, ah]), [0, 255, 100], 1)
    cv2.line(img, tuple([0, bh]), tuple([w, bh]), [0, 255, 100], 1)

    # Blurring Image To Smoothen Edges
    blur = cv2.GaussianBlur(img, (7, 7), 0)

    # Converting Image from BGR to Gray
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)

    # Thresholding Image to Get Mask for Hand (Only Blurring and Thresholding worked for me and Morphing didn't make
    # much of a difference so, for the sake of simplicity, I didn't include Morphing)
    _, thresh1 = cv2.threshold(gray, 140, 255, cv2.THRESH_TOZERO)

    # Getting Contours from Image
    contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Continue if Contours are Found
    try:
        # Get the Max Contour by Area i.e. Hand
        cnt = max(contours, key=lambda x: cv2.contourArea(x))

        # Approximating Polygonal Curve for Hull
        epsilon = 0.0005 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        # Getting Convex Hull for the Contour and getting Defects
        hull = cv2.convexHull(approx, returnPoints=False)
        defects = cv2.convexityDefects(approx, hull)

        # Getting the Starting Points of Defects in a list
        st = []
        for i in range(defects.shape[0]):
            s = defects[i, 0, 0]
            start = tuple(approx[s][0])
            st.append(start)

        # Sorting the list of Starting Points by Y coordinate to get starting points of fingers
        st.sort(key=lambda x: x[1])

        # Taking the first Highest Point by Default
        s1 = st[0]
        s2 = st[1]

        # Traversing the list and choosing the next highest point which is some distance away from the first point so
        # that it is from another finger
        for i in st:
            if abs(s1[0] - i[0]) > 30 and abs(s1[1] - i[1]) < 80:
                s2 = i
                break

        # Getting the Center Point between the 2 Fingers
        c1 = (s1[0] + s2[0]) // 2
        c2 = (s1[1] + s2[1]) // 2

        # Logic for Implementing Acceleration, Brake and Neutral according to the Region the Center Point Lies in
        if c2 > bh:
            ReleaseKey(W)
            PressKey(S)
            print('brake')

        elif c2 < ah:
            ReleaseKey(S)
            PressKey(W)
            print('accelerate')

        else:
            ReleaseKey(W)
            ReleaseKey(S)
            print('neutral')

        # Getting Angle of the Line by Fingers to Determine Turning Mode and its Region
        angle = math.atan((s2[1] - c2) / (s2[0] - c1))

        # Logic to Determine Turn Method by the Region of Angle of the Line
        if angle > 0.27:
            ReleaseKey(A)
            PressKey(D)
            print('right')

        elif angle < -0.27:
            ReleaseKey(D)
            PressKey(A)
            print('left')

        else:
            ReleaseKey(A)
            ReleaseKey(D)

        # Show Circle Point for the center of Fingers and a Line Connecting the Fingers
        cv2.circle(img, tuple([c1, c2]), 4, [255, 0, 0], 6)
        cv2.line(img, s1, s2, [0, 0, 255], 2)

    # If Fingers are not detected, then Release All Keys
    except:
        ReleaseKey(W)
        ReleaseKey(A)
        ReleaseKey(S)
        ReleaseKey(D)

    # Show the Output
    cv2.imshow('Image', img)

    # If ESC key Encountered, then Terminate
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
# Created By: Aadil Tajani
# Release All Keys at End
ReleaseKey(W)
ReleaseKey(A)
ReleaseKey(S)
ReleaseKey(D)

# Release Resources at End
cap.release()
cv2.destroyAllWindows()
