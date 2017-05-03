import tensorflow as tf
import numpy as np
import cv2

def get_feature(number_files):
	csv = "/home/pw-1234/SwipeBricksML/temp.csv"
	
	with open(csv, 'w') as file:
		for filename in number_files:
			img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
			height, width = img.shape
			
			for y in range(height):
				for x in range(width):
					file.write("%d,"%img[y, x])
				for x in range(24-width):
					file.write("0,"%img[y, x])
					
			for y in range(32-height):
				for x in range(24):
					file.write("0,")
			file.write("0\n")

def digit_predict(number_files):
	get_feature(number_files)
	
	xy = np.loadtxt("/home/pw-1234/SwipeBricksML/temp.csv", delimiter=',')
	try:
		x_test = xy[:, :-1]
		y_test = xy[:, [-1]]
	except:
		x_test = xy[:-1]
		y_test = xy[-1]
		x_test = np.reshape(x_test, (-1, 768))
		
	# print(x_test.shape)
	
	sess = tf.Session()
	
	saver = tf.train.import_meta_graph('./save/digit_ocr/model.meta')
	print(tf.train.latest_checkpoint("./save/digit_ocr/"))
	
	saver.restore(sess, tf.train.latest_checkpoint("./save/digit_ocr"))
	
	hypothesis = tf.get_collection('hypo')[0]
	vars = tf.get_collection('vars')
	input_vars = tf.get_collection('input')
	
	X = input_vars[0]
	Y = input_vars[1]
	keep_prob = input_vars[2]
	
	feed_dict = {X:x_test, keep_prob:1}
	predictions = sess.run(tf.argmax(hypothesis, 1), feed_dict=feed_dict)
	
	num = 0
	idx = 1
	for predic in predictions:
		num += predic * idx
		idx *= 10
	
	return num
	

if __name__ == "__main__":
	main()
	
	
	