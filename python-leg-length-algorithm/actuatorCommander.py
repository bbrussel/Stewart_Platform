#!/usr/bin/env python3
from printy import printy

def sendActuationCommand(legLengths, assemblyGeometry, ser):
	percentLengths = []
	for mem in legLengths:
		percentLengths.append(str(int(( (mem - assemblyGeometry.actuatorClosedLength)/(assemblyGeometry.actuatorFullLength - assemblyGeometry.actuatorClosedLength) )*100)))
	commandString = (",").join(percentLengths)
	commandString += "\n"
	ser.write(commandString.encode('utf-8'))
	print(commandString)
	return ser



def validateLegLengths(legLengths, assemblyGeometry):
	allValid = True
	for i in range(6):
		if (legLengths[i] > assemblyGeometry.faultMaxLength) | (legLengths[i] < assemblyGeometry.faultMinLength):
			allValid = False
	return allValid

def sendHome(assemblyGeometry, ser):
	print("Sending legs to home lengths")
	homeLengths = [assemblyGeometry.actuatorHomeLength] * 6
	if validateLegLengths(homeLengths, assemblyGeometry) == True:
		ser = sendActuationCommand(homeLengths, assemblyGeometry, ser)

	return ser






#Developing Feedback.  Can only work on this with single leg since feedback is required
def sendActuationCommandSingleLegWFeedback(legLengths, assemblyGeometry, ser):
	printy("Sending actuation command", "cB")
	commandString = (str(int(( (legLengths[0] - assemblyGeometry.actuatorClosedLength)/(assemblyGeometry.actuatorFullLength - assemblyGeometry.actuatorClosedLength) )*100)))
	commandString += "\n"
	ser.write(commandString.encode('utf-8'))
	bs = ser.readline()
	if "Complete" in bs.decode('ascii'):
		printy(bs.decode('ascii').strip(), "nB")
	else:
		printy(bs.decode('ascii').strip(), "rB")
	return ser

def sendHomeSingleLegWFeedback(assemblyGeometry, ser):
	print("Sending legs to home lengths")
	homeLengths = [assemblyGeometry.actuatorHomeLength] * 6
	if validateLegLengths(homeLengths, assemblyGeometry) == True:
		ser = sendActuationCommandSingleLegWFeedback(homeLengths, assemblyGeometry, ser)

	return ser
