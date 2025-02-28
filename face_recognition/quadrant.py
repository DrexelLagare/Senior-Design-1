import numpy as np
import cv2 as cv
import tello_drone as tello
import time

host = ''
port = 9000
local_address = (host, port)
counter = 0
img_counter = 0
quadrant = 1
face_capture = False
spin = True

# Pass the is_dummy flag to run the face detection on a local camera
drone = tello.Tello(host, port, is_dummy=False)


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


face_cascade = cv.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')
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
    for face in faces:
        (x, y, w, h) = face
        cv.rectangle(frame,(x, y),(x + w, y + h),(255, 255, 0), 2)

        face_center_x = x + int(h/2)
        face_center_y = y + int(w/2)
        z_area = w * h

        cv.circle(frame, (face_center_x, face_center_y), 10, (0, 0, 255))
        
        if face_capture == False and quadrant == 1:
        	counter += 1
        	face_capture = True
        if face_capture == False and quadrant == 2:
        	counter += 1
        	face_capture = True
        if face_capture == False and quadrant == 3:
        	counter += 1
        	face_capture = True
        if face_capture == False and quadrant == 4:
        	counter += 1
        	face_capture = True

        print(counter)

    # Calculate recognized face offset from center
    offset_x = face_center_x - center_x
    # Add 30 so that the drone covers as much of the subject as possible
    offset_y = face_center_y - center_y - 30

    cv.putText(frame, f'[{offset_x}, {offset_y}, {z_area}]', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv.LINE_AA)
    #adjust_tello_position(offset_x, offset_y, z_area)
    
    k = cv.waitKey(1)

    # Test Drone
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = "opencv_frame_{}.png".format(img_counter)
        cv.imwrite(img_name, frame)
        print("{} written!".format(img_name))
    
        img_counter += 1
    # w key for 'forward'
    elif k%256 == 119:
    	drone.move_forward(60)
    # a key for 'left'
    elif k%256 == 97:
    	drone.move_left(40)
    # s key for 'backward'
    elif k%256 == 115:
    	drone.move_backward(60)
    # d key for 'left'
    elif k%256 == 100:
    	drone.move_right(40)
    # r key for 'up'
    elif k%256 == 114:
    	drone.move_up(40)
    # f key for 'down'
    elif k%256 == 102:
    	drone.move_down(40)
    # q key for 'rotate counter clockwise'
    elif k%256 == 113:
    	drone.rotate_ccw(90)
    	if quadrant == 1:
    		quadrant = 4
    		face_capture = False
    	elif quadrant > 1:
    		quadrant -= 1
    		face_capture = False
    # e key for 'rotate clockwise'
    elif k%256 == 101:
    	drone.rotate_cw(90)
    	if quadrant == 4:
    		quadrant = 1
    		face_capture = False
    	elif quadrant < 4:
    		quadrant += 1
    		face_capture = False
    # Display the resulting frame
    cv.imshow('Tello detection...', frame)
    if cv.waitKey(1) == ord('x'):
        break
#
# Stop the BackgroundFrameRead and land the drone
drone.end()
cv.destroyAllWindows()
