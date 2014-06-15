dev-tools
=========

Tools for hardware and software development, scripts, programs etc.

SerialLogger  

Some features of SerialLogger:  
1) Output file is set to yy-mm-dd.log by default if you did not enter a file.  
2) If no serial entered, automatically search for tty.usbmodem or tty.usbserial or COMXXX.  
3) If no baud entered use 19200 by default.  
4) Use -t option to have serial data spit over the command line.  

By now most of the tests were conducted in MacOS. But, it should work on Windows and Linux machines.  

Usage: SerialLogger.py  
-o	--outfile	Output file to save the log  
-s	--serial	Serial port where Arduino is connected  
-b  --baud    Baud rate min 1200 and max 921600, default 19200  
-t  --tail    Log and prints device output to command line  
-h	--help		This help  
example: SerialLogger.py -o log1.txt -s '/dev/tty.usbusbmodemXXX' -b 19200 -t
