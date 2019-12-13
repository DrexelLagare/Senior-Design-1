import numpy as np
import cv2 as cv
import tello_drone as tello
import pickle

host = ''
port = 9000
local_address = (host, port)

# Pass the is_dummy flag to run the face detection on a local camera
#drone = tello.Tello(host, port, is_dummy=True) #local camera
drone = tello.Tello(host, port, is_dummy=False) #tello camera

def adjust_tello_position(offset_x, offset_y, offset_z):
    """
    Adjusts the position of the tello drone based on the offset values given from the frame

    :param offset_x: Offset between center and face x coordinates
    :param offset_y: Offset between center and face y coordinates
    :param offset_z: Area of the face detection rectangle on the frame
    """
    if not -90 <= offset_x <= 90 and offset_x is not 0:
        if offset_x < 0:
            drone.rotate_ccw(20)
        elif offset_x > 0:
            drone.rotate_cw(20)
    
    if not -70 <= offset_y <= 70 and offset_y is not -30:
        if offset_y < 0:
            drone.move_up(15)
        elif offset_y > 0:
            drone.move_down(20)
    
    if not 15000 <= offset_z <= 30000 and offset_z is not 0:
        if offset_z < 15000:
            drone.move_forward(20)
        elif offset_z > 30000:
            drone.move_backward(20) 


face_cascade = cv.CascadeClassifier('cascades/lbpcascade_frontalface_improved.xml')
#face_cascade = cv.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')

# Recognizer using LBPH algorithm for facial recognition
recognizer = cv.face.LBPHFaceRecognizer_create(radius = 1, neighbors = 8, grid_x = 8, grid_y = 8)

# Recognizer read the trainer.yml made by the traindata.py
recognizer.read("trainer.yml")

# labels dictionary to hold labels 
labels = {}

with open("labels.pickle", 'rb') as f:
    oglabels = pickle.load(f)  #before flip: lables = {'Drexel': 0}

    # After flip labels = {0: 'Drexel'}
    labels = {v:k for k,v in oglabels.items()} 

    # Print  statement to see who is in the labels dictionary
    # for x in labels:
    #    print(labels)

frame_read = drone.get_frame_read()

# Variable to indicate person not found yet
found = False

while True:
    
    # Video stream read in frame by frame
    frame = frame_read.frame
    cap = drone.get_video_capture()

    height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)
    width = cap.get(cv.CAP_PROP_FRAME_WIDTH)

    # Calculate frame center
    center_x = int(width/2)
    center_y = int(height/2)

    # Draw the center of the frame
    cv.circle(frame, (center_x, center_y), 10, (0, 255, 0))
    
    # Convert frame to grayscale in order to apply the haar cascade
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, minNeighbors=5)

    #Search room for a face in a false
    if found == False:
        drone.rotate_ccw(30)  # Problem: Once face is found it keeps trying to search

    
    # If a face is recognized, draw a rectangle over it and add it to the face list
    face_center_x = center_x
    face_center_y = center_y
    z_area = 0

    color = (0,0,255) #color red
    stroke = 2 #line thickness

    # Iterate through faces
    for face in faces:
        (x, y, w, h) = face

        # Region of interest that we are interested in
        roi_gray = gray[y:y+h,x:x+w]

        # recognizer.predict(roi_gray) to calculate and predict region of interest
        id_,conf = recognizer.predict(roi_gray)
        print(f"Confidence rating: {conf}")
      

        # Lock on to Drexel Only if the confidence rating is higher than 85
        if conf >= 85: # if confidence rating is over set it value will display name on top of rectangle 
            
            found = True # Drexel is found

            color = (0,255,0) # color green
            name = labels[id_] # set name to be Drexel from labels dictionary

            # Draw box around Drexel's face 
            cv.rectangle(frame,(x, y),(x + w, y + h), color, stroke)

            # Drexel will be shown on top of the boxed face
            font = cv.FONT_HERSHEY_SIMPLEX            
            cv.putText(frame,name,(x,y), font, 1, color, stroke, cv.LINE_AA) 
           
            # Adjust Tello to Drexel
            face_center_x = x + int(h/2)
            face_center_y = y + int(w/2)
            z_area = w * h

            # Circle used to try to center drone to be centered with the face
            cv.circle(frame, (face_center_x, face_center_y), 10, (0, 0, 255))

            # Calculate recognized face offset from center
            offset_x = face_center_x - center_x
            # Add 30 so that the drone covers as much of the subject as possible
            offset_y = face_center_y - center_y - 30

            # Adjust tello to be centered on person's face
            adjust_tello_position(offset_x, offset_y, z_area)
            
        else: # Confidence rating is below 85
            
            # Draw box around face
            cv.rectangle(frame,(x, y),(x + w, y + h), color, stroke) #Draw rectangle

            # Unknown will be shown on top of boxed faced
            font = cv.FONT_HERSHEY_SIMPLEX 
            cv.putText(frame,"Unknown",(x,y), font, 1, color, stroke, cv.LINE_AA)

            # Person is not Drexel, continue search for him
            found = False  
 
    # Display the resulting frame
    cv.imshow('Tello detection...', frame)
    if cv.waitKey(1) == ord('q'): # Land the drone once q key is hit
        break

# Stop the BackgroundFrameRead 
drone.end()
cv.destroyAllWindows()
