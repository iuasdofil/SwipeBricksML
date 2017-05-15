import tensorflow as tf
import gc
import numpy as np
import socket, pickle
import copy

class degree_predict(object):
	def __init__(self):
		self.__sess = tf.Session()
		self.__saver = tf.train.import_meta_graph("D:/SwipeBricksML/save/bot_model2/bot.meta")
		self.__saver.restore(self.__sess, tf.train.latest_checkpoint("D:/SwipeBricksML/save/bot_model2"))
		self.__hypothesis = tf.get_collection('hypo')[0]
		self.__input_vars = tf.get_collection('input')
		self.__X = self.__input_vars[0]
		self.__Y = self.__input_vars[1]
		self.__keep_prob = self.__input_vars[2]
	
	def predict(self, x_data):
		# print(np.asarray(x_data))
		feed_dict = {self.__X:x_data, self.__keep_prob:1}
		
		predictions = self.__sess.run(tf.argmax(self.__hypothesis, 1), feed_dict=feed_dict)
		
		return predictions

def main():
	HOST, PORT = "localhost", 2000
	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen(10)
	
	angle = degree_predict()
	
	while True:
		conn, addr = s.accept()
		x_data =[]
		origin = pickle.loads(conn.recv(40960))
		
		for degree in range(10, 171):
			x = copy.deepcopy(origin)
			x.append(degree)
			x_data.append(x)
			
		degree = angle.predict(x_data)
		conn.send(pickle.dumps(degree))
		conn.close()
	
	
	
	# server = socketserver.TCPServer((HOST, PORT), DegreeML)
	# print("start serve_forever")
	# server.serve_forever()
	
	
if __name__ == "__main__":
	main()
