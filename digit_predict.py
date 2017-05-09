import tensorflow as tf
import numpy as np
import cv2
import os
import threading

class digit_predict(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.__sess = tf.Session()
		self.__saver = tf.train.import_meta_graph("./save/digit_ocr/model.meta")
		self.__saver.restore(self.__sess, tf.train.latest_checkpoint("./save/digit_ocr"))
		self.__hypothesis = tf.get_collection('hypo')[0]
		self.__input_vars = tf.get_collection('input')
		self.__X = self.__input_vars[0]
		self.__Y = self.__input_vars[1]
		self.__keep_prob = self.__input_vars[2]
	
	def predict(self, number_files):
		csv = "temp.csv"
		
		with open(csv, 'w') as file:
			for filename in number_files:
				img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
				height, width = img.shape
				
				if height > 32:
					height = 32
				if width > 24:
					width = 24
				
				for y in range(height):
					for x in range(width):
						file.write("%d,"%img[y, x])
					for x in range(24-width):
						file.write("0,")
						
				for y in range(32-height):
					for x in range(24):
						file.write("0,")
				file.write("0\n")
				
		xy = np.loadtxt("temp.csv", delimiter=',')
		try:
			x_test = xy[:, :-1]
			y_test = xy[:, [-1]]
		except:
			x_test = xy[:-1]
			y_test = xy[-1]
			x_test = np.reshape(x_test, (-1, 768))
		
		feed_dict = {self.__X:x_test, self.__keep_prob:1}
		
		predictions = self.__sess.run(tf.argmax(self.__hypothesis, 1), feed_dict=feed_dict)
		
		num = 0
		idx = 1
		
		for predic in predictions:
			num += predic * idx
			idx *= 10
			
		return num
