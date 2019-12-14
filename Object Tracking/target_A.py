from scipy.spatial import distance as dist
import numpy as np
import cv2
import imutils
import tello_drone as tello
import time


host = ''
port = 9000
local_address = (host, port)

# Pass the is_dummy flag to run the face  detection on a local camera
drone = tello.Tello(host, port, is_dummy=False)




frame_read = drone.get_frame_read()



frame1 = frame_read.frame
frame2 = frame_read.frame

cap = drone.get_video_capture()



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

    # if not -70 <= offset_y <= 70 and offset_y is not -30:
    #     if offset_y < 0:
    #         drone.move_up(20)
    #     elif offset_y > 0:
    #         drone.move_down(20)

    # if not 15000 <= offset_z <= 30000 and offset_z is not 0:
    #     if offset_z < 15000:
    #         drone.move_forward(20)
    #     elif offset_z > 30000:
    #         drone.move_backward(20)


def rotate(r,d):


    drone.rotate_ccw(r)
    r = d + r
    # time.sleep(2)
    return r

def hsv_Edge(frame):
    #yellow color detection range
    l_b = np.array([22,155,62])
    u_b = np.array([80,255,255])


    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


    mask =cv2.inRange(hsv,l_b,u_b)


    res = cv2.bitwise_and(frame, frame, mask=mask)


#commented transformations caused tracking without movement
    # diff = cv2.absdiff(mask1, mask2)
    gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    edge = cv2.GaussianBlur(gray, (5,5), 0)
    _, edge = cv2.threshold(edge, 20, 255, cv2.THRESH_BINARY)

    # edge = cv2.dilate(edge, None, iterations=2)

    return edge

def f_Marker( mark ):

    """
    finds largest contour/object among contours in frame
    ln#74-75
    returns minAreaRect and contourArea of largest object
    """

    contours, hierarchy = cv2.findContours(mark, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # if len(contours) > 0:
    #     cnts = imutils.grab_contours( contours )
    #     c = max(cnts, key = cv2.contourArea)
    cnts = [(cv2.contourArea(contour), contour) for contour in contours]

    if len(contours)==0:
        return 0, 0, None
    else:
        c = max(cnts, key=lambda x: x[0])[1]
        return cv2.minAreaRect( c ), cv2.contourArea(c), c
    # else:
    #     return False
def move_2Marker( box ):
    """
    calculates distance drone needs to move in cm
    inserts into to drone move command.
    """



    p, x, y = pixel( box )
    d = calc_distance( p, x, y )
    drone.move_forward( d )




# calculates mid points of 2 sets of x y coordinates.
# used in calculations to find distance needed to travel to object
def midpoint(a , b):
    return ((a[0]+b[0])*0.5,(a[1]+b[1])*0.5)

# uses box points to calculate pixel width of object
# used in calculations to find distance needed to travel to object
def pixel( box ):
    # tl, tr, br, bl
    ( x,  y,  w,  h) = box

    (tltrX,tltrY) = midpoint( x, y )
    (blbrX, blbrY ) = midpoint( h, w )

    (tlblX,tlblY) = midpoint( x, h )
    (trbrX, trbrY ) = midpoint( y, w )

    # dA is the pixel height of an object
    dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
    # dB is the pixel width of an object
    dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))


    # pixM is the pixel width / by known width 8in
    pixM = dB/ 8
    dimb = dB / pixM

    p = box[1][0]
    # cv2.putText(frame1, "{:.1f}in".format(dimb),
    #     (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
    #     0.65, (255, 255, 255), 2)


    return pixM, trbrX, trbrY

def calc_distance( pixel, x, y ):
    """ distance is calculated with values obtained from
        a static image with controlled variable i.e distance from
        camera and width of object
    """

    # f is the focal length
    # f = (pixel * knownDistance)knownWidth
    # f = (pixel * 72)/8
    f=31.5

    # from here using calculated value of f when can determine
    # d distance of object



    d = (f * 8)/pixel
    # --convert d from inches to cm that drone uses to measure movement
    d_cm = int(d * 2.54)


    """
    prints are trouble shooting to figure out what data has been gathered
    and if we can use it to focus/center object in frame.
    """
    print("============")
    print(f'focal : {f}')
    print(f'pixel:={pixel}')
    print(f'distance:={d}')
    print(f'distance CM:= {d_cm}')
    print("============")



    cv2.putText(frame1, "{:.1f}cm".format(d_cm),
        (int( x + 100 ), int( y )), cv2.FONT_HERSHEY_SIMPLEX,
        0.65, (255, 255, 255), 2)
    return d_cm

s = 0
once = 0


found = False

while True:




# testing : getting biggest contour and bounding box to it
# next step will be to put rotate drone if condition not met.

    edged = hsv_Edge(frame1)
    marker, area, cnt = f_Marker( edged )


    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    # Calculate frame center
    center_x = int(width/2)
    center_y = int(height/2)

    obj_center_x = center_x
    obj_center_y = center_y
    z_area = 0

    """
    if area from f_Marker is below threshold this case 1000 and found
    continues to be false rotate drone which acts as a search for object.
    """
    
    
    if area < 1000 and found == False:
        # rotates drone
        s = rotate( 8,s )
        # cv2.putText(frame1, f"Rotate", (10, 420), cv2.FONT_HERSHEY_SIMPLEX,
        #                 1, (0, 0, 255), 3)
        # cv2.imshow("feed", frame1)





    else:

    # draw a bounding box around the image and display it
        box = cv2.cv.BoxPoints(marker) if imutils.is_cv2() else cv2.boxPoints(marker)
        box = np.int0(box)
        cv2.drawContours(frame1, [box], -1, (0, 255, 0), 2)

        M = cv2.moments(cnt)


        (startX, startY, endX, endY) = box


        obj_center_x = int((startX[0] + endX[0]) / 2.0)
        obj_center_y = int((startY[1] + endY[1]) / 2.0)
        z_area = (endX[1]+endY[1]) * (endX[0] + endY[0])

        # using  moments to calculate center ln. 255
        o_x = int(M['m10']/M['m00'])
        o_y = int(M['m01']/M['m00'])
        mz_area = M['m00']

        print("\n **************")
        print(f"start x: {startX}")
        print(f"start y: {startY}")
        print(f"end x: {endX}")
        print(f"end y: {endY}")
        print(f"area: {z_area}")
        print("\n **************")
        print(f"moments X center: {o_x}")
        print(f"moments Y center: {o_y}")
        print(f"moments area: {mz_area}")


        print("\n **************")

        print (f"object center x: {obj_center_x}")
        print (f"object center y: {obj_center_y}")
        print (f"object area : {area}")
        print("**************")

        # Calculate recognized face offset from center
        # offset_x = obj_center_x - center_x
        offset_x = o_x - center_x
        # Add 30 so that the drone covers as much of the subject as possible
        # offset_y = obj_center_y - center_y - 30
        offset_y = o_y - center_y - 30


        print("**************")
        print (f"center x: {center_x}")
        print (f"center y: {center_y}")

        print (f"offset x: {offset_x}")
        print (f"offset y: {offset_y}")
        print("**************")



        cv2.putText(frame1, "Target Acquired:", (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 3)
        cv2.imshow("feed", frame1)
        found = True

        if found == True:
                if once == 0:
                    adjust_tello_position( offset_x, offset_y, mz_area)
                    move_2Marker( box )
                    once = 1

    cv2.imshow("feed", frame1)
    cv2.imshow("edged",edged )

    frame1 = frame2
    frame2 = frame_read.frame


    if cv2.waitKey(40) == 27:
        # cv2.imwrite('drone.jpg',frame1)
        break




drone.end()
cv2.destroyAllWindows()
