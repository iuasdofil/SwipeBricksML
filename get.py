import os
import images
import numpy as np
import DQN
from collections import deque
import tensorflow as tf
import random
import requests
import json
import time

dis = 0.9
REPLAY_MEMORY = 50000


def simpleReplayTrain(DQN, trainBatch):
    xStack = np.empty(0).reshape(0, 45)
    yStack = np.empty(0).reshape(0, 161)

    for state, action, reward, nextState, done in trainBatch:
        Q = DQN.predict(state)

        if not done:
            Q[0, action - 10] = reward
        else:
            Q[0, action - 10] = reward + dis * np.argmax(DQN.predict(nextState))

        xStack = np.vstack([xStack, state])
        yStack = np.vstack([yStack, Q])

    return DQN.update(xStack, yStack)


def main():
    env = images.Images(os.getcwd())
    maxEpisode = 5000
    replayBuffer = deque()

    with tf.Session() as sess:
        mainDQN = DQN.DQN(sess)
        tf.global_variables_initializer().run()
        saver = tf.train.Saver()

        for episode in range(maxEpisode):
            e = 1. / ((episode / 10) + 1)
            done = False
            stepCounter = 0
            env.restart()
            state = env.initState()
            print("episode : %d" % episode)

            while not done:
                if np.random.rand(1) < e:
                    action = random.randrange(10, 170)
                    print("Episode : %d random degree : %d" % (episode, action))
                else:
                    action = mainDQN.predict(state)[0]
                    action = np.argmax(action) + 10
                    print("Episode : %d predict degree : %d" % (episode, action))
                    # action.index(max(action)) + 10

                nextState, reward, done = env.action(action)
                if done:
                    reward = -100

                replayBuffer.append((state, action, reward, nextState, done))
                print("next State length : %d" % len(nextState))

                # URL = "http://192.168.190.130:8000/"
                URL = "http://35.200.208.151/"
                current_state = ",".join(map(str, state[:42]))
                next_state = ",".join(map(str, nextState[:42]))
                round = nextState[42]
                ball_position = nextState[43]
                ball_number = nextState[44]

                print("------------------------------------------------------------")
                print("current_state : %s" % type(current_state))
                print("next_state : %s" % type(next_state))
                print("round : %s" % type(round))
                print("ball_position : %s" % type(ball_position))
                print("action : %s" % type(action))
                print("done : %s" % type(done))

                requests.post(URL, data=json.dumps({"current_state" : current_state, "next_state" : next_state,
                                                    "round" : int(round), "ball_position" : ball_position,
                                                    "ball_number" : int(ball_number),
                                                    "action" : int(action),
                                                    "done" : done }))

                if len(replayBuffer) > REPLAY_MEMORY:
                    replayBuffer.popleft()

                state = nextState
                stepCounter += 1

            print("Episode : {} steps : {}".format(episode, stepCounter))

            if episode % 10 == 2:
                for _ in range(50):
                    miniBatch = random.sample(replayBuffer, 10)
                    loss, _ = simpleReplayTrain(mainDQN, miniBatch)
                print("Loss :", loss)
                saver.save(sess, "./save/DQN/model")


if __name__ == "__main__":
    main()
