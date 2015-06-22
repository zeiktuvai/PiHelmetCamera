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

import RPi.GPIO as GPIO
import time
#import os
#import datetime
#import picamera
import subprocess
#import signal
import multiprocessing
from multiprocessing import Queue
import xbeeRf
import pymedia


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
   

def startRecording() :
    if cam.getCamRecord == False :
        if cam.startCamRec() :
            xbee.sndXbeeMsg('\x00\x00','SR')
            LED("ON")
    time.sleep(1)
    

def stopRecording() :
    if cam.getCamRecord() :
        if cam.stopCamRec() :
            xbee.sndXbeeMsg('\x00\x00','ER')
            LED("OFF")


# setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(START_BTTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(STOP_BTTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN, GPIO.OUT)

#define xbee information and queue
port = '/dev/ttyAMA0'
q = Queue()
xbee = xbeeRf.xbeeRadio(port,q)

#define camera
cam = pymedia.pycamera('/home/pi/camera',True,25,2,8000000)

# blink to let you know the camera is ready
if cam.getCamState() :
    print("Camera Ready")
    LED_BLINK(3,.3)
    xbee.sndXbeeMsg('\x00\x00','CR')



#global KeepGoing
#KeepGoing = False
#global recordFlag
#recordFlag = False



# Main loop
while True:

    if not q.empty() :
       cmd = q.get()
       if cmd == 'StR' :
          #call start function.
          startRecording()          
       if cmd == 'SpR' :
          if cam.getCamRecord() :
             stopRecording()
       if cmd == 'cnv' :
          subprocess.call("/home/pi/convert.sh", shell=True)
       if cmd == 'gcp' :
          cam.getCamProperties()


    #check if recording and keep going as long as recording is happening.
    if GPIO.input(START_BTTN) == False :
        startRecordin()
       
    if cam.getCamRecord() :
        if not cam.waitRecording(2) :
            #error code here
            print('Error')

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


