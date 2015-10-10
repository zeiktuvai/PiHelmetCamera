#!/usr/bin/env python
#title           :Camera.py
#description     :Script for controlling raspberry pi camera and audio with GPIO buttons and RF
#author          :G. Rozzo
#date            :20150608
#version         :0.4
#usage           :
#notes           :
#python_version  :2.7  
#==============================================================================

import RPi.GPIO as GPIO
import time
import os
import datetime
import picamera
import subprocess
import signal
import multiprocessing
from serial import Serial
from xbee import XBee
from multiprocessing import Queue
# import pygame


global KeepGoing
KeepGoing = False
global recordFlag
recordFlag = False
global filename
global stamp
global p
global xbee

# define GPIO pin variables
START_BTTN = 21
STOP_BTTN = 20
LED_PIN = 16


# setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(START_BTTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(STOP_BTTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN, GPIO.OUT)

# define path for storing recorded video
VIDEO_PATH = '/home/pi/camera/'

# Camera properties
VIDEO_FRAMERATE  = 25
VIDEO_ROTATE     = 180
#VIDEO_RESOLUTION = ( 640, 360)
#VIDEO_RESOLUTION = (1280, 720)
VIDEO_RESOLUTION = (1920, 1080)
VIDEO_BITRATE = 8000000

#define serial port for xbee
port = '/dev/ttyAMA0'
baudrate = 9600
serial = Serial(port, baudrate)
xbee = XBee(serial)

# define functions
# function to generate file names
def GetFileName():
    # Generates a filename with timestamp
    filename = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
    return filename

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


#sending message over xbee
def xbee_SendMsg(message):
    xbee.tx(dest_addr='\x00\x00', data=message)


def xbee_ReadMsg(return_val):
    while True:
        frame = xbee.wait_read_frame()
        rMssg = repr(frame['rf_data']).replace("\'","")
        q.put(rMssg)
       


def recordVideo() :
    

    # define loop control variable
    # get new filename for video recording
    global filename
    filename = GetFileName()
    # get current time
    start_time = time.time()
    # get new name for audio file
    wavname = VIDEO_PATH + filename + ".wav"
    # define command to execute for recording via subprocess
    record = ["arecord", "-f", "cd", "-D", "plughw:0,0", wavname]

    # Start recording
    global stamp
    stamp = datetime.datetime.fromtimestamp(start_time).strftime('%H:%M:%S')
    msg = 'Start recording : ' + stamp + ' : ' + filename + '.h264'
    print(msg)
    xbee_SendMsg('SR')
    # command to actually start recording
    camera.start_recording(os.path.join(VIDEO_PATH,filename + '.h264'), format='h264', bitrate=VIDEO_BITRATE)
    # kick off subprocess for recording audio
    global p
    p = subprocess.Popen(record, stdout=subprocess.PIPE)
        
    # set variable for loop and turn on indicator LED
    global KeepGoing
    KeepGoing = True
    LED("ON")



def stop() :
    msg = 'End Recording: ' + stamp + ' : ' + filename + '.h264'
    print(msg)
    xbee_SendMsg('ER')
    os.kill(p.pid, signal.SIGTERM)
    LED("OFF")
    camera.stop_recording()  


# Create camera object and setup
camera = picamera.PiCamera()
camera.framerate = VIDEO_FRAMERATE
camera.resolution = VIDEO_RESOLUTION
camera.rotation = VIDEO_ROTATE
#camera.start_preview()



print("Camera Ready")
xbee.tx(dest_addr='\x00\x00', data='CR')

# blink to let you know the camera is ready
LED_BLINK(3,.3)

#create thread for reading xbee
jobs = []
q = Queue()
thread = multiprocessing.Process(target=xbee_ReadMsg, args=(q,))
jobs.append(thread)
thread.start()


# Main loop
while True:


    if not q.empty() :
       cmd = q.get()
       if cmd == 'StR' :
          print("starting") 
          recordFlag = True
       if cmd == 'SpR' :
          print("stopping")
          recordFlag = False
       if cmd == 'cnv' :
          subprocess.call("/home/pi/convert.sh", shell=True)


    if GPIO.input(START_BTTN) == False or recordFlag == True :
        
        if KeepGoing == False :
            recordVideo()
            print("call start")
            time.sleep(1)
        
        

    #---print(KeepGoing)
    if KeepGoing == True :
        camera.wait_recording(2)
    # Check state of button, if stop button is pressed stop everything.
        if GPIO.input(STOP_BTTN) == False or recordFlag == False :      
            if KeepGoing == True :
                KeepGoing = False
                recordFlag = False
                stop()
            



         

# while not recording, check if stop button is pressed, wait 10 seconds, of pressed the whole time
#  then blink LED rapidly 10 times and execute system shutdown.
    if GPIO.input(STOP_BTTN) == False:
        start = time.time()
        while GPIO.input(STOP_BTTN) == False:
            elapsed = time.time() - start
            if elapsed > 10:
                LED_BLINK(10,.05)
                subprocess.call("/home/pi/shutdown.sh", shell=True)
            time.sleep(0.001)




    # Wait loop
    #while KeepGoing==True:

    #      # Wait 2 seconds
    #      camera.wait_recording(2)
    #      print(recordFlag)

    #      # Check state of button, if stop button is pressed stop everything.
    #      if GPIO.input(STOP_BTTN) == False :
    #         recordFlag = False
    #      if recordFlag == False:            
    #         KeepGoing = False

    #msg = 'End Recording: ' + stamp + ' : ' + filename + '.h264'
    #print(msg)
    #xbee_SendMsg('\x00\x00',msg)
    #os.kill(p.pid, signal.SIGTERM)
    #LED("OFF")
    #camera.stop_recording()
