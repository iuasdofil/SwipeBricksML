# Import the modules
import cv2
from sklearn.externals import joblib
from skimage.feature import hog
import numpy as np
import sys
import os

def ocr(filename):
	clf = joblib.load("digits_cls.pkl")
	
	im = cv2.bitwise_not(cv2.imread(filename))
	
	im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
	im_gray = cv2.GaussianBlur(im_gray, (5, 5), 0)
	
	ret, im_th = cv2.threshold(im_gray, 90, 255, cv2.THRESH_BINARY_INV)
	ctrs, hier = cv2.findContours(im_th.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	rects = [cv2.boundingRect(ctr) for ctr in ctrs]
		
	for rect in rects:
		crop = im[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
		files = os.listdir("/home/pw-1234/SwipeBricksML/TrainingData")
		# print files
		count = 0
		for file in files:
			if file.startswith("Training"):
				count += 1
		
		cv2.imwrite("TrainingData/Training_%04d.png"%count, crop)
		
		# Draw the rectangles
		cv2.rectangle(im, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (0, 255, 0), 3) 
		
		# Make the rectangular region around the digit
		leng = int(rect[3] * 1.6)
		pt1 = int(rect[1] + rect[3] // 2 - leng // 2)
		pt2 = int(rect[0] + rect[2] // 2 - leng // 2)
		roi = im_th[pt1:pt1+leng, pt2:pt2+leng]
		
		# Resize the image
		roi = cv2.resize(roi, (28, 28), interpolation=cv2.INTER_AREA)
		roi = cv2.dilate(roi, (3, 3))
		
		# Calculate the HOG features
		roi_hog_fd = hog(roi, orientations=9, pixels_per_cell=(14, 14), cells_per_block=(1, 1), visualise=False)
		
		nbr = clf.predict(np.array([roi_hog_fd], 'float64'))
	
	return nbr

if __name__ == "__main__":
	if len(sys.argv) == 2:
		ocr(sys.argv[1])
	elif len(sys.argv) == 1:
		files = os.listdir(os.getcwd() + "/crop_image")
		
		for file in files:
			print file
			ocr(os.getcwd() + "/crop_image/" + file)