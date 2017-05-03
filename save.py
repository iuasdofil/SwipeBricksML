import tensorflow as tf
import numpy as np

def one_hot(y_data, dimension):
	one_hot = []
	
	for y in y_data:
		dim = [0.0 for i in range(dimension)]
		dim[int(y[0])] = 1.0
		one_hot.append(dim)
		
	return one_hot

def main():
	xy = np.loadtxt("/mnt/hgfs/SwipeBricksML/labeling/TrainingData_noPathNP.csv", 
		delimiter=',')
		
	x_data = xy[:, :-1]
	y_data = xy[:, [-1]]
	y_data = one_hot(y_data, 10)
	keep_prob = tf.placeholder(tf.float32)
	
	xy = np.loadtxt("/mnt/hgfs/SwipeBricksML/labeling/TestData_noPathNP.csv", 
		delimiter=',')
		
	x_test = xy[:, :-1]
	y_test = xy[:, [-1]]
	y_test = one_hot(y_test, 10)
	
	X = tf.placeholder(tf.float32, [None, 768])
	Y = tf.placeholder(tf.float32, [None, 10])
	
	w1 = tf.get_variable('w1', shape=[768, 614],
		initializer = tf.contrib.layers.xavier_initializer())
	b1 = tf.Variable(tf.random_uniform([614]))
	L1 = tf.nn.relu(tf.matmul(X, w1) + b1)
	L1 = tf.nn.dropout(L1, keep_prob = keep_prob)

	w2 = tf.get_variable('w2', shape=[614, 10],
		initializer = tf.contrib.layers.xavier_initializer())
	b2 = tf.Variable(tf.random_uniform([10]))
	hypothesis = tf.matmul(L1, w2) +b2
	
	tf.add_to_collection('hypo', hypothesis)
	tf.add_to_collection('input', X)
	tf.add_to_collection('input', Y)
	tf.add_to_collection('input', keep_prob)
	
	tf.add_to_collection('vars', w1)
	tf.add_to_collection('vars', b1)
	
	
	cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(
		logits = hypothesis, labels=Y))
	optimizer = tf.train.AdamOptimizer(learning_rate=0.001).minimize(cost)
	
	sess = tf.Session()
	sess.run(tf.global_variables_initializer())
	saver = tf.train.Saver()
	
	print("learning start")
	for step in range(2000):
		if step % 100 == 0:
			print(step)
		feed_dict = {X:x_data, Y:y_data, keep_prob:0.7}
		sess.run([cost, optimizer], feed_dict=feed_dict)
	
	print("learning finished")
	
	
	saver.save(sess, "./save/digit_ocr/model")
	print("prediction")
	feed_dict = {X:x_test, keep_prob:1}
	predictions = sess.run(tf.argmax(hypothesis, 1), feed_dict=feed_dict)
	
	print(predictions)

if __name__ == "__main__":
	main()