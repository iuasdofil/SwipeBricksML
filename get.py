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
    util = utils.Utils(os.getcwd())
    env = images.Images(os.getcwd())
    maxEpisode = 5000
    
    replayBuffer = deque()
    
    with tf.Session() as sess:
        mainDQN = DQN.DQN(sess, "main")
        tf.global_variables_initializer().run()
        
        for episode in range(maxEpisode):
            e = 1. / ((episode / 10) + 1)
            done = False
            stepCount = 0
            
            gameRound = 1
            prev = 0
            
            while not done:
                util.deleteFile()
                imgPath = util.screenshot()
                state, gameRound, xPosition, ballNumber = env.getGameState(imgPath)
                
                if prev == gameRound:
                    continue
                elif gameRound == -100:
                    done = True
                
                prev = gameRound
                
                if np.random.rand(1) < e:
                    action = random.randrange(10, 170)
                else:
                    action = np.argmax(mainDQN.predict(state)) + 10
                
                print("action : %d" % action)
                env.action(action)
                time.sleep(30)
                
                
                
            print("Episode : {} steps : {}".format(episode, stepCount))
            if stepCount > 10000:
                pass
            if episode % 10 == 1:
                for _ in range(50):
                    miniBatch = random.sample(replayBuffer, 10)
                    loss, _ = simpleReplayTrain(mainDQN, miniBatch)
                print("Loss :", loss)

if __name__ == "__main__":
    main()
