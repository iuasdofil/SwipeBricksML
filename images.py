import os
import numpy as np
from PIL import Image
import cv2
import ocr
import math

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
        self.__state = np.zeros((7, 6))
        self.__prevState = np.zeros((7, 6))
        self.__gameRound = 0
        
    def getReward(self):
        reward = 0
        
        for cRow, pRow in zip(self.__state[1:], self.__prevState[:-1]):
            for current, prev in zip(cRow, pRow):
                if prev >= 0:
                    reward += (prev - current)
                elif prev == -1 and current == 0:
                    reward += 1

        return reward
        
    def action(self, degree):
        x = 360
        y = 985
        r = 200
        
        rx = x + (r * math.cos(math.radians(degree)))
        ry = y - (r * math.sin(math.radians(degree)))
        
        os.system("nox_adb shell input swipe %d %d %d %d 250" % (x, y, rx, ry))
        
        self.__prevState = np.copy(self.__state)

    def getGameState(self, filename):
        self.__gameRound = self.getRound(filename)
        
        if self.__gameRound == -100:
            return -100, -100, -100, -100
            
        self.cropBricks(filename)
        self.getGreenBall(filename)
        xPosition, ballNumber = self.findBlueBall(filename)
    
        return self.__state, self.__gameRound, xPosition, ballNumber
    
    def cropBricks(self, filename):
        img = Image.open(filename)
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
    
    def getGreenBall(self, filename):
        img = Image.open(filename)
        rgb = img.convert("RGB")
        rgb = np.array(rgb, np.uint8)
        rgb = np.reshape(rgb, (1280, -1, 3))
        
        for i, height in enumerate(self.__mid_h):
            for j, width in enumerate(self.__mid_w):
                r, g, b = rgb[height][width]
                
                if(55 < r and r < 60) and (210 < g and g < 215) and (95 < b and b < 100):
                    self.__state[i][j] = -1
        
    def getRound(self, filename):
        img = Image.open(filename)
        box = (self.__round_w, self.__round_h, self.__round_w + 70, self.__round_h + 40)
        region = img.crop(box)
        roundImg = "%s/croppedImages/round.png" % self.__rootPath
        region.save(roundImg)
        img.close()

        return self.getNumber(roundImg)

    def findBlueBall(self, filename):
        img = Image.open(filename)
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
    
    def getNumber(self, filename):
        im = cv2.imread(filename)
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
            print("game over")
            return -100
        
        return self.__OCR.predict(numFiles)

    def cropNumber(self, im, x, y, w, h):
        crop = im[y:y + h, x:x + w]
        length = len(os.listdir("croppedImages"))
        filename = "croppedImages/num_%d.png" % length
        cv2.imwrite(filename, crop)
    
        return filename
