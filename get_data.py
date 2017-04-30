import os, sys
import numpy as np
from PIL import Image
import cv2
from sklearn.externals import joblib
from skimage.feature import hog
import shutil

def screenshot():
	files = os.listdir(os.getcwd() + "/screenshot")
	
	count = 0
	for file in files:
		if file.startswith("screenshot") and file.endswith("png"):
			count += 1
	
	filename = "screenshot_%04d.png"%(count+1)
	
	os.system("adb shell screencap -p /data/local/tmp/"+filename)
	os.system("adb pull /data/local/tmp/"+filename)
	
	shutil.move(filename, "/mnt/hgfs/SwipeBricksML/screenshot/"+filename)
	# os.rename(filename, "/mnt/hgfs/SwipeBricksML/screenshot/"+filename)
	
	print filename
	return "/mnt/hgfs/SwipeBricksML/screenshot/"+filename
	
	
def deleteFile():
	cwd = os.getcwd()
	
	os.chdir("/mnt/hgfs/SwipeBricksML/crop_image")
	files = os.listdir(os.getcwd())
	
	for file in files:
		os.remove(file)
	
	os.chdir(cwd)

def getPixel(filename):
	heights = [364, 444, 524, 604, 684, 764, 844]
	widths = [4, 124, 244, 364, 484, 604]

	mid_h = [399, 479, 559, 639, 719, 799, 879]
	mid_w = [59, 246, 299, 419, 539, 659]

	width_size = 115
	height_size = 75
	
	img = Image.open(filename)
	rgb = img.convert("RGB")
	rgb = np.array(rgb, np.uint8)
	rgb = np.reshape(rgb, (1280, -1, 3))
	
	arr = np.zeros((7, 6))
	
	for i, height in enumerate(heights):
		for j, width in enumerate(widths):
			r, g, b = rgb[height][width]
			
			if r == 230 and g == 230 and b == 230:
				arr[i][j] = 0
			else:
				box = (width, height, width + width_size, height + height_size)
				region = img.crop(box)
				region.save("crop_image/crop_img[%d][%d].png"%(i, j))
				shutil.move("crop_image/crop_img[%d][%d].png"%(i, j), 
					"/mnt/hgfs/SwipeBricksML/crop_image/crop_img[%d][%d].png"%(i, j))
				
				arr[i][j] = 1
				
			r, g, b = rgb[mid_h[i]][mid_w[j]]
			
			if r == 58 and g == 211 and b == 97:
				arr[i][j] = -1
				
	print "Box and ball position"
	for i in range(len(heights)):
		str = ""
		for j in range(len(widths)):
			str += "%02d "%arr[i][j]
			
		print str
	
def ocr(filename):
	im = cv2.imread(filename)
	im3 = im.copy()
	
	gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
	blur = cv2.GaussianBlur(gray, (5, 5), 0)
	thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)
	
	contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, 
		cv2.CHAIN_APPROX_SIMPLE)
		
	samples = np.empty((0, 100))
	responses = []
	keys = [i for i in range(48, 58)]
	
	for cnt in contours:
		if cv2.contourArea(cnt)>50:
			[x, y, w, h] = cv2.boundingRect(cnt)
			
			# if h > 28:
			# if h > 31:
			if 28 < h and h < 36:
				saveTrainingData(im, x, y, w, h)
				cv2.rectangle(im, (x, y), (x+w, y+h), (0, 0, 255), 2)
				roi = thresh[y:y+h, x:x+w]
				roismall = cv2.resize(roi, (10, 10))
				# cv2.imshow("norm", im)
				# key = cv2.waitKey(0)
			
			
def saveTrainingData(im, x, y, w, h):
	crop = im[y:y+h, x:x+w]
	
	with open("/mnt/hgfs/TrainingData/num.txt", 'r') as file:
		lines = file.readlines()
	
	cv2.imwrite("/mnt/hgfs/TrainingData/Training_%04d.png"%int(lines[0]), crop)
	
	with open("/mnt/hgfs/TrainingData/num.txt", 'w') as file:
		file.write("%d\n"%(int(lines[0]) + 1))
		file.write("%d"%int(lines[1]))

def main():
	filename = screenshot()
	deleteFile()
	getPixel(filename)
	
	files = os.listdir("/mnt/hgfs/SwipeBricksML/crop_image/")
	
	for file in files:
		ocr("/mnt/hgfs/SwipeBricksML/crop_image/" + file)

if __name__ == "__main__":
	main()