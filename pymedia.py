#!/usr/bin/env python
#title           :headcam.py
#description     :Script for controlling raspberry pi camera and audio with GPIO buttons and RF
#author          :G. Rozzo
#date            :20150621
#version         :1.0
#usage           :
#notes           :
#python_version  :3.2  
#==============================================================================

import time
import os
import datetime
import picamera
import subprocess
import signal
import multiprocessing
from multiprocessing import Queue



class pycamera :
    
    def __init__(self, path, rotate, frame, resolution, bitrate) :

        # define path for storing recorded video
        self.VIDEO_PATH = path

        # Camera properties
        self.VIDEO_FRAMERATE  = frame
        if rotate == True :
            self.VIDEO_ROTATE = 180
        else :
            self.VIDEO_ROTATE = 0

        self.RESOLUTIONS = [( 640, 360),(1280, 720),(1920, 1080)]
        if resolution == 0 :
            self.VIDEO_RESOLUTION = self.RESOLUTIONS[0]
        elif resolution == 1 :
            self.VIDEO_RESOLUTION = self.RESOLUTIONS[1]
        elif resolution == 2 :
            self.VIDEO_RESOLUTION = self.RESOLUTIONS[2]
        
        self.VIDEO_BITRATE = bitrate

        # Create camera object and setup
        self.camera = picamera.PiCamera()
        self.camera.framerate = self.VIDEO_FRAMERATE
        self.camera.resolution = self.VIDEO_RESOLUTION
        self.camera.rotation = self.VIDEO_ROTATE
        #camera.start_preview()

        
    def getCamProperties(self) :
        print(self.VIDEO_BITRATE)
        print(self.VIDEO_FRAMERATE)
        print(self.VIDEO_PATH)
        print(self.VIDEO_RESOLUTION)
 
    #Get state of camera, Returns true if camera object open, false if camera closed.
    def getCamState(self) :
        state = True
        try :
            self.camera._check_camera_open()
        except :
            state = False
        return state

    #Check if camera is recording, if it is return True, if not return False
    def getCamRecord(self) :
        state = False
        try :
            self.camera._check_recording_stopped()
        except :
            state = True
        return state

    def __GetFileName(self):
    # Generates a filename with timestamp
        filename = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        return filename


    def __getTimeStamp(self) :
        start_time = time.time()
        timestamp = datetime.datetime.fromtimestamp(start_time).strftime('%H:%M:%S')
        return timestamp


    def startCamRec(self) :
    
        filename = self.__GetFileName()
                   
        # get new name for audio file
        wavname = self.VIDEO_PATH + filename + ".wav"
        # define command to execute for recording via subprocess
        record = ["arecord", "-f", "cd", "-D", "plughw:0,0", wavname]

        # Start recording
        stamp = self.__getTimeStamp()
        print('Start recording : ' + stamp + ' : ' + filename + '.h264')
             
        # command to actually start recording
        self.camera.start_recording(os.path.join(self.VIDEO_PATH,filename + '.h264'), format='h264', bitrate=self.VIDEO_BITRATE)
        # kick off subprocess for recording audio
        self.p = subprocess.Popen(record, stdout=subprocess.PIPE)
        return True


    def stopCamRec(self) :
        print('End Recording: ' + self.__getTimeStamp())
        os.kill(self.p.pid, signal.SIGTERM)
        self.camera.stop_recording()  
        return True

    #calls wait_recording method, if an error occurs during recording, returns false.
    def waitRecording(self, secs) :
        state = True
        try :
            self.camera.wait_recording(secs)
        except :
            state = False
        return state



#cam = pycamera('/home/pi/camera',True,25,2,8000000)
#cam.getCamProperties()
#print("state " + str(cam.getCamState()))
#print("recording " + str(cam.getCamRecord()))
#val = cam.startCamRec()
#print(val)
#print("recording " + str(cam.getCamRecord()))
#time.sleep(10)
#val = cam.stopCamRec()
#print(val)
#time.sleep(5)
#exit()

