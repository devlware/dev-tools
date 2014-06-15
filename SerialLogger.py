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
import glob
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
        self.baud = None
        self.tail = None

    def main(self):
        """ Main method, parse parameters, open serial and file, call the main loop method. """

        try:
            opts, args = getopt.getopt(sys.argv[1:], "hs:b:o:t", ["help", "serial=", "baud=" "outfile=", "tail"])
        except getopt.GetoptError, self.err:
            print(self.err)
            print self.usage()
            sys.exit(2)
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print self.usage()
                sys.exit(0)
            elif opt in ("-s", "--serial"):
                self.serialPort = arg
            elif opt in ("-b", "--baud"):
                self.baud = arg
            elif opt in ("-o", "--outfile"):
                self.outFileName = arg
            elif opt in ("-t", "--tail"):
                self.tail = True
            else:
                assert False, "unhandled option"
                sys.exit()

        # Check if serial port is ok.
        self.handle_serial_ports()

        # Validate baud rate.
        if self.baud != None:
            if not self.baud >= 1200 and self.baud <= 921600:
                print "Invalid baud rate, min 1200 bps and max 921600 bps."
                print self.usage()
                sys.exit(2)
        else:
            print "Using default baud rate of 19200 bps. Ultra fast ;)"
            self.baud = 19200

        # Try to open serial port.
        try:
            self.ser = serial.Serial(self.serialPort, self.baud, timeout=0.5, parity=serial.PARITY_NONE)
            time.sleep(3)
            if not self.ser.isOpen():
                print "Serial port is not opened, please check."
                sys.exit(-1)
        except (serial.SerialException):
            print "Could not open Serial port."
            sys.exit(-1)

        # if not passed a file name use default yyyy-mm-dd.log
        if self.outFileName == None:
            self.outFileName = str(datetime.datetime.now().date()) + '.log'

        with open(self.outFileName, 'a') as self.outFile:
            actualTime = datetime.datetime.now()
            self.outFile.write(actualTime.ctime())
            self.outFile.write(unicode("\nStarting log...\n"))
            self.outFile.flush()
            initTime = time.time()

            while True:
                try:
                    line = self.ser.readline()
                    if self.tail:
                        sys.stdout.write(line)
                    self.outFile.write(line)
                    self.outFile.flush()
                except (serial.SerialException):
                    self.outFile.write(unicode("\nSerial error.\n"))
                    print "Serial error, exiting..."
                    self.end_gracefully()
                    sys.exit(0)

    def handle_serial_ports(self):
        """ List available serial ports for depending on OS. """
        
        # Check if serial port exists.
        found = False
        computer_ports = None
        
        if self.serialPort != None:
            if os.name == 'nt':
                # windows XP and 7 gives nt, com ports should be COMXXX
                computer_ports = list(serial.tools.list_ports.comports())
                if len(computer_ports) > 0:
                    for port_item in computer_ports:
                        if port_item[0] == self.serialPort:
                            found = True
                            break
            elif os.name == 'posix':
                # Macos and Linux gives posix.
                computer_ports = glob.glob('/dev/tty.usbmodem*') + glob.glob('/dev/tty.usbserial*')
                if len(computer_ports) > 0:
                    for port_item in computer_ports:
                        if port_item == self.serialPort:
                            found = True
                            break            
        else:
            if os.name == 'nt':
                computer_ports = list(serial.tools.list_ports.comports())
                if len(computer_ports) > 0:
                    self.serialPort = computer_ports[0][0]
                    found = True
                    print "Using default COM port: " + self.serialPort
            elif os.name == 'posix':
                computer_ports = glob.glob('/dev/tty.usbmodem*') + glob.glob('/dev/tty.usbserial*')
                if len(computer_ports) > 0:
                    self.serialPort = computer_ports[0]
                    found = True
                    print "Using default serial port: " + self.serialPort
            
        if found == False:
            print "Need to enter a proper serial, tty.usbmodem or tty.usbserial or COMXYZ."
            print self.usage()            
            sys.exit(2)

    def usage(self):
        """ Returns usage message. """

        return "Usage: %s\n" \
                "-o\t--outfile\tOutput file to save the log, default yy-mm-dd.log\n" \
                "-s\t--serial\tSerial port where device is connected\n" \
                "-b\t--baud\t\tBaud rate min 1200 and max 921600, default 19200\n" \
                "-t\t--tail\t\tLog and prints device output to command line\n" \
                "-h\t--help\t\tThis help\n" \
                "example: %s -o log1.txt -s '/dev/tty.usbusbmodemXXX' -b 19200 -t" % (sys.argv[0], sys.argv[0])

    def end_gracefully(self):
        """ This is called to close open file and serial handlers. """

        actualTime = datetime.datetime.now()
        self.outFile.write(actualTime.ctime())
        if self.ser.isOpen():
            self.ser.close()
        self.outFile.write(unicode("\nStoping log due to Signal INT.\n"))
        self.outFile.close()

    def signal_handler(self, signal, frame):
        """ Signal handler for Ctrl+C. """

        self.end_gracefully()
        sys.exit(0)

if __name__ == '__main__':
    # Creates an instance of SerialLogger
    apl = SerialLogger()
    # Register the Signal handler
    signal.signal(signal.SIGINT, apl.signal_handler)
    apl.main()
