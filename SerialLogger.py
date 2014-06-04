#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
# SerialLogger
# Small script to read data from serial and save to a file.
#
# Copyright (C) 2014 by Diego W. Antunes <devlware@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import datetime
import getopt
import os
import serial
import signal
import sys
import time
from serial.tools import list_ports

__version__ = "1.0"
__author__ = 'Diego W. Antunes <devlware@gmail.com>'
__license__ = 'MIT'

class SerialLogger:

    def __init__(self):
        """ Just initialize class variables. """

        self.serialPort = None
        self.outFile = None
        self.outFileName = None
        self.err = None
        self.ser = None

    def main(self):
        """ Main method, parse parameters, open serial and file, call the main loop method. """

        try:
            opts, args = getopt.getopt(sys.argv[1:], "ht:r:s:o:", ["help", "serial=", "outfile="])
        except getopt.GetoptError, self.err:
            print(err)
            print self.usage()
            sys.exit(2)
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print self.usage()
                sys.exit(0)
            elif opt in ("-s", "--serial"):
                self.serialPort = arg
            elif opt in ("-o", "--outfile"):
                self.outFileName = arg
            else:
                assert False, "unhandled option"
                sys.exit()

        for port in list_ports.grep('usbserial'):
        	sal = port
        self.serialPort = sal[0]

        if self.serialPort == None:
            print self.usage()
            sys.exit(2)

        try:
            self.ser = serial.Serial(self.serialPort, 19200, timeout=0.5, parity=serial.PARITY_NONE)
            time.sleep(3)

            if not self.ser.isOpen():
                print "Serial port is not opened, please check."
                sys.exit(-1)
        except (serial.SerialException):
            print "Could not open Serial port."
            sys.exit(-1)

        if self.outFileName == None:
            self.outFileName = str(datetime.datetime.now().date()) + '.log'

            with open(self.outFileName, 'a') as self.outFile:
                actualTime = datetime.datetime.now()
                self.outFile.write(actualTime.ctime())
                self.outFile.write(unicode("\nStarting log...\n"))
                # Try to read any data sent from Arduino.
                arduData = self.ser.read(50)
                self.outFile.write(arduData)
                self.outFile.flush()
                # Starts the process, send start character to Arduino.
                initTime = time.time()
                self.ser.write('s')

                while True:
                    line = self.ser.readline()
                    self.outFile.write(line)
                    self.outFile.flush()

    def usage(self):
        """ Returns usage message. """

        return "Usage: %s\n" \
                "-o\t--outfile\tOutput file to save the log\n" \
                "-s\t--serial\tSerial port where Arduino is connected\n" \
                "-h\t--help\t\tThis help\n" \
                "example: %s -o log1.txt -s '/dev/tty.usbusbmodemXXX'" % (sys.argv[0], sys.argv[0])

    def end_gracefully(self):
        """ This is called to close open file and serial handlers. """

        actualTime = datetime.datetime.now()
        self.outFile.write(actualTime.ctime())
        self.ser.close()
        self.outFile.write(unicode("\nStoping log due to Signal INT.\n"))
        self.outFile.close()

    def signal_handler(self, signal, frame):
        """ Signal handler for Ctrl+C. """

        self.end_gracefully()
        sys.exit(0)

    def list_serial_ports():
        """
        Returns a generator for all available serial ports
        """
        if os.name == 'nt':
            for i in range(256):
            	try:
                	s = serial.Serial(i)
                	s.close()
                	yield 'COM' + str(i + 1)
            	except serial.SerialException:
            		pass
        else:
            for port in list_ports.grep('usbserial'):
            	yield port[0]

if __name__ == '__main__':
    # Creates an instance of SerialLogger
    apl = SerialLogger()
    # Register the Signal handler
    signal.signal(signal.SIGINT, apl.signal_handler)
    apl.main()
