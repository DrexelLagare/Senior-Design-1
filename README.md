# Senior Design 

- Facial Recognition
    1. Find a person in the room
    2. Using quadrant to count people in a room
    
- Object Tracking Implementations:
    1. Object Tracking using KCF
    2. Object Tracking using HSV
    3. Counting Pads
    

# Find a Person in the Room
1. Finding a person in the room in a controlled environment in which everybody is facing the drone and the drone will slowly pan in a      circle to detect a face. 
2. Once a face is detected then the drone will make a comparison using the LBPH facial recogniton implemented in main.py. 
3. The LBPH facial recognition will determine if the face being compared is the person we are looking for by confidence rating. 
4. If the confidence rating is greater than or equal to 85 then that is the person we are looking for then that face will have green box    and the person's name on top and the drone will lock on and start following the matched person. 
5. If the confidence rating is lower than 85 than that face will have a red box with "Unknown" on top and the drone will continue its      search by panning around the room.

# Current Implementation
This is an implementation of face recognition and tracking on the dji Tello drone based on a HAAR Cascade using OpenCV and Python 3.6.

The current implementation allows the user to:

- Train images for Facial Recognition using traindata.py
- Launch the drone through the command line using `python main.py`
- Receive video feed from the drone to the computer and visualize the face detection and face recognition carried out by the drone

It allows the drone to:

- Search the room by slowly panning in a circle
- Detect multiple faces at any given frame
- LBPH facial recognition implemenation allows to compare if the detected face is the person we are looking 
- If confidence rating is greater than or equal to 85 the drone will lock on and follow the matched person
- If confidence rating is lower than 85 it will continue searching the room 
- Position the user at the center of any shot by deciding the best movement based on the users x, y and z coordinates

**Note:** Current implementation allows only tracking of 1 user.

## Quick Start

To initialize your drone and get it up and running, simply clone the repository and download its dependencies with:

```bash
pip install -r requirements.txt
```

## How to Train images using Traindata.py for facial recognition
1. In images folder create a folder and name that folder the person you want the drone to recognize
2. Inside the person's folder add images and number them 1, 2, 3, etc.
3. In order to train on the images make sure you are in the right directory and in the terminal type in:

  ```bash
   python traindata.py
  ```
4. Training is complete when you get a message: Done training data... 

## Find a Person in the Room program in main.py
1. Make sure the person to find is in the room and data was trained for that person
2. Connect to the Tello wifi and open the terminal
3. Start find the person program by typing in the terminal:

  ```bash
    python main.py
  ```
4. Drone launches and starts searching
5. If the confidence rating is greater than or equal to 85, there will be a green rectangle on the face with 
   the person's name on top, lock on to the person and start following. 
   NOTE: The person must face the drone to be followed
6. If the confidence rating is below 85 than there will be a red rectangle with the name of "Unknown" on
   the face and the drown will keep rotating to search for the person.


## Next Steps
- [ ] Make the facial recognition more accurate, the facial recognition usually recognizes
      the wrong person to be the person we were looking ofr.
- [ ] Fix warning messages when executing the command and waiting for drone video feed
- [ ] Support drone centering with multiple users in a shot
- [ ] Optimize code for better video performance
 
Original Github link to Face Detection and Tracking: https://github.com/juanmapf97/Tello-Face-Recognition

## Using quadrant to count people in a room
1. This program counts the people in the room. When the program runs the user can control the drone
   using the keys mentioned in the quadrant.py
2. Connect to the Tello wifi and open the terminal
3. Start find the person program by typing in the terminal:

  ```bash
    python quadrant.py
  ```
4. Once a person is found press the space bar to update counter.



## Object Tracking Implementations:




## Object Tracking using KCF
1. This program will run on your computer's camera. To run program open the terminal and type in
  ```bash
    python objectTracking.py
  ```
2. Put an object infront of the camera and hold it still until the there is a box around it to indicate
   the object is being tracked.
3. Slowly move the object across the camera to see the tracking. 

   NOTE: Moving the object quickly across the camera will result in a lost of tracking of the 
         object and having to go back to step 2 to start tracking again.

## Object Tracking using HSV
1. This program will have the drone find an object in the room by having the drone pan in a circle
2. Connect to the Tello wifi and open the terminal
3. Start the program by typing in the terminal:

  ```bash
    python target_A.py
  ```
4. The drone will launch and pan in a circle to find the object
5. Once the object is found it will draw a green box on the object, lock on and get closer to the object

## Counting Pads
1. This program will have the drone recognize pads that came with the Tello EDU drone. We covered the pads
   with a black covering to make it was the color easiest for the drone to recognize. The pads were either
   upright or angled to make the pads identifiable
2. Connect to the Tello wifi and open the terminal
3. Start the program by typing in the terminal:

  ```bash
    python CountingPads.py
  ```
 4. The drone will rotate in a circle to look for pads. Once a pad is found it will draw a green rectangle 
    around the pad and then continue rotating to look for more pads.
 
