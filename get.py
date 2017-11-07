import os
import utils
import images
import time
import numpy as np
import DQN
from collections import deque
import tensorflow as tf
import random

dis = 0.9
REPLAY_MEMORY = 50000

def simpleReplayTrain(DQN, trainBatch):
    xStack = np.empty(0).reshape(0, DQN.__inputSize)
    yStack = np.empty(0).reshape(0, DQN.__outputSize)
    
    for state, action, reward, nextState, done in trainBatch:
        Q = DQN.predict(state)
        
        if done:
            Q[0, action] = reward
        else:
            Q[0, action] = reward + dis * np.max(DQN.predict(nextState))
        
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
        
        for episode in range(maxEpisode):
            e = 1. / ((episode / 10) + 1)
            done = False
            stepCounter = 0
            env.restart()
            state = env.initState()
            print("episode : %d" % episode)
            
            while not done:
                if np.random.rand(1) < e:
                    degree = random.randrange(10, 170)
                else:
                    degree = mainDQN.predict(state)[0] + 10
            
                print("degree : %d" % degree)
                nextState, reward, done = env.action(degree)
                if done:
                    reward = -100
                
                replayBuffer.append((state, degree, reward, nextState, done))
                if len(replayBuffer) > REPLAY_MEMORY:
                    replayBuffer.popleft()
                    
                state = nextState
                stepCounter += 1
            
        print("Episode : {} steps : {}".format(episode, stepCounter))
        if stepCounter > 10000:
            pass
        
        if episode % 10 == 1:
            for _ in range(50):
                miniBatch = random.sample(replayBuffer, 10)
                loss, _ = simpleReplayTrain(mainDQN, miniBatch)
            print("Loss : {}".foramt(loss))
    
    

if __name__ == "__main__":
    main()
