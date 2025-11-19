#!/usr/bin/env python3
from printy import printy

def sendEnableCommand(ser):
    command = "$ENABLE$\n"   # or "\r\n" to match your sketch
    if ser.in_waiting:
        ser.reset_input_buffer()
    ser.reset_output_buffer()  # clear pending writes just in case

    ser.write(command.encode("ascii"))
    ser.flush()
    print("Command: " + command.strip())
    return ser

def sendActuationCommand(legLengths, speeds, assemblyGeometry, ser):
    # Interleave lengths and speeds: length1,speed1,length2,speed2,...
    interleaved = []
    for length, speed in zip(legLengths, speeds):
        interleaved.append(f"{length:.1f}")
        interleaved.append(f"{int(speed)}")
    
    command = "$" + ",".join(interleaved) + "$\n"
    
    if ser.in_waiting:
        ser.reset_input_buffer()
    ser.reset_output_buffer()  # clear pending writes just in case

    ser.write(command.encode("ascii"))
    ser.flush()

    print("Command: " + command.strip())
    return ser

def validateLegLengths(legLengths, assemblyGeometry):
	allValid = True
	for i in range(6):
		if (legLengths[i] > assemblyGeometry.faultMaxLength) | (legLengths[i] < assemblyGeometry.faultMinLength):
			allValid = False
	return allValid

# def sendHome(assemblyGeometry, ser):
# 	print("Sending legs to home lengths")
# 	homeLengths = [assemblyGeometry.actuatorHomeLength] * 6
# 	if validateLegLengths(homeLengths, assemblyGeometry) == True:
# 		ser = sendActuationCommand(homeLengths, assemblyGeometry, ser)

# 	return ser




# #Developing Feedback.  Can only work on this with single leg since feedback is required
# def sendActuationCommandSingleLegWFeedback(legLengths, assemblyGeometry, ser):
# 	printy("Sending actuation command w feedback", "cB")
# 	commandString = (str(int(( (legLengths[0] - assemblyGeometry.actuatorClosedLength)/(assemblyGeometry.actuatorFullLength - assemblyGeometry.actuatorClosedLength) )*100)))
# 	commandString += "\n"
# 	print(legLengths)
# 	print(commandString)
# 	ser.write(commandString.encode('utf-8'))
# 	bs = ser.readline()
# 	if "Complete" in bs.decode('ascii'):
# 		printy(bs.decode('ascii').strip(), "nB")
# 	else:
# 		printy(bs.decode('ascii').strip(), "rB")
# 	return ser


# def sendHomeSingleLegWFeedback(assemblyGeometry, ser):
# 	print("Sending legs to home lengths")
# 	homeLengths = [assemblyGeometry.actuatorHomeLength] * 6
# 	if validateLegLengths(homeLengths, assemblyGeometry) == True:
# 		ser = sendActuationCommandSingleLegWFeedback(homeLengths, assemblyGeometry, ser)
# 	return ser
