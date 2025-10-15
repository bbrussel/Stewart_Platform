#!/usr/bin/env python3
from printy import printy

# def sendActuationCommand(legLengths, assemblyGeometry, ser):
# 	printy("Sending actuation command", "cB")
# 	commandString = ",".join(f"{x:.1f}" for x in legLengths)
# 	ser.flush()
# 	ser.write(commandString.encode('utf-8'))
# 	print(commandString)
# 	return ser

def sendActuationCommand(legLengths, assemblyGeometry, ser):
    # Make a CSV with one decimal and a newline terminator the Arduino expects
    command = ",".join(f"{x:.1f}" for x in legLengths) + "\n"   # or "\r\n" to match your sketch
    
    # Clear any backlog from Arduino’s continuous status prints
    if ser.in_waiting:
        ser.reset_input_buffer()
    ser.reset_output_buffer()  # clear pending writes just in case

    # Write and ensure it actually leaves the OS buffer
    ser.write(command.encode("ascii"))
    ser.flush()

    print(command.strip())
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
	printy("Sending actuation command w feedback", "cB")
	commandString = (str(int(( (legLengths[0] - assemblyGeometry.actuatorClosedLength)/(assemblyGeometry.actuatorFullLength - assemblyGeometry.actuatorClosedLength) )*100)))
	commandString += "\n"
	print(legLengths)
	print(commandString)
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
