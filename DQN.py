import tensorflow as tf
import numpy as np


class DQN:
    def __init__(self, session, name="main"):
        self.__session = session
        self.__name = name
        self.__inputSize = 45
        self.__outputSize = 161

        self.buildNetwork()

    def buildNetwork(self, hiddenSize=50, learningRate=1e-1):
        with tf.variable_scope(self.__name):
            self.__X = tf.placeholder(tf.float32, [None, self.__inputSize], name="inputX")
            w1 = tf.get_variable("W1", shape=[self.__inputSize, hiddenSize],
                                 initializer=tf.contrib.layers.xavier_initializer())
            b1 = tf.Variable(tf.random_uniform([hiddenSize]))
            layer1 = tf.nn.tanh(tf.matmul(self.__X, w1) + b1)

            w2 = tf.get_variable("W2", shape=[hiddenSize, hiddenSize],
                                 initializer=tf.contrib.layers.xavier_initializer())
            b2 = tf.Variable(tf.random_uniform([hiddenSize]))
            layer2 = tf.nn.tanh(tf.matmul(layer1, w2) + b2)

            w3 = tf.get_variable("W3", shape=[hiddenSize, self.__outputSize],
                                 initializer=tf.contrib.layers.xavier_initializer())
            b3 = tf.Variable(tf.random_uniform([self.__outputSize]))
            self.__Qpred = tf.matmul(layer2, w3) + b3

        self.__Y = tf.placeholder(shape=[None, self.__outputSize], dtype=tf.float32)
        self.__loss = tf.reduce_mean(tf.square(self.__Y - self.__Qpred))
        self.__train = tf.train.AdamOptimizer(learning_rate=learningRate).minimize(self.__loss)

    def predict(self, state):
        x = np.reshape(state, [1, self.__inputSize])
        return self.__session.run(self.__Qpred, feed_dict={self.__X: x})

    def update(self, xStack, yStack):
        return self.__session.run([self.__loss, self.__train], feed_dict={self.__X: xStack, self.__Y: yStack})