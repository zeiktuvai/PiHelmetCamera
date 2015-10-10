#!/usr/bin/env python
#title           :headcam.py
#description     :Script for controlling raspberry pi camera and audio with GPIO buttons and RF
#author          :G. Rozzo
#date            :20150621
#version         :1.1.1
#usage           :
#notes           :
#python_version  :2.7  
#==============================================================================

import RPi.GPIO as GPIO
import time
import os
import glob
#import datetime
#import picamera
import subprocess
import signal
import multiprocessing
from multiprocessing import Queue
import xbeeRf
import pymedia
import OLED

address = ('\x00\x00',)

# define GPIO pin variables
START_BTTN = 21
STOP_BTTN = 20
LED_PIN = 16


# define functions
# setup function to control led state
def LED(STATE):
    if STATE == "ON":
        GPIO.output(LED_PIN, True)
    if STATE == "OFF":
        GPIO.output(LED_PIN, False)       

# function for blinking led by: num of times, time interval between blinks
def LED_BLINK(NUM, INTERVAL):
    count = 0
    while count < NUM:
       GPIO.output(LED_PIN, True)
       time.sleep(INTERVAL)
       GPIO.output(LED_PIN, False)
       time.sleep(INTERVAL)
       count += 1

   
def video_count() :
    videos = len(glob.glob1("/home/pi/camera","*.h264"))
    display.vid_count = videos


def startRecording() :
    print(cam.getCamRecord())
    if cam.getCamRecord() == False :
        if cam.startCamRec() :
            xbee.sndXbeeMsg('\x00\x00','SR')
            display.start_recording()
            LED("ON")
            video_count()
    time.sleep(1)
    

def stopRecording() :
    if cam.getCamRecord() :
        if cam.stopCamRec() :
            xbee.sndXbeeMsg('\x00\x00','ER')
            display.stop_recording()
            LED("OFF")


#Display Setup
def update_disp_info() :
    camprop = cam.getCamProperties()
    resolution, frame, bit, path = camprop
    unused, res = resolution
    display.resolution = str(res)
    display.framerate = str(frame)


# setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(START_BTTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(STOP_BTTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN, GPIO.OUT)

#define xbee information and queue
port = '/dev/ttyAMA0'
q = Queue()
xbee = xbeeRf.xbeeRadio(port, q)

#define camera
cam = pymedia.pycamera('/home/pi/camera/',False,25,2,8000000)
display = OLED.OLED()

# blink to let you know the camera is ready
if cam.getCamState() :
    print("Camera Ready")
    LED_BLINK(3,.3)
    xbee.sndXbeeMsg('\x00\x00','CR')

video_count()
update_disp_info()


# Main loop
while True:
    display.oled_display()

    if not q.empty() :
       cmd = q.get()
       print(cmd)
       if cmd == 'str' :
          startRecording()          
       if cmd == 'spr' :
          if cam.getCamRecord() :
             stopRecording()
       if cmd == 'cnv' :
          subprocess.call("/home/pi/convert.sh", shell=True)
          xbee.sndXbeeMsg('\x00\x00','CC')
       if cmd == 'gcp' :
          cam.getCamProperties()
       if cmd == 'gcs' :
          if cam.getCamState() :
              xbee.sndXbeeMsg(address[0], 'CR')


    #check if recording and keep going as long as recording is happening.
    if GPIO.input(START_BTTN) == False :
        startRecording()
       
    if cam.getCamRecord() :
        if not cam.waitRecording(2) :
            #error code here
            display.oled_mssg("Error")

        # Check state of button, if stop button is pressed stop everything.
        if GPIO.input(STOP_BTTN) == False :      
             stopRecording()
            

# while not recording, check if stop button is pressed, wait 10 seconds, of pressed the whole time
#  then blink LED rapidly 10 times and execute system shutdown.
    if not cam.getCamRecord() :
        if GPIO.input(STOP_BTTN) == False:
            start = time.time()
            while GPIO.input(STOP_BTTN) == False:
                elapsed = time.time() - start
                if elapsed > 10:
                    LED_BLINK(10,.05)
                    subprocess.call("/home/pi/shutdown.sh", shell=True)
                    while True:
                        display.oled_display_shut()
                time.sleep(0.001)


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


