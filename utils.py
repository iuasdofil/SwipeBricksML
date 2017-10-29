import os


class Utils(object):
    def __init__(self, rootPath):
        self.__rootPath = rootPath
        print(self.__rootPath)
        
    def screenshot(self):
        os.system("nox_adb shell screencap -p /data/local/tmp/screenshot.png")
        os.system("nox_adb pull /data/local/tmp/screenshot.png")
        os.rename("screenshot.png", "./screenshot/screenshot.png")
        filePath = "%s/screenshot/screenshot.png" % self.__rootPath
        
        return filePath
    
    def deleteFile(self):
        os.chdir("croppedImages")
        for file in os.listdir("./"):
            os.remove(file)
        os.chdir("../")
        print("delete all files in croppedImages")
        
        os.chdir("screenshot")
        for file in os.listdir("./"):
            os.remove(file)
        os.chdir("../")
        print("delete all files in screenshot")
        
    def saveGameData(self):
        print("save game data")