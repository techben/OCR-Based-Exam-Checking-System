# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 18:05:23 2018

@author: Areeba aftab
"""

from flask import Flask,render_template,request,session,redirect,url_for,send_from_directory,send_file
import sys
from flask_uploads import UploadSet,configure_uploads,TEXT
import _decimal

# import cdecimal
# from cdecimal import Decimal
from _decimal import Decimal

#import warnings
#warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
import gensim
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
from nltk.corpus import wordnet as wn
from os import path

import psycopg2
import fpdf
from fpdf import FPDF
from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
