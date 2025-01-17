import tensorflow as tf
import numpy as np
import cv2


class OCR(object):
    def __init__(self):
        self.__sess = tf.Session()
        self.__saver = tf.train.import_meta_graph("./save/digit/model.meta")
        self.__saver.restore(self.__sess, tf.train.latest_checkpoint("./save/digit"))
        self.__hypothesis = tf.get_collection('hypo')[0]
        self.__input_vars = tf.get_collection('input')
        self.__X = self.__input_vars[0]
        self.__Y = self.__input_vars[1]
        self.__keep_prob = self.__input_vars[2]

    def predict(self, numberFiles):
        csv = "temp.csv"
        xData = []
        for filename in numberFiles:
            img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
            height, width = img.shape

            if height > 32:
                height = 32
            if width > 24:
                width = 24

            data = []
            for y in range(height):
                for x in range(width):
                    data.append(img[y, x])
                for x in range(24 - width):
                    data.append(0)
            for y in range(32 - height):
                for x in range(24):
                    data.append(0)

            xData.append(data)

        xData = np.array(xData)
        feed_dict = {self.__X: xData, self.__keep_prob: 1}

        predictions = self.__sess.run(tf.argmax(self.__hypothesis, 1), feed_dict=feed_dict)

        num = 0
        idx = 1

        for predic in predictions:
            num += predic * idx
            idx *= 10

        return num
