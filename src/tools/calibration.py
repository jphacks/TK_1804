import numpy as np
import cv2

cap = cv2.VideoCapture(0)

if cap.isOpened() is False:
    raise("IO Error")

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

imgInd=0
while True:
    ret, img = cap.read()
    if ret == False:
        continue
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    cv2.putText(img,'Number of capture: '+str(imgInd),(30,20),cv2.FONT_HERSHEY_PLAIN, 1,(0,255,0))
    cv2.putText(img,'c: Capture the image',(30,40),cv2.FONT_HERSHEY_PLAIN, 1,(0,255,0))
    cv2.putText(img,'q: Finish capturing and calcurate the camera matrix and distortion',(30,60),cv2.FONT_HERSHEY_PLAIN, 1,(0,255,0))
    cv2.imshow("Image", img) 

    k = cv2.waitKey(1) & 0xFF
    if k == ord('c'):
        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (7,6),None)
        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)

            corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
            imgpoints.append(corners2)

            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, (7,6), corners2,ret)
            cv2.imshow('Image',img)
            cv2.waitKey(500)

            imgInd+=1

    if k == ord('q'):
        break

# Calc urate the camera matrix
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)

# Save the csv file
np.savetxt("mtx.csv", mtx, delimiter=",")
np.savetxt("dist.csv", dist, delimiter=",")

cap.release()
cv2.destroyAllWindows()