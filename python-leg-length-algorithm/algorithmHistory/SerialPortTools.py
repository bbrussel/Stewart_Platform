#!/usr/bin/env python3

import serial
import time
from termcolor import colored

maxlegLength = 153
minLegLength = 103
midLength = minLegLength + (maxlegLength - minLegLength)/2

def actuateToLengthMM(lengthMM, ser):
	validLength = True
	if lengthMM < minLegLength:
		validLength = False
	elif lengthMM > maxlegLength:
		validLength = False
	if validLength:
		print(colored("Actuating to " + str(lengthMM) + "mm", "green"))
		value = int(100*(lengthMM - minLegLength)/(maxlegLength - minLegLength))
		ser.write(str(value).encode('utf-8'))
		movementComplete = False
		while movementComplete == False :
			value = ser.readline()
			if (value == b'Movement Complete\r\n') :
				movementComplete = True;
				print("Done")
	else:
		print(colored(str(lengthMM) + " isn't a valid leg length", "red"))

	return validLength

def main():
	ser = serial.Serial("/dev/ttyACM0")
	finished = actuateToLengthMM(midLength, ser)
	finished = actuateToLengthMM(153, ser)
	finished = actuateToLengthMM(113, ser)
	finished = actuateToLengthMM(103, ser)
	ser.close()

# main()