import os, sys
import numpy as np
from PIL import Image
import cv2
import shutil
import tensorflow as tf
import digit_predict
import blue_predict
import degree_predict
import math
import random, time
import subprocess, shlex
import socket, pickle
import copy

print("first")
digit_prediction = digit_predict.digit_predict()
digit_prediction.start()

# print("second")
# blue_prediction = blue_predict.blue_predict()
# blue_prediction.start()

# print("third")
# degree_prediction = degree_predict.degree_predict()
# degree_prediction.start()
# print("after")

def screenshot():
	files = os.listdir(os.getcwd() + "/screenshot")
	
	count = 0
	for file in files:
		if file.startswith("screenshot") and file.endswith("png"):
			count += 1
	
	filename = "screenshot_%04d.png"%(count)
	
	os.system("nox_adb shell screencap -p /data/local/tmp/"+filename)
	os.system("nox_adb pull /data/local/tmp/"+filename)
	
	os.rename(filename, "./screenshot/"+filename)
	print(filename)
	return os.getcwd() + "/screenshot/" + filename
	
def deleteFile():
	cwd = os.getcwd()
	os.chdir("crop_image")
	files = os.listdir(os.getcwd())
	
	for file in files:
		os.remove(file)
	
	os.chdir(cwd)
	
def getPosition(filename):
	heights = [364, 444, 524, 604, 684, 764, 844]
	widths = [4, 124, 244, 364, 484, 604]

	mid_h = [399, 479, 559, 639, 719, 799, 879]
	mid_w = [59, 246, 299, 419, 539, 659]
	
	round_h = 70
	round_w = 405

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
				crop_path = os.getcwd() + "/crop_image/crop_img[%d][%d].png"%(i, j)
				
				region.save("crop_image/crop_img[%d][%d].png"%(i, j))
				
				num = digit_ocr(crop_path, 0)
				if num == -100:
					return None, None, None
					
				arr[i][j] = num
				
			r, g, b = rgb[mid_h[i]][mid_w[j]]
			
			# find green ball
			if (55 < r and r < 60) and (210 < g and g < 215) and (95 < b and b < 100):
				arr[i][j] = -1
	
	blue_ball = 0
	
	for x in range(719):
		r, g, b = rgb[985][x]
		
		if r != 230 or g != 230 or b != 230:
			blue_ball = x + 14
			height = 985 + 35
			width = x + 14 - 45
			
			box = (0, 1020, 720, 1055)
			region = img.crop(box)
			
			src_path = "crop_image/ball_number.png"
			region.save(src_path)
		
			ball_num = digit_ocr(src_path, 1)
			break
	
	box = (round_w, round_h, round_w + 70, round_h + 40)
	region = img.crop(box)
	crop_path = os.getcwd() + "/crop_image/round.png"
	region.save(crop_path)
	
	num = digit_ocr(crop_path, 1)
	print("round : %d"%num)
	
	img.close()
	return arr, ball_num, blue_ball

def digit_ocr(filename, mode):
	im = cv2.imread(filename)
	im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
	blur = cv2.GaussianBlur(im, (5, 5), 0)
	thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)
	
	_, contours, hierarchy = cv2.findContours(thresh, 
		cv2.RETR_LIST, 
		cv2.CHAIN_APPROX_SIMPLE)
		
	samples = np.empty((0, 100))
	keys = [i for i in range(48, 58)]
	num = 0
	number_files = []
	
	for cnt in contours:
		if cv2.contourArea(cnt) > 50:
			[x, y, w, h] = cv2.boundingRect(cnt)
			
			if 24 < h and h < 36 and w > 5:
				num_file = crop_number(im, x, y, w, h)
				number_files.append(num_file)
				
	if number_files == []:
		print("game over")
		return -100
	
	if mode == 0:
		num = digit_prediction.predict(number_files)
		# num = digit_predict.digit_predict(number_files)
	else:
		num = digit_prediction.predict(number_files)
		# num = blue_predict.digit_predict(number_files)
	
	return num
	
def crop_number(im, x, y, w, h):
	crop = im[y:y+h, x:x+w]
	
	with open("TrainingData/num.txt", 'r') as file:
		lines = file.readlines()
	
	filename = "TrainingData/Training_%04d.png"%int(lines[0])
	cv2.imwrite(filename, crop)	
	
	with open("TrainingData/num.txt", 'w') as file:
		file.write("%d\n"%(int(lines[0]) + 1))
		file.write("%d"%int(lines[1]))
	
	return filename
	
def swipeball(degree):
	x = 360
	y = 985
	r = 200
	
	rx = x + (r * math.cos(math.radians(degree)))
	ry = y - (r * math.sin(math.radians(degree)))
	
	os.system("nox_adb shell input swipe %d %d %d %d 250"%(x, y, rx, ry))
	
def restart():
	x = 460
	y = 900
	
	name = "com.unity3d.player.UnityPlayerNativeActivity"
	app = "com.Monthly23.SwipeBrickBreaker"
	
	args = shlex.split("nox_adb shell ps")
	lines = subprocess.getoutput(args).split("\n")
	pid = 0
	
	for line in lines:
		if line.find("SwipeBrickBreaker") >= 0:
			term = line.split()
			pid = int(term[1])

	kill = "nox_adb shell kill %d"%pid
	start = "nox_adb shell am start -a android.intent.action.MAIN -n %s/%s"%(app, name)
	
	os.system(kill)
	time.sleep(3)
	os.system(start)
	
	time.sleep(8)
	os.system("nox_adb shell input tap %d %d"%(x, y))
	
def save_data(position, ball_num, blue_ball, round, degree):
	with open("raw_data.csv", 'a') as file:
		for i in range(7):
			for j in range(6):
				file.write("%d,"%position[i][j])
		
		file.write("%d,"%blue_ball)	# x coordinate
		file.write("%d,"%ball_num)	# number of ball
		file.write("%d,"%round)		# round
		file.write("%d\n"%degree)	# degree
		
def get_degree(position, blue_ball, ball_num):
	x_data = []
	max = [0, 0]
	HOST, PORT = "localhost", 2000
	
	address = ('localhost', 2000)
	
	
	for i in range(7):
		for j in range(6):
			x_data.append(position[i][j])
	
	x_data.append(blue_ball)
	x_data.append(ball_num)
	
	
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
		sock.connect((HOST, PORT))
		sock.sendall(pickle.dumps(x_data))
		predict = pickle.loads(sock.recv(40960))
		
	print(predict)
	print(len(predict))
	
	idx = 0
	max = 0
	
	for i, item in enumerate(predict):
		if item > max:
			max = item
			idx = i
	
	idx += 10
	print("max : %d, degree : %d"%(max, idx))
	
	return idx
	
	
	# for degree in range(10, 171):
		# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
			# sock.connect((HOST, PORT))
			# x = copy.deepcopy(origin)
			# x.append(degree)
			# x_data.append(degree)
			# data_string = pickle.dumps(x_data)
			
			# sock.sendall(data_string)
			# data = sock.recv(4096)
			# predict = pickle.loads(data)
			
			# x_data.pop()
		
		# if predict[0] > max[0]:
			# max[0] = predict[0]
			# max[1] = degree
		
	# return max[1]

def main(round):
	filename = screenshot()
	deleteFile()
	position, ball_num, blue_ball = getPosition(filename)
	
	if position is None and ball_num is None and blue_ball is None:
		print("game over")
		restart()
		return -1
	
	print("Box and green ball position")
	for i in range(7):
		str = ""
		for j in range(6):
			str += "%03d "%position[i][j]
			
		print(str)
	print("ball X:",blue_ball, "num:",ball_num)
	
	degree = get_degree(position, blue_ball, ball_num)
	# degree = random.randint(10, 170)
	print("degree", degree)
	swipeball(degree)
	save_data(position, ball_num, blue_ball, round, degree)
	
	return 1
	
if __name__ == "__main__":
	round = 1
	while True:
		num = main(round)
		time.sleep(15)
		if num == -1:
			round = 1
			continue
			
		round += num
		