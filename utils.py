import os
import shlex
import subprocess
import time


class Utils(object):
    def __init__(self, rootPath):
        self.__rootPath = rootPath
        print(self.__rootPath)

    def screenshot(self):
        self.deleteFile()
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
        # print("delete all files in croppedImages")

        os.chdir("screenshot")
        for file in os.listdir("./"):
            os.remove(file)
        os.chdir("../")
        # print("delete all files in screenshot")

    def saveGameData(self):
        print("save game data")

    def restart(self):
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
        time.sleep(3)
        os.system(start)

        time.sleep(8)
        os.system("nox_adb shell input tap %d %d " % (x, y))