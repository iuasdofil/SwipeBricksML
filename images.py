import os
import numpy as np
from PIL import Image
import cv2
import ocr
import math
import utils
import shlex
import subprocess
import time

class Images(object):
    def __init__(self, rootPath):
        self.__rootPath = rootPath
        self.__heights = [364, 444, 524, 604, 684, 764, 844]
        self.__widths = [4, 124, 244, 364, 484, 604]
        self.__mid_h = [399, 479, 559, 639, 719, 799, 879]
        self.__mid_w = [59, 179, 299, 419, 539, 659]
        self.__round_h = 70
        self.__round_w = 405
        self.__widthSize = 115
        self.__heightSize = 75
        self.__OCR = ocr.OCR()
        self.__state = np.zeros((7, 6), dtype=np.int)
        self.__prevState = np.zeros((7, 6), dtype=np.int)
        self.__gameRound = 0
        self.__util = utils.Utils(rootPath)

    def restart(self):
        print("restart")
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
    
        kill = "nox_adb shell kill %d" % pid
        start = "nox_adb shell am start -a android.intent.action.MAIN -n %s/%s" % (app, name)
    
        os.system(kill)
        time.sleep(6)
        os.system("nox_adb shell input tap %d %d" % (300, 715))
        # restart game with game guardian
        # os.system(start)
    
        time.sleep(5)
        os.system("nox_adb shell input tap %d %d" % (x, y))  # touch replay game
    
        time.sleep(2)
        os.system("nox_adb shell input swipe 200 180 220 180 4000")  # long pree 4sec
        
        # long press game guardian icon
    
        print("game speed")
        os.system("nox_adb shell input tap 385 180")  # game speed 1.2
        os.system("nox_adb shell input tap 385 180")  # game speed 1.3
        os.system("nox_adb shell input tap 385 180")  # game speed 1.5
        os.system("nox_adb shell input tap 385 180")  # game speed 2
        os.system("nox_adb shell input tap 385 180")  # game speed 3
        os.system("nox_adb shell input tap 385 180")  # game speed 4
        os.system("nox_adb shell input tap 385 180")  # game speed 5
        os.system("nox_adb shell input tap 385 180")  # game speed 6
        os.system("nox_adb shell input tap 385 180")  # game speed 9
        os.system("nox_adb shell input tap 385 180")  # game speed 12
        
        self.__gameRound = 0
        self.__state = np.zeros((7, 6), dtype=np.int)
        self.__prevState = np.zeros((7, 6), dtype=np.int)
        
    def initState(self):
        imgPath = self.__util.screenshot()
        
        self.getRound()
        self.cropBricks(imgPath)
        self.getGreenBall(imgPath)
        xPosition, ballNumber = self.findBlueBall(imgPath)
        
        ret = sum(self.__state.tolist(), [])
        ret.append(self.__gameRound)
        ret.append(xPosition)
        ret.append(ballNumber)
        
        return ret
    
    def action(self, degree):
        x = 360
        y = 985
        r = 200

        rx = x + (r * math.cos(math.radians(degree)))
        ry = y - (r * math.sin(math.radians(degree)))

        os.system("nox_adb shell input swipe %d %d %d %d 250" % (x, y, rx, ry))
        
        self.__prevState = np.copy(self.__state)
        
        # return next_state, reward, done, _
        
        if not self.getRound():
            ret = sum(self.__state.tolist(), [])
            ret.append(self.__gameRound)
            ret.append(-100)
            ret.append(-100)
            
            return ret, -100, True
        
        imgPath = self.__util.screenshot()
        self.cropBricks(imgPath)
        self.getGreenBall(imgPath)
        xPosition, ballNumber = self.findBlueBall(imgPath)
        
        ret = sum(self.__state.tolist(), [])
        ret.append(self.__gameRound)
        ret.append(xPosition)
        ret.append(ballNumber)
        
        return ret, self.getReward(), False
    
    def getRound(self):
        while True:
            img = Image.open(self.__util.screenshot())
            box = (self.__round_w, self.__round_h, self.__round_w + 70, self.__round_h + 40)
            region = img.crop(box)
            roundImg = "%s/croppedImages/round.png" % self.__rootPath
            region.save(roundImg)
            img.close()
            
            gameRound = self.getNumber(roundImg)
            if self.__gameRound < gameRound:
                self.__gameRound = gameRound
                return True
            elif gameRound == -100:
                return False
    
    def getReward(self):
        reward = 0
        
        for cRow, pRow in zip(self.__state[1:], self.__prevState[:-1]):
            for current, prev in zip(cRow, pRow):
                if prev >= 0:
                    reward += (prev - current)
                elif prev == -1 and current == 0:
                    reward += 1

        return reward
    
    def cropBricks(self, imgPath):
        img = Image.open(imgPath)
        rgb = img.convert("RGB")
        rgb = np.array(rgb, np.uint8)
        rgb = np.reshape(rgb, (1280, -1, 3))
        self.__state.fill(0)
        
        for i, height in enumerate(self.__heights):
            for j, width in enumerate(self.__widths):
                r, g, b = rgb[height][width]
                
                if r == 230 and g == 230 and b == 230:
                    continue
                else:
                    box = (width, height, width+self.__widthSize, height+self.__heightSize)
                    region = img.crop(box)
                    cropPath = "%s/croppedImages/cropImg[%d][%d].png" % (self.__rootPath, i, j)
                    region.save(cropPath)
                    self.__state[i][j] = self.getNumber(cropPath)
                    
        img.close()
    
    def getGreenBall(self, imgPath):
        img = Image.open(imgPath)
        rgb = img.convert("RGB")
        rgb = np.array(rgb, np.uint8)
        rgb = np.reshape(rgb, (1280, -1, 3))
        
        for i, height in enumerate(self.__mid_h):
            for j, width in enumerate(self.__mid_w):
                r, g, b = rgb[height][width]
                
                if(55 < r and r < 60) and (210 < g and g < 215) and (95 < b and b < 100):
                    self.__state[i][j] = -1

    def findBlueBall(self, imgPath):
        img = Image.open(imgPath)
        rgb = img.convert("RGB")
        rgb = np.array(rgb, np.uint8)
        rgb = np.reshape(rgb, (1280, -1, 3))
        
        for x in range(719):
            r, g, b = rgb[985][x]
            
            if r != 230 or g != 230 or b != 230:
                blueBall = x + 14
                height = 985 + 35
                width = x + 14 - 45
                
                box = (0, 1020, 720, 1055)
                region = img.crop(box)
                
                srcPath = "%s/croppedImages/ballNumber.png" % (self.__rootPath)
                region.save(srcPath)
                ballNumber = self.getNumber(srcPath)
                break
        
        img.close()
        return blueBall, ballNumber
    
    def getNumber(self, imgPath):
        im = cv2.imread(imgPath)
        im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(im, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)

        _, contours, hierarchy = cv2.findContours(thresh,
                                                  cv2.RETR_LIST,
                                                  cv2.CHAIN_APPROX_SIMPLE)
        
        numFiles = []
        
        for cnt in contours:
            if cv2.contourArea(cnt) > 50:
                [x, y, w, h] = cv2.boundingRect(cnt)
                
                if 24 < h and h < 36 and w > 5:
                    number = self.cropNumber(im, x, y, w, h)
                    numFiles.append(number)
                    
        if numFiles == []:
            return -100
        
        return self.__OCR.predict(numFiles)

    def cropNumber(self, im, x, y, w, h):
        crop = im[y:y + h, x:x + w]
        length = len(os.listdir("croppedImages"))
        filename = "croppedImages/num_%d.png" % length
        cv2.imwrite(filename, crop)
    
        return filename
