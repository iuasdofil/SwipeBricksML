import os
import numpy as np
from PIL import Image
import cv2
import ocr

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

    def getGameStatus(self, filename):
        status = np.zeros((7, 6))
        gameRound = 0
        
        self.cropBricks(filename, status)
        self.getGreenBall(filename, status)
        gameRound = self.getRound(filename)
        xPosition, ballNumber = self.findBlueBall(filename)
    
        return status, gameRound, xPosition, ballNumber
    
    def cropBricks(self, filename, status):
        img = Image.open(filename)
        rgb = img.convert("RGB")
        rgb = np.array(rgb, np.uint8)
        rgb = np.reshape(rgb, (1280, -1, 3))
        
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
                    status[i][j] = self.getNumber(cropPath)
                    
        img.close()
    
    def getGreenBall(self, filename, status):
        img = Image.open(filename)
        rgb = img.convert("RGB")
        rgb = np.array(rgb, np.uint8)
        rgb = np.reshape(rgb, (1280, -1, 3))
        
        for i, height in enumerate(self.__mid_h):
            for j, width in enumerate(self.__mid_w):
                r, g, b = rgb[height][width]
                
                if(55 < r and r < 60) and (210 < g and g < 215) and (95 < b and b < 100):
                    status[i][j] = -1
        
        return status
        
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
