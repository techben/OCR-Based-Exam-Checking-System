# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 16:34:03 2018

@author: Areeba aftab
"""

# Define if you want to download data from the original database or use the dataset one already provided and preprocessed
# Use:
# 'load': If you want to load the datase from the directory
# 'download': To download data from the database and process the images
dataset_load_method = 'download'

# Define if you want to save the dataset to a file
save_dataset = False nve,

# Define if you want to load the trained classifiers from the directory
#load_classifiers = False
load_classifiers = False


# Define if you want to save the trained classifiers to a file
#save_classifiers = True
save_classifiers = False


# Define if you want to save classification test output to a file
save_results = True
if (save_results):
    result_output_file = open('result_output.txt','w') 

# Define if you want to print errors and warnings
enable_error_output = False


import numpy as np
import matplotlib.pyplot as plt
import plotly.offline as py
py.init_notebook_mode(connected=True)
import plotly.graph_objs as go
import plotly.tools as tls
import scipy
import sklearn
import pandas as pd
from sklearn import linear_model, datasets, metrics
#from sklearn.model_selection import train_test_split
from sklearn.cross_validation import train_test_split
from sklearn.preprocessing import binarize
from sklearn.neural_network import BernoulliRBM, MLPClassifier
from sklearn.datasets import fetch_mldata
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from skimage import data, color, exposure, measure
from skimage.transform import resize
from skimage.feature import hog
from sklearn.manifold import TSNE
from sklearn.externals import joblib

from io import StringIO
import cv2
from scipy import ndimage
from difflib import SequenceMatcher
from sys import stdout
from IPython.display import clear_output
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
from nltk.corpus import wordnet as wn 
import gensim

def print_percentage(prct, msg=None):
    if (prct > 100 or prct < 0):
        return
    clear_output(wait=True)
    if (msg == None):
        stdout.write("Progress: [")
    else:
        stdout.write(msg+" [")
    end = int(int(prct)/10)
    for i in range(0, end):
        stdout.write("=")
    for i in range(end, 10):
        stdout.write(" ")
    stdout.write("] "+str(prct)+"%")
    stdout.flush()

df2=pd.read_csv("../new alphabets.csv", sep=',',header=None)
df3=pd.read_csv("../alphabets test.csv", sep=',',header=None)


def delborders(crop):
    cropf = ndimage.gaussian_filter(crop, 0.5)
    cropbin = (cropf<0.8)
    labeled, nr_objects = ndimage.label(cropbin)
    labels_to_delete = []
    for i in range(0, labeled.shape[1]):
        if (labeled[labeled.shape[0]-1][i] > 0):
            labels_to_delete.append(labeled[labeled.shape[0]-1][i])
    
    label_in_delete = False
    for x in range(0, labeled.shape[1]):
        for y in range(0, labeled.shape[0]):
            label_in_delete = False
            for l in range(0, len(labels_to_delete)):
                if (labeled[y][x] == labels_to_delete[l]):
                    label_in_delete = True
            
            if(label_in_delete):
                crop[y][x] = 1.0
    
    return crop
    
def getcrop(n):
    image = cv2.imread(df2[1][n])
    
    
    #plt.imshow(image) 
    imgh, imgw = image.shape[:-1]
    img_rgb = image.copy()
    template = cv2.imread("../template.png")
    h, w = template.shape[:-1]
    
    template_match_success = False
    res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
    threshold = .7
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):  # Switch collumns agetd rows
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        croph1 = pt[1]
        croph2 = pt[1]+h
        cropw = pt[0] + w
        template_match_success = True
        
    
    if (not template_match_success):
        #Template matching has failed so return...
        crop = image.copy()
        crop = color.rgb2gray(crop)
          
        return crop, True
        
    
    if (df2[3][n] == 'first' or df2[3][n] == 'last'):
        crop = image.copy()[max(croph1-6, 0):min(croph2+6, imgh), cropw:imgw]
    else:
        crop = image.copy()[max(min(croph2+4, imgh-1), 0):imgh, :]
        
    crop = color.rgb2gray(crop)
    if (df2[3][n] == 'first_b' or df2[3][n] == 'last_b'):
        crop = delborders(crop)
    crop = cv2.resize(crop, dsize=(315,24), interpolation=cv2.INTER_CUBIC)
    return crop, True

def getcrop1(n):
    image = cv2.imread(df3[1][n])
    
    
    #plt.imshow(image) 
    imgh, imgw = image.shape[:-1]
    img_rgb = image.copy()
    template = cv2.imread("../template.png")
    h, w = template.shape[:-1]
    
    template_match_success = False
    res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
    threshold = .7
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):  # Switch collumns and rows
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        croph1 = pt[1]
        croph2 = pt[1]+h
        cropw = pt[0] + w
        template_match_success = True
        
    
    if (not template_match_success):
        #Template matching has failed so return...
        crop = image.copy()
        crop = color.rgb2gray(crop)
          
        return crop, True
        
    
    if (df3[2][n] == 'first' or df3[2][n] == 'last'):
        crop = image.copy()[max(croph1-6, 0):min(croph2+6, imgh), cropw:imgw]
    else:
        crop = image.copy()[max(min(croph2+4, imgh-1), 0):imgh, :]
        
    crop = color.rgb2gray(crop)
    if (df3[2][n] == 'first_b' or df3[2][n] == 'last_b'):
        crop = delborders(crop)
    crop = cv2.resize(crop, dsize=(315,24), interpolation=cv2.INTER_CUBIC)
    return crop, True
def gen_dataset(n=df2.shape[0]):
    data = []
    labels = []
    for i in range(1, n):
        crop, success = getcrop(i)
        if (success):
            data.append(crop)
            labels.append(df2[2][i])
            print(labels)
        else:
            if (enable_error_output):
                print("[WARNING] Template matching has failed for image: "+str(i))
        print_percentage((i*100/(n-1)), "Fetched "+str(i)+" images:")
    
    print_percentage(100, "Fetched "+str(n-1)+" images:")
    print("")
    print("Finished!")
    return data, labels

def gen_dataset1(n=df3.shape[0]):
    data1 = []
    #labels = []
    for i in range(1, n):
        crop1, success1 = getcrop1(i)
        if (success1):
            data1.append(crop1)
            #labels.append(df2[2][i])
            #print(labels)
        else:
            if (enable_error_output):
                print("[WARNING] Template matching has failed for image: "+str(i))
        print_percentage((i*100/(n-1)), "Fetched "+str(i)+" images:")
    
    print_percentage(100, "Fetched "+str(n-1)+" images:")
    print("")
    print("Finished!")
    return data1

 if (dataset_load_method == 'download'):
    dataset, labels = gen_dataset(69)
    dataset1 = gen_dataset1(12)

    
    

# Load dataset from files
if (dataset_load_method == 'load'):
    dataset = np.load("C:/Users/Areeba Aftab/Desktop/checker/github/handwritten/Handwritten-Names-Recognition-master/Notebook/HandwrittenNames_data2.npz")['data']
    labels = np.load("C:/Users/Areeba Aftab/Desktop/checker/github/handwritten/Handwritten-Names-Recognition-master/Notebook/HandwrittenNames_labels.npz")['data']

# If specified, the generated dataset can be saved to .npz files using these functions.

# In[ ]:

# Save dataset to a file if defined
if (save_dataset):
    np.savez("C:/Users/Areeba Aftab/Desktop/checker/github/handwritten/Handwritten-Names-Recognition-master/Notebook/HandwrittenNames_data2.npz", data=dataset)
    np.savez("C:/Users/Areeba Aftab/Desktop/checker/github/handwritten/Handwritten-Names-Recognition-master/Notebook/HandwrittenNames_labels2.npz", data=labels)


# We can plot some images and print their corresponding labels to check that everything is correct: 

# In[ ]:

# Change selection to plot a different image and label
selection = 7
plt.imshow(dataset[selection], cmap='gray')
plt.show()
print(labels[selection])
print(str(type(labels[7])))


# # 3. Defining extra helpful functions
# 
# In this section of the notebook we will define some functions that will be useful later on.

# ### get_labels
# 
# This function labels the connected components in an image by binarizing it and running a clustering method, it returns the labels and the number of labels it detects.

# In[ ]:

def get_labels(crop):
    
    img = crop.copy() # gray-scale image
    
    # You could smooth the image (to remove small objects) but we saw better results without using it...
    # blur_radius = 0.5
    # imgf = ndimage.gaussian_filter(img, blur_radius)
    
    threshold = 0.8
    
    # Find connected components
    labeled, nr_objects = ndimage.label(img<threshold) 
    #print("Number of objects is " +str(nr_objects))

    # Find connected components
    #labeled, nr_objects = ndimage.label(img<threshold) 
                
    return labeled, nr_objects   
                   

# ### get_bboxes
# 
# This function gets the bounding boxes to cut each character correctly given the labels obtained from get_labels. It returns a list of each character's bounding boxes (2 2D points).


# In[ ]:

def get_bboxes(labeled, nr_objects):
    bboxes = np.zeros((nr_objects, 2, 2), dtype='int')

    x1, y1, x2, y2 = 0, labeled.shape[0], 0, 0
    coord = 0
    cont = 0
    ytop, ybot = 0, 0
    nzero, firstb = False, False

    for x in range(0, labeled.shape[1]):
        nzero, firstb = False, False
        ytop, ybot = 0, 0
        for y in range(0, labeled.shape[0]):
            if (labeled[y][x] > 0):
                nzero = True
                if (not firstb):
                    ytop = y
                    firstb = True
                ybot = y

        if (nzero):
            if (ytop < y1):
                y1 = ytop
            if (ybot > y2):
                y2 = ybot
            if (coord == 0):
                x1 = x
                coord = 1
            elif (coord == 1):
                x2 = x
        elif ((not nzero) and (coord == 1)):
            bboxes[cont][0] = [x1, y1]
            bboxes[cont][1] = [x2, y2]
            cont += 1
            coord = 0
            x1, y1, x2, y2 = 0, labeled.shape[0], 0, 0

    bboxes = bboxes[0:cont]
    return bboxes, cont


# ### crop_characters
# 
# Given an image and character bounding boxes this function crops each character in an image and returns each character's corresponding binarized image in a list.

# In[ ]:

def crop_characters(img, bboxes, n):
    characters = []
    for i in range(0, n):
        c = img.copy()[bboxes[i][0][1]:bboxes[i][1][1], bboxes[i][0][0]:bboxes[i][1][0]]
        if (c.shape[0] != 0 and c.shape[1] != 0):
            c = resize(c, (28, 28), mode='constant', cval=1.0, clip=True)
            characters.append((c<0.80).reshape(784))
    return characters, len(characters)


# ### labelsep
# 
# Separates a full name label into a character list. Useful for the training part to have the labels of each character.

# In[ ]:


