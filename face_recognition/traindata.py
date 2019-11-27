import cv2 as cv
import os
import numpy as np
from PIL import Image
import pickle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.join(BASE_DIR, "images")

#face_cascade = cv.CascadeClassifier('cascades/lbpcascade_frontalface_improved.xml')
face_cascade = cv.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')
recognizer = cv.face.LBPHFaceRecognizer_create()

current_id = 0
label_ids = {}
y_labels = []
x_train = []

for root, dirs, files in os.walk(image_dir):
    for file in files:
        if file.endswith("png") or file.endswith("jpg"):
            path = os.path.join(root,file)
            label = os.path.basename(root).replace(" ", "-")#.lower()
            #print(label, path)
            if not label in label_ids:
                label_ids[label] = current_id
                current_id +=1
            id_ = label_ids[label]
            #print(label_ids)
            pil_image = Image.open(path).convert("L")
            image_array = np.array(pil_image, "uint8")
            #print(image_array)
            faces = face_cascade.detectMultiScale(image_array, 1.3, minNeighbors=5)

            for(x,y,w,h) in faces:
                roi = image_array[y:y+h, x:x+w]
                x_train.append(roi)
                y_labels.append(id_)


with open("labels.pickle", 'wb') as f:
    pickle.dump(label_ids, f)

recognizer.train(x_train, np.array(y_labels)) 
recognizer.save("trainer.yml")  
print ("Done training data....")      
            