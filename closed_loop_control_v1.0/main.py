import cv2
import serial
import numpy as np
from printy import printy
from collections import deque
import os

import image_utils
import stewartCalculations

pi = np.pi

class feedbackQues_Class():
    def __init__(self):
        self.leg_1 = deque(maxlen=6)
        self.leg_2 = deque(maxlen=6)
        self.leg_3 = deque(maxlen=6)
        self.leg_4 = deque(maxlen=6)
        self.leg_5 = deque(maxlen=6)
        self.leg_6 = deque(maxlen=6)

assemblyGeometry = stewartCalculations.SP_assemblyGeometry()
assemblyGeometry.r_B = 220           # Base radius
assemblyGeometry.r_P = 220           # Platform Radius
assemblyGeometry.actuatorClosedLength = 152
assemblyGeometry.actuatorFullLength = 252
assemblyGeometry.baseAnchorAngleDegrees = 50 # angle from center out to leg pair in degrees
assemblyGeometry.platformAnchorAngleDegrees = 32 # angle from center out to leg pair in degrees
assemblyGeometry.refRotationDegrees = 0    # Assembly oriention around z axis

assemblyGeometry.actuatorHomeLength = assemblyGeometry.actuatorClosedLength + (assemblyGeometry.actuatorFullLength-assemblyGeometry.actuatorClosedLength)/2
assemblyGeometry.psi_B = stewartCalculations.calcPsiB(assemblyGeometry.baseAnchorAngleDegrees, assemblyGeometry.refRotationDegrees) #Radians
assemblyGeometry.psi_P = stewartCalculations.calcPsiP(assemblyGeometry.platformAnchorAngleDegrees, assemblyGeometry.refRotationDegrees) #Radians

assemblyGeometry.stroke = assemblyGeometry.actuatorFullLength-assemblyGeometry.actuatorClosedLength



center_box_size = 30
skipInitialFrames = 10

comport = "COM5"
baudrate = 115200

def parse_telemetry_data(dataLine):
    packetCounter = None
    lastCommandedLengths = [None, None, None, None, None, None]
    feedbackLengths = [None, None, None, None, None, None]
    statusCode = None

    splitLine = dataLine.decode().strip().split(",")
    packetCounter = splitLine[0]
    lastCommandedLengths = [float(splitLine[1]), float(splitLine[2]), float(splitLine[3]), float(splitLine[4]), float(splitLine[5]), float(splitLine[6])]
    feedbackLengths = [float(splitLine[7]), float(splitLine[8]), float(splitLine[9]), float(splitLine[10]), float(splitLine[11]), float(splitLine[12])]
    statusCode = int(splitLine[13])
    outOfRangeFlag = int(splitLine[14])

    return np.array(lastCommandedLengths), np.array(feedbackLengths), statusCode, outOfRangeFlag


def determine_if_moving(feedbackLengths, feedbackTracking):
    que_change_threshold = 3
    feedbackTracking.leg_1.append(feedbackLengths[0])
    feedbackTracking.leg_2.append(feedbackLengths[1])
    feedbackTracking.leg_3.append(feedbackLengths[2])
    feedbackTracking.leg_4.append(feedbackLengths[3])
    feedbackTracking.leg_5.append(feedbackLengths[4])
    feedbackTracking.leg_6.append(feedbackLengths[5])
    que_ranges = [max(feedbackTracking.leg_1) - min(feedbackTracking.leg_1), max(feedbackTracking.leg_2) - min(feedbackTracking.leg_2), max(feedbackTracking.leg_3) - min(feedbackTracking.leg_3), max(feedbackTracking.leg_4) - min(feedbackTracking.leg_4), max(feedbackTracking.leg_5) - min(feedbackTracking.leg_5), max(feedbackTracking.leg_6) - min(feedbackTracking.leg_6)]
    max_que_range = max(que_ranges)
    if max_que_range >= que_change_threshold:
        moving = True
    else:
        moving = False

    return moving, feedbackTracking


def initializePlatformToHome(baseOrientation, platformOrientation, assemblyGeometry, ser, feedbackTracking):
    printy("Initializing platform to home position...", "cB")
    L, legLengths, B, PV = stewartCalculations.PerformCalcs(baseOrientation=baseOrientation, platformOrientation=platformOrientation, assemblyGeometry=assemblyGeometry)
    commandString = ",".join(map(lambda x: format(x, '.2f'), legLengths))
    previous_telemetry_lengths = np.array([None, None, None, None, None, None])
    ser.write(commandString.encode('utf-8'))
    ser.reset_input_buffer()
    telemetry_data = ser.readline()
    lastCommandedLengths, feedbackLengths, statusCode, outOfRangeFlag = parse_telemetry_data(telemetry_data)
    platform_in_motion, feedbackTracking = determine_if_moving(feedbackLengths, feedbackTracking)
    while platform_in_motion == True:
        ser.reset_input_buffer()
        telemetry_data = ser.readline()
        lastCommandedLengths, feedbackLengths, statusCode, outOfRangeFlag = parse_telemetry_data(telemetry_data)
        platform_in_motion, feedbackTracking = determine_if_moving(feedbackLengths, feedbackTracking)

    return baseOrientation, platformOrientation, ser, feedbackTracking

def checkIfPointAdjustmentNeeded(x_offset, y_offset, outOfRangeFlag, platformOrientation, baseOrientation, assemblyGeometry, ser):
    movementRequired = False
    preCommandPitch = platformOrientation.pitchDegrees
    preCommandRoll = platformOrientation.rollDegrees
    if x_offset > (center_box_size/2):
        platformOrientation.rollDegrees -= abs(x_offset)/48
        movementRequired = True
    elif x_offset < (-center_box_size/2):
        platformOrientation.rollDegrees += abs(x_offset)/48
        movementRequired = True
    if y_offset > (center_box_size/2):
        platformOrientation.pitchDegrees += abs(y_offset)/37
        movementRequired = True
    elif y_offset < (-center_box_size/2):
        platformOrientation.pitchDegrees -= abs(y_offset)/37
        movementRequired = True
    if movementRequired == True:
        L, legLengths, B, PV = stewartCalculations.PerformCalcs(baseOrientation=baseOrientation, platformOrientation=platformOrientation, assemblyGeometry=assemblyGeometry)
        commandString = ",".join(map(lambda x: format(x, '.2f'), legLengths))

        print("")
        printy("Current Pitch: {:.2f}°".format(preCommandPitch), "cB")
        printy("Current Roll: {:.2f}°".format(preCommandRoll), "cB")
        printy("Commanded Pitch: {:.2f}°".format(platformOrientation.pitchDegrees), "cB")
        printy("Commanded Roll: {:.2f}°".format(platformOrientation.rollDegrees), "cB")
        if outOfRangeFlag == 1:
            printy(commandString, "rB")
        else:
            printy(commandString, "cB")
        print("")

        ser.write(commandString.encode('utf-8'))

    return platformOrientation, baseOrientation, ser, outOfRangeFlag


def main():
    os.system("clear")

    printy("Initializing Target Detection Video Stream...", 'cB')
    cap = cv2.VideoCapture(1)
    printy("Initializing Observation Video Stream...", 'cB')
    cap2 = cv2.VideoCapture(0)
    printy("Initializing Serial connection to microcontroller...", "cB")
    ser = serial.Serial(comport, baudrate)

    platformOrientation = stewartCalculations.orientation() #Initialize orientation class for platform
    baseOrientation = stewartCalculations.orientation() #Initialize orientation class for base

    feedbackTracking = feedbackQues_Class()

    baseOrientation, platformOrientation, ser, feedbackTracking = initializePlatformToHome(baseOrientation, platformOrientation, assemblyGeometry, ser, feedbackTracking)

    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"Frame Width: {width}")
    print(f"Frame Height: {height}")

    processedFramesCounter = 0

    printy("Beginning Target Tracking...", "cB")
    while True:
        
        x_offset, y_offset, result = image_utils.get_target_position(cap, center_box_size)
        processedFramesCounter += 1

        ret2, frame2 = cap2.read()

        cv2.imshow('Observation', frame2)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            returnValue = True

        ser.reset_input_buffer()
        telemetry_data = ser.readline()
        lastCommandedLengths, feedbackLengths, statusCode, outOfRangeFlag = parse_telemetry_data(telemetry_data)

        platform_in_motion, feedbackTracking = determine_if_moving(feedbackLengths, feedbackTracking)

        if (platform_in_motion == False) and (x_offset is not None) and (processedFramesCounter > skipInitialFrames): #This means target is detected in image and platform is not moving.
            
            platformOrientation, baseOrientation, ser, outOfRangeFlag = checkIfPointAdjustmentNeeded(x_offset, y_offset, outOfRangeFlag, platformOrientation, baseOrientation, assemblyGeometry, ser)

        if processedFramesCounter >= skipInitialFrames:
            print(telemetry_data.decode().strip())

        if result == True:
            break

    cap.release()
    cv2.destroyAllWindows()
    ser.close()


main()