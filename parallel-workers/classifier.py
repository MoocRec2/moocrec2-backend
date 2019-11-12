import os
import cv2
import os.path
import numpy as np
import tensorflow as tf
from keras.applications.vgg16 import VGG16
from keras.preprocessing import image
from keras.models import load_model
from keras import backend as K
from datetime import datetime

K.set_image_dim_ordering('tf')

classifier_path = './vgg16_model.h5'
classifier = load_model(classifier_path)
classifier.summary()
model = VGG16(weights='imagenet', include_top=False)

video_directory = './videos/'
img_directory = './images/'
model = VGG16(weights='imagenet', include_top=False )


# Set up directories.
if not os.path.exists(video_directory):
    os.makedirs(video_directory)
if not os.path.exists(img_directory):
    os.makedirs(img_directory)

def deleteImages():
    for root, dirs, files in os.walk(img_directory):
        for file in files:
            os.remove(os.path.join(root,file))


def predict(file):
    global model
    x = image.load_img(file, target_size=(150,150))
    x = image.img_to_array(x)
    x = x/255
    x = np.expand_dims(x, axis=0)
    features = model.predict(x)
    result = classifier.predict_classes(features)
    if result[0] == 0:
        prediction = 'animation'
    elif result[0] == 1:
        prediction = 'code'
    elif result[0] == 2:
        prediction = 'head'
    elif result[0] == 3:
        prediction = 'slide'
    elif result[0] == 4:
        prediction = 'writing'
    return prediction

def videoStyles(file_, start_frame, end_frame):
    num = 0
    count = 0
    cap = cv2.VideoCapture(file_)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    end_frame = length-1 if length < end_frame else end_frame-1
    
    print(file_)
    print('[INFO] Video file: {file}'.format(file=file_))
    print('[INFO] Number of frames in the video: {frames}\n[INFO] Frames range to be classified: {sframe} --> {eframe}'.format(frames=length, sframe=start_frame, eframe=end_frame))
    
    for i in range(start_frame, end_frame, 50):
        cap.set(1, i)
        res, frame = cap.read()
        name = '{directory}/to_be_classified_{i}.jpg'.format(directory='./images', i=i)

        if res:
            cv2.imwrite(name, frame)

    cap.release()
    dir_content = os.listdir(img_directory)
    list_img = [img for img in dir_content if 'to_be_classified' in img]   # to avoid unnecessary files being read.
    img_count = len(list_img)

    print('[INFO] Directory contains #{count} images'.format(count=img_count))
    # Probabilities for each style.
    head = 0
    code = 0
    slide = 0 
    writing = 0
    animation = 0
    
    for img in list_img:
        temp = predict(img_directory+img)
        if temp == 'head':
            head +=1
        elif temp == 'code':
            code +=1
        elif temp == 'slide':
            slide +=1
        elif temp == 'animation':
            animation +=1
        elif temp == 'writing':
            writing +=1

    deleteImages()

    head_p = round(((head / img_count) * 100), 2)
    code_p = round(((code / img_count) * 100), 2)
    slide_p = round(((slide / img_count) * 100), 2)
    animation_p = round(((animation / img_count) * 100), 2)
    writing_p = round(((writing / img_count) * 100), 2)

    print('[SUMMARY] Frames classified: {sframe} --> {eframe}. Classifications: Talking Head->{hc}, Code->{cc}, Slides->{sc}, Writing->{wc}, Animation->{ac}'.format(
        sframe=start_frame, eframe=end_frame, hc=head_p, cc=code_p, sc=slide_p, wc=writing_p, ac=animation_p))

    return head_p,code_p,slide_p,animation_p,writing_p
