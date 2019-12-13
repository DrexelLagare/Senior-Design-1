import cv2 as cv
import os
import numpy as np
from PIL import Image
import pickle

# Setting path where images will be trained
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.join(BASE_DIR, "images") # Training data in images folder

#face_cascade = cv.CascadeClassifier('cascades/lbpcascade_frontalface_improved.xml')
face_cascade = cv.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')

# Recognizer using LBPH algorithm for facial recognition
recognizer = cv.face.LBPHFaceRecognizer_create()

# Counter to keep track of labels, labels will be the name of the person's folder in the images folder
current_id = 0

# Dictionary to hold labels
label_ids = {}

y_labels = []
x_train = []

for root, dirs, files in os.walk(image_dir):
    # Iterate through files
    for file in files:
        # In Drexel folder, images are either png or jpg
        if file.endswith("png") or file.endswith("jpg"):

            # Path to the images that are in Drexel folder that is inside images folder
            path = os.path.join(root,file)
            
            # Use path to obtain name of the person folder as a label
            label = os.path.basename(root).replace(" ", "-")#.lower()

            # print statement used to check the directory where the images will be trained
            # print(label, path)

            # Put labels inside label_ids dictionary, give them an id
            # and increment current_id counter for each label added
            if not label in label_ids:
                label_ids[label] = current_id
                current_id +=1
            id_ = label_ids[label]

            #print(label_ids)

            # Opening the image and convert the image to Grayscale
            pil_image = Image.open(path).convert("L")
            # Convert to numpy array 
            image_array = np.array(pil_image, "uint8")

            # Print statement to see what is inside the numpy array of image_array
            # print(image_array)

            # Face detector using face_cascade
            faces = face_cascade.detectMultiScale(image_array, 1.3, minNeighbors=5)

            # Region of interest to be trained
            for(x,y,w,h) in faces:
                roi = image_array[y:y+h, x:x+w]
                x_train.append(roi)  # Train region of interest (roi)
                y_labels.append(id_) # Each label wil have an id

# labels.pickle will be written in bytes as file
with open("labels.pickle", 'wb') as f:
    pickle.dump(label_ids, f)  # Dump label_ids to a file

# Training recognizer 
recognizer.train(x_train, np.array(y_labels)) 
recognizer.save("trainer.yml")  
print ("Done training data....")      
            