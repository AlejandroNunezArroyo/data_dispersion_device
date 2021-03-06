# import the OpenCV library for computer vision
import cv2
# from object_detector import *
from circle_detector import *
import numpy as np
import time
import streamlit as st
import urllib.request
import datetime
from PIL import Image
import pandas as pd


#****************************

#****************************

# Load the dictionary that was used to generate the markers.
# There's different aruco marker dictionaries, this code uses 6x6
# dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_50)
dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_ARUCO_ORIGINAL)

# Initialize the detector parameters using default values
parameters = cv2.aruco.DetectorParameters_create()

# initialize the webcam as "camera" object
camera = cv2.VideoCapture(0)
# we dont use set for problems with camera 
# camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Load Object Detector
detector = HomogeneousBgDetectorCircle()

x_0 = x_1 = y_0 = y_1 = 0
bool_v = True
fun_counter = 0 
(mark_counter) = 0

state_dif_line = 0 
special_conter = 0

v_medium_center_circle_x = []
v_medium_center_circle_y = []
v_dis = []

while(bool_v):

    # creates an "img" var that takes in a camera frame
    _, img = camera.read()
    ## convert to hsv
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_range = np.array([61, 48, 116])
    upper_range = np.array([94, 186, 214])
        
    ## mask of green (36,0,0) ~ (70, 255,255)
    mask1 = cv2.inRange(hsv, lower_range, upper_range)
    
    img_circle = img
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # detect aruco tags within the frame
    markerCorners, markerIds, rejectedCandidates = cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)

    # draw box around aruco marker within camera frame
    img = cv2.aruco.drawDetectedMarkers(img, markerCorners, markerIds)

    # if a tag is found...
    if markerIds is not None:
        # for every tag in the array of detected tags...
        for i in range(len(markerIds)):
            # _________________________________________________________
            # Values to convert pixel to radio.
            # Draw polygon around the marker
            int_corners = np.int0(markerCorners)
            cv2.polylines(img, int_corners, True, (0, 255, 0), 5)

            # Aruco Perimeter
            aruco_perimeter = cv2.arcLength(markerCorners[0], True)

            # Pixel to cm ratio convertion
            pixel_cm_ratio = aruco_perimeter / 8
            # pixel_cm_ratio = aruco_perimeter / 20
            # _________________________________________________________
            
            (topLeft, topRight, bottomRight, bottomLeft) = markerCorners[i][0]
            
            # convert each of the (x, y)-coordinate pairs to integers
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))

            # draw the bounding box of the ArUCo detection
            cv2.line(img, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(img, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(img, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(img, bottomLeft, topLeft, (0, 255, 0), 2)

            # compute and draw the center (x, y)-coordinates of the ArUco
            # marker
            # cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            # cY = int((topLeft[1] + bottomRight[1]) / 2.0)

            # Value of the marker
            object_width = ( ( ((topRight[0] - topLeft[0])**2) + ((topRight[1] - topLeft[1])**2) ) ** (1/2)) / pixel_cm_ratio
            object_height = ( ( ((topRight[0] - bottomRight[0])**2) + ((topRight[1] - bottomRight[1])**2) ) ** (1/2)) / pixel_cm_ratio

            # marker ids 
            if i == 0:
                cv2.putText(img, "Tag 0 Detected!", (25, 400), cv2.FONT_HERSHEY_COMPLEX, 0.7,
                            (0, 255, 0), 2)
                x_0 = topRight[0]
                y_0 = topRight[1]

            if i == 1:
                cv2.putText(img, "Tag 1 Detected!", (25, 425), cv2.FONT_HERSHEY_COMPLEX, 0.7,
                            (0, 255, 0), 2)
                x_1 = topRight[0]
                y_1 = topRight[1]
                
            circles_im = np.copy(img_circle)
            # contours = detector.detect_objects(img)
            cv2.imshow('frame', img) 
            cv2.imshow('mask1', mask1)
            
            centro_total_x = int((x_0 + x_1) / 2.0)
            centro_total_y = int((y_0 + y_1) / 2.0)

            diagonal_line = ( ( ((x_0 - x_1)**2) + ((y_0 - y_1)**2) ) ** (1/2)) / pixel_cm_ratio
                
            cv2.line(img, (x_0, y_0), (x_1, y_1), (255, 0, 0), 2)
            cv2.circle(img, (int(centro_total_x), int(centro_total_y)), 6, (0, 0, 255), -1)
            
            # the code works when detec a circle 
            try: 
                circles = detector.circle_detector(mask1)
                medium_center_circle_x = 0
                medium_center_circle_y = 0
                counter = 0 
                for circle in circles[0,:]:
                    counter += 1
                    # draw the outer circle
                    cv2.circle(circles_im,(circle[0],circle[1]),circle[2],(255,0,0),2)
                    # draw the center of the circle
                    cv2.circle(circles_im,(circle[0],circle[1]),2,(0,0,255),3)
                    # average circle from ball
                    medium_center_circle_x = circle[0] + medium_center_circle_x
                    medium_center_circle_y = circle[1] + medium_center_circle_y
                
                # cv2.imshow('circles_im', circles_im) 

                medium_center_circle_x = medium_center_circle_x/counter
                medium_center_circle_y = medium_center_circle_y/counter
                # Draw space:
                # centro_total_x = int((x_0 + x_1) / 2.0)
                # centro_total_y = int((y_0 + y_1) / 2.0)

                # diagonal_line = ( ( ((x_0 - x_1)**2) + ((y_0 - y_1)**2) ) ** (1/2)) / pixel_cm_ratio

                dif_line = ( ( ((centro_total_x - medium_center_circle_x)**2) + ((centro_total_y - medium_center_circle_y)**2) ) ** (1/2)) / pixel_cm_ratio

                # print("center x", medium_center_circle_x, "center y", medium_center_circle_y, "distancia", dif_line)
                # print("center circle: ", centro_total_x, centro_total_y)
                # Center circle 
                # Put value of detection
                # cv2.putText(img, "Width {} cm".format(round(object_width, 1)), (int(cX - 100), int(cY - 20)), cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)
                # cv2.putText(img, "Height {} cm".format(round(object_height, 1)), (int(cX - 100), int(cY + 15)), cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)
                # cv2.putText(img, "Diagonal {} cm".format(round(diagonal_line, 1)), (300, 400), cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)
                #**************************
                # cv2.circle(img, (int(centro_total_x), int(centro_total_y)), 6, (0, 0, 255), -1)
                # cv2.putText(img, "Diferencia {} cm".format(round(dif_line, 1)), (300, 400), cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)
                # cv2.line(img, (x_0, y_0), (x_1, y_1), (255, 0, 0), 2)
                #**************************
                
                # cv2.line(img, (centro_total_x, centro_total_y), (medium_center_circle_x, medium_center_circle_y), (255, 0, 0), 2)
                # Draw the center of aruko marker
                # cv2.circle(img, (cX, cY), 4, (0, 0, 255), -1)
                if ((centro_total_x > 300 and centro_total_x < 350) and (centro_total_y > 240 and centro_total_y < 264)):
                    if fun_counter == 2:
                        special_conter += 1
                        # print("entra condicion")
                        # cv2.putText(img, "Diferencia {} cm".format(round(dif_line, 1)), (300, 400), cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)
                        cv2.line(img, (x_0, y_0), (x_1, y_1), (255, 0, 0), 2)
                        cv2.circle(img, (int(centro_total_x), int(centro_total_y)), 6, (0, 0, 255), -1)
                        cv2.imwrite('lab'+str(special_conter)+'.png', circles_im)
                        state_dif_line = dif_line
                        v_medium_center_circle_x.append(medium_center_circle_x)
                        v_medium_center_circle_y.append(medium_center_circle_y)
                        v_dis.append(state_dif_line)
                        print(medium_center_circle_x, medium_center_circle_y, state_dif_line)
                        df1 = pd.DataFrame({'Eje X': v_medium_center_circle_x,
                            'Eje Y': v_medium_center_circle_y, 
                            'Distancia del centro': v_dis})
                        df1.to_csv('experiment.csv', index=False)
                        
                        
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                        # print(fun_counter)
                        fun_counter += 1
                        time.sleep(7)
                        # bool_v = False
                        break
                    else: 
                        fun_counter += 1   
            except:
                bool_v = True
                fun_counter = 0

    # handler to press the "q" key to exit the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        # print(v_medium_center_circle_x)
        # print(v_medium_center_circle_y)
        # print(v_dis)
        # df1 = pd.DataFrame({'Eje X': v_medium_center_circle_x,
        #     'Eje Y': v_medium_center_circle_y, 
        #     'Distancia del centro': v_dis})
        # df1.to_csv('experiment.csv')
        break

# When everything done, release the capture
camera.release()
cv2.destroyAllWindows()