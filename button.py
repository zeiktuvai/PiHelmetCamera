import RPi.GPIO as GPIO
import time
import uinput

GPIO.setmode(GPIO.BCM)

p5 = 5
p6 = 6
p13 = 13
p16 = 16
p19 = 19
p20 = 20
p21 = 21
p26 = 26

GPIO.setwarnings(False)
GPIO.setup(p5, GPIO.IN)
GPIO.setup(p6, GPIO.IN)
GPIO.setup(p13, GPIO.IN)
GPIO.setup(p16, GPIO.IN)
GPIO.setup(p19, GPIO.IN)
GPIO.setup(p20, GPIO.IN)

events = (uinput.KEY_LEFT,uinput.KEY_RIGHT,uinput.KEY_UP,uinput.KEY_DOWN,uinput.KEY_EQUAL,
          uinput.REL_WHEEL,)
device = uinput.Device(events)


def ms_up(channel):
    device.emit(uinput.REL_WHEEL, 1)
    

def ms_dwn(channel):
    device.emit(uinput.REL_WHEEL, -1)
    

def key_left(channel):
    device.emit_click(uinput.KEY_LEFT)
    

def key_right(channel):
    device.emit_click(uinput.KEY_RIGHT)
    

def key_pressup(channel):
    device.emit_click(uinput.KEY_UP)
   
def key_dwn(channel):
    device.emit_click(uinput.KEY_DOWN)  
   
           
GPIO.add_event_detect(p5, GPIO.FALLING, callback=ms_up, bouncetime=1000)
GPIO.add_event_detect(p6, GPIO.FALLING, callback=ms_dwn, bouncetime=1000)
GPIO.add_event_detect(p13, GPIO.FALLING, callback=key_left, bouncetime=1000)
GPIO.add_event_detect(p16, GPIO.FALLING, callback=key_right, bouncetime=1000)
GPIO.add_event_detect(p19, GPIO.FALLING, callback=key_pressup, bouncetime=1000)
GPIO.add_event_detect(p20, GPIO.FALLING, callback=key_dwn, bouncetime=1000)

while True:
    time.sleep(1)             
            





GPIO.cleanup()
