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
            drone.rotate_ccw(10)
        elif offset_x > 0:
            drone.rotate_cw(10)
    
    if not -70 <= offset_y <= 70 and offset_y is not -30:
        if offset_y < 0:
            drone.move_up(20)
        elif offset_y > 0:
            drone.move_down(20)
    
    if not 15000 <= offset_z <= 30000 and offset_z is not 0:
        if offset_z < 15000:
            drone.move_forward(20)
        elif offset_z > 30000:
            drone.move_backward(20) 


face_cascade = cv.CascadeClassifier('cascades/lbpcascade_frontalface_improved.xml')
#face_cascade = cv.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')
recognizer = cv.face.LBPHFaceRecognizer_create()
recognizer.read("trainer.yml")

labels = {}
with open("labels.pickle", 'rb') as f:
    oglabels = pickle.load(f)
    labels = {v:k for k,v in oglabels.items()}

frame_read = drone.get_frame_read()
while True:
    # frame = cv.cvtColor(frame_read.frame, cv.COLOR_BGR2RGB)
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

    # If a face is recognized, draw a rectangle over it and add it to the face list
    face_center_x = center_x
    face_center_y = center_y
    z_area = 0

    color = (255,0,0) #color blue
    stroke = 2 #line thickness
    for face in faces:
        (x, y, w, h) = face
        roi_gray = gray[y:y+h,x:x+w]

        id_,conf = recognizer.predict(roi_gray)
        print(f"Confidence rating: {conf}")
        if conf >= 65: # if confidence rating is over set value will display name on top of rectangle 
            #print(id_)
            name = labels[id_]
            font = cv.FONT_HERSHEY_SIMPLEX            
            cv.putText(frame,name,(x,y), font, 1, color, stroke, cv.LINE_AA) 
        #else:
            #drone.rotate_ccw(10)

        #img_item = "frameImg.png"
        #cv.imwrite(img_item, roi_gray)

        cv.rectangle(frame,(x, y),(x + w, y + h), color, stroke)

        face_center_x = x + int(h/2)
        face_center_y = y + int(w/2)
        z_area = w * h

        cv.circle(frame, (face_center_x, face_center_y), 10, (0, 0, 255))

    # Calculate recognized face offset from center
    offset_x = face_center_x - center_x
    # Add 30 so that the drone covers as much of the subject as possible
    offset_y = face_center_y - center_y - 30

    #cv.putText(frame, f'[{offset_x}, {offset_y}, {z_area}]', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv.LINE_AA)
    adjust_tello_position(offset_x, offset_y, z_area)
    
    # Display the resulting frame
    cv.imshow('Tello detection...', frame)
    if cv.waitKey(1) == ord('q'):
        break

# Stop the BackgroundFrameRead and land the drone
drone.end()
cv.destroyAllWindows()
