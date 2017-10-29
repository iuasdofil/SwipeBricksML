import os
import utils
import images
import cv2

def main():
    util = utils.Utils(os.getcwd())
    image = images.Images(os.getcwd())
    
    util.deleteFile()
    
    imgPath = util.screenshot()
    status, gameRound, xPosition, ballNumber = image.getGameStatus(imgPath)
    
    print("screenshot Path : %s" % imgPath)
    print("gameRound : %d" % gameRound)
    print("ball Position : %d" % xPosition)
    print("ball number : %d" % ballNumber)
    print(status)
    
    

if __name__ == "__main__":
    main()
