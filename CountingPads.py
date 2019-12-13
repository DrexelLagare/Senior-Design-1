import numpy as np
import cv2
import tello_drone as tello
import time

host = ''
port = 9000
local_address = (host, port)
counter = 0
img_counter = 0
quadrant = 1
pad_found = False

# Pass the is_dummy flag to run the face detection on a local camera
drone = tello.Tello(host, port, is_dummy=False)

#initial read of the frame from drone
frame_read = drone.get_frame_read()
cap = drone.get_video_capture()
z_area = 0

def rotate(r):

    r = r + 1

    return r

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

#finds the contours of the color and returns the value of the largets one
def frame_contours( mark ):
    contours, hierarchy = cv2.findContours(mark, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = [(cv2.contourArea(contour), contour) for contour in contours]
    if len(contours)==0:
        return 0, 0, None
    else:
        c = max(cnts, key=lambda x: x[0])[1]
        return cv2.minAreaRect( c ), cv2.contourArea(c), c

#uses hsv to apply the color range to find the black pads
def Finding_Pads(frame1):
    #sets the lower and upper bounds for the color blakc
    lower_bound = np.array([0,0,0])
    upper_bound = np.array([180,255,30])

    #converts from bgr to hsv
    hsv1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV)

    #checks to make sure it is within range
    mask1 =cv2.inRange(hsv1,lower_bound,upper_bound)

    #clears up the image
    res1 = cv2.bitwise_and(frame1, frame1, mask=mask1)
    gray = cv2.cvtColor(res1, cv2.COLOR_BGR2GRAY)
    edge = cv2.GaussianBlur(gray, (5,5), 0)
    _, edge = cv2.threshold(edge, 20, 255, cv2.THRESH_BINARY)

    return edge

while True:
    #assigns the frame read in from the drone to be used in functions
    frame1 = frame_read.frame
    #calls the function that uses the hsv approach to find the black pads
    test = Finding_Pads(frame1)
    #places the frame around the largest contour area
    mark1, area, best = frame_contours(test)

    #finds the height and width and assigns them respectively
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    # Calculate frame center
    center_x = int(width/2)
    center_y = int(height/2)
    z_area = height * width

    # Draw the center of the frame
    cv2.circle(frame1, (center_x, center_y), 10, (0, 255, 0))

    s = 1
    #find the smallest possible frame demensions for the object
    (x, y, w, h) = cv2.boundingRect(best)
    #used to rotate the drone with out user input
    if area < 2000:
        s = rotate(s)
    else:
        #draws the actual frame
        cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.imshow("Pad Finder", frame1)

    #adjust the position of the drone in flight otherwise without it causes the drone to land while stream is still going
    adjust_tello_position(center_x, center_y, z_area)
    
    k = cv2.waitKey(1)

    #movements for the drone implemented in quadrant.py
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = "opencv2_frame_{}.png".format(img_counter)
        cv2.imwrite(img_name, frame1)
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
    		pad_found = False
    	elif quadrant > 1:
    		quadrant -= 1
    		pad_found = False
    # e key for 'rotate clockwise'
    elif k%256 == 101:
    	drone.rotate_cw(90)
    	if quadrant == 4:
    		quadrant = 1
    		pad_found = False
    	elif quadrant < 4:
    		quadrant += 1
    		pad_found = False
    # Display the resulting frame
    if cv2.waitKey(1) == ord('x'):
        break

    #the quadrant counter implemented in quandrant.py
    if pad_found == False and quadrant == 1:
        counter += 1
        pad_found = True
    
    if pad_found == False and quadrant == 2:
        counter += 1
        pad_found = True
    if pad_found == False and quadrant == 3:
        counter += 1
        pad_found = True
    if pad_found == False and quadrant == 4:
        counter += 1
        pad_found = True

    print(counter)

# Stop the BackgroundFrameRead and land the drone
drone.end()
cv2.destroyAllWindows()