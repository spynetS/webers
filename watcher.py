from os import *
import os
import time

class Logger:
    def __init__(self):
        self.should_log = True

    def log(self,msg):
        from time import gmtime, strftime
        tday = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        print(tday,"|INFO|",msg)

class watcher:
    def __init__(self):
        self.path = "./"
        self.readFiles = {}
        self.sleeptime = 1

    def start(self,new_file=lambda: None, edited=lambda :None, logger=Logger(), ignore = ["./.git/"]):

        while True: 
            for subdir, dirs, files in os.walk(self.path, topdown=True):

                for file in files:
                    #print os.path.join(subdir, file)
                    filePath = subdir + os.sep + file
                    fileStatsObj = os.stat ( filePath )
                    t = os.path.getmtime(filePath)

                    isBreak = False
                    for k in ignore:
                        if(k in filePath):
                            isBreak = True
                    if(isBreak): break

                    if filePath not in self.readFiles.keys():
                        logger.log("new file detected "+filePath)
                        new_file()
                        self.readFiles[filePath] = t
                    elif self.readFiles[filePath] != t:
                        logger.log(filePath+" edited")
                        edited()
                        self.readFiles[filePath] = t
                    

            time.sleep(self.sleeptime)
