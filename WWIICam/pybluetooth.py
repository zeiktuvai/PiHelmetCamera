import serial
import multiprocessing
from multiprocessing import Queue

class pybluetooth :

    def __init__(self, blueport, queue) :
        self.Port = serial.Serial(blueport, 9600)
        self.q = queue

        def readlineCR(return_val):
            rv = ""
            ct = 0
            while True :
                while ct < 4:
                        ch = self.Port.read()
                        if ch =='!':
                                ct = 1
                                continue
                        if ct > 0:
                                rv += ch
                                ct = ct + 1
                               # print(rv)
                self.q.put(rv)
                ct = 0
                rv = ""

        jobs = []
        readThread = multiprocessing.Process(target=readlineCR, args=(queue,))
        jobs.append(readThread)
        readThread.start()


    def write(self, data) :
        self.Port.write(data)


#blue = pybluetooth("/dev/ttyAMA0")
#while True:
#        val = blue.readlineCR()
#        print(val)
#        blue.write(val)
