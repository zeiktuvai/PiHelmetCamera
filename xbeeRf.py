#import os
#import sys
#import time
from serial import Serial
from xbee import XBee
import multiprocessing
from multiprocessing import Queue

class xbeeRadio :


    def __init__(self, port, queue) :
        baudrate = 9600
        serial = Serial(port, baudrate)
        self.xbee = XBee(serial)
        self.q = queue

        def rdXbeeMsg(return_val):
            while True:
                frame = self.xbee.wait_read_frame()
                rMssg = repr(frame['rf_data']).replace("\'","")
                self.q.put(rMssg)

        jobs = []
        readThread = multiprocessing.Process(target=rdXbeeMsg, args=(queue,))
        jobs.append(readThread)
        readThread.start()

    def sndXbeeMsg (self, addr, data) :
        self.xbee.tx(dest_addr=addr, data=data)

#'\x00\x01'