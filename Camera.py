import RPi.GPIO as GPIO
import time
import os
import datetime
import picamera
import subprocess
import signal
# import pygame

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


# define functions

#
# def GetVideoCount(path):
    # Counts existing video files
#    video_count = 0
#    for root,dirs,files in os.walk(path) :
#        for file in files:
#            if file[-5:]=='.h264':
#                video_count = video_count + 1
#    return video_count

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



# Create camera object and setup
camera = picamera.PiCamera()
camera.framerate = VIDEO_FRAMERATE
camera.resolution = VIDEO_RESOLUTION
camera.rotation = VIDEO_ROTATE
camera.start_preview()


print "Camera object created"
# blink to let you know the camera is ready
LED_BLINK(3,.3)

# define loop control variable
KeepGoing = False

# Main loop
while True:

    if GPIO.input(START_BTTN) == False:
        # get new filename for video recording
        filename = GetFileName()
        # get current time
        start_time = time.time()
        # get new name for audio file
        wavname = VIDEO_PATH + filename + ".wav"

        # define command to execute for recording via subprocess
        record = ["arecord", "-f", "cd", "-D", "plughw:0,0", wavname]

        # Start recording
        stamp = datetime.datetime.fromtimestamp(start_time).strftime('%H:%M:%S')
        print 'Start recording : ' + stamp + ' : ' + filename + '.h264'
        # command to actually start recording
        camera.start_recording(os.path.join(VIDEO_PATH,filename + '.h264'), format='h264', bitrate=VIDEO_BITRATE)
        # kick off subprocess for recording audio
        p = subprocess.Popen(record, stdout=subprocess.PIPE)
        # set variable for loop and turn on indicator LED
        KeepGoing = True
        LED("ON")

        # Wait loop
        while KeepGoing==True:

            # Wait 2 seconds
            camera.wait_recording(2)
      
            # Check state of button, if stop button is pressed stop everything.
            if GPIO.input(STOP_BTTN) == False:
                camera.stop_recording()
                KeepGoing = False
                print 'End Recording: ' + stamp + ' : ' + filename + '.h264'
                os.kill(p.pid, signal.SIGTERM)
                LED("OFF")


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




