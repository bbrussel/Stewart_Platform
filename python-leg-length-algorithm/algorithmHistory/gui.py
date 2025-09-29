#!/usr/bin/env python3 
import numpy as np
from stewartController import Stewart_Platform
import sys
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import serial
plt.rcParams["font.family"] = "Trebuchet MS"
np.seterr(divide='ignore')
np.seterr(invalid='ignore')

import SerialPortTools

actuateLegs = False

#Initial View      ##########################################################################################################################
# elevationAngle=0.0
# azimuthAngle=0.0

# elevationAngle=30.0
# azimuthAngle=60.0

elevationAngle=20.0
azimuthAngle=80.0


if actuateLegs == True:
    ser = serial.Serial("/dev/ttyACM0")


#Initial Variables ##########################################################################################################################
figureTitle = "Stewart Platform Model"
r_B = 130           # Base radius
r_P = 130           # Platform Radius
lhl = 0           # Horn lengths (0 for our model?)
ldl = 127            # Rod length
baseAnchorAngle = 32 # angle from center out to leg pair in degrees
platformAnchorAngle = 50 # angle from center out to leg pair in degrees
ref_rotationDegrees = 0    # Entire assembly rotation about Z axis(Vert)

#Defines min and max rod actuator length used for limit warnings
actuatorClosedLength = 102
actuatorStrokedLength = 152
actuatorStrokeMargin = .10

#Calculated Variables:
Psi_B = .5*baseAnchorAngle*np.pi/180      # Half of angle between two anchors on the base (radians)
Psi_P = .5*platformAnchorAngle*np.pi/180      # Half of angle between two anchors on the platform (radians)
ref_rotation = .5*ref_rotationDegrees*np.pi/180

##############################################################################################################################################
##############################################################################################################################################

def updateDataString(r_B, r_P, lhl, ldl, leg_lengths, servo_angles):
    dataString = "Base Radius: " + str(r_B) + "\n"
    dataString += "Base Leg Spacing: " + str(baseAnchorAngle) + "$^\circ$\n"
    dataString += "Platform Radius: " + str(r_P) + "\n"
    dataString += "Platform Leg Spacing: " + str(platformAnchorAngle) + "$^\circ$\n\n"
    if lhl > 0:
        dataString += "Servo Horn Lengths: " + str(lhl) + "\n\n"
    dataString += "Actuator Lengths:\n"
    counter = 1
    for mem in leg_lengths:
        if (mem <= actuatorClosedLength) | (mem >= actuatorStrokedLength):
            dataString += str(counter) + ": " + str(round(mem, 2)) + " !!!" "\n"
        else:
            dataString += str(counter) + ": " + str(round(mem, 2)) + "\n"
        counter += 1

    if lhl > 0:
        dataString += "\nServo Horn angles:\n"
        counter = 1
        for mem in servo_angles:
            dataString += str(counter) + ": " + str(round(mem, 2)) + "\n"
            counter += 1

    return dataString

def validateLegLenths(leg_lengths):
    allValid = True
    for mem in leg_lengths:
        if (mem <= actuatorClosedLength) | (mem >= actuatorStrokedLength):
            allValid = False
    return allValid



def main():
    #initialization parameters

    if actuateLegs == True:
        SerialPortTest.actuateToLengthMM(ldl, ser)

    platform = Stewart_Platform(r_B, r_P, lhl, ldl, Psi_B, Psi_P, ref_rotation, actuatorClosedLength, actuatorStrokedLength, actuatorStrokeMargin)
    
    # Platform position parameters
    xTranslation = 0
    yTranslation = 2
    zTranslation = 1
    translationVector = np.array([xTranslation,yTranslation,zTranslation])  # Translation in X,Y,Z
    pitch = 2            # degrees
    roll = 5.2            # degrees
    yaw = 0             # degrees

    rotationVector = np.array([roll*np.pi/180, pitch*np.pi/180, yaw*np.pi/180])

    servo_angles, leg_lengths = platform.calculate(translationVector, rotationVector)

    if actuateLegs == True:
        SerialPortTest.actuateToLengthMM(leg_lengths[0], ser)
        # printToConsole(servo_angles, leg_lengths)

    fig, ax = plt.subplots()

    fig.canvas.manager.set_window_title("Heliospace " + figureTitle)

    fig.set_size_inches(10, 8)
    plt.subplots_adjust(bottom=0.25, top=.95)
    fig.suptitle(figureTitle, fontsize=24, fontweight="bold")
    fig.patch.set_visible(False)
    ax.axis('off')

    ax = platform.plot_platform()

    ax.view_init(elev=elevationAngle, azim=azimuthAngle)

    rollAxis = plt.axes([0.25, 0.2, 0.65, 0.03])
    rollSlider = Slider(rollAxis, 'Roll$^\circ$', -90.0, 90.0, roll, color="#268bd2")
    pitchAxis = plt.axes([0.25, 0.17, 0.65, 0.03])
    pitchSlider = Slider(pitchAxis, 'Pitch$^\circ$', -90.0, 90.0, pitch, color="#268bd2")
    yawAxis = plt.axes([0.25, 0.14, 0.65, 0.03])
    yawSlider = Slider(yawAxis, 'Yaw$^\circ$', -90.0, 90.0, yaw, color="#268bd2")
    axXTranslation = plt.axes([0.25, 0.11, 0.65, 0.03])
    xTranslationSlider = Slider(axXTranslation, 'Translate X', -50, 50, xTranslation, color="#268bd2")
    axYTranslation = plt.axes([0.25, 0.08, 0.65, 0.03])
    yTranslationSlider = Slider(axYTranslation, 'Translate Y', -50, 50, yTranslation, color="#268bd2")
    axZTranslation = plt.axes([0.25, 0.05, 0.65, 0.03])
    zTranslationSlider = Slider(axZTranslation, 'Translate Z', -50, 50, zTranslation, color="#268bd2")


    def update(val):
        xTranslation = xTranslationSlider.val
        yTranslation = yTranslationSlider.val
        zTranslation = zTranslationSlider.val
        translationVector = np.array([xTranslation,yTranslation,zTranslation])  # Translation in X,Y,Z

        xRotation = rollSlider.val              # degrees
        yRotation = pitchSlider.val               # degrees
        zRotation = yawSlider.val                   # degrees

        rotationVector = np.array([xRotation*np.pi/180, yRotation*np.pi/180, zRotation*np.pi/180])
        servo_angles, leg_lengths = platform.calculate(translationVector, rotationVector)

        ax = platform.plot_platform()

        ax.view_init(elev=elevationAngle, azim=azimuthAngle)

        dataString = updateDataString(r_B, r_P, lhl, ldl, leg_lengths, servo_angles)
        dataText.set_text(dataString)

        if (validateLegLenths(leg_lengths) == True) and (actuateLegs == True):
            SerialPortTest.actuateToLengthMM(leg_lengths[0], ser)




    rollSlider.on_changed(update)
    pitchSlider.on_changed(update)
    yawSlider.on_changed(update)
    xTranslationSlider.on_changed(update)
    yTranslationSlider.on_changed(update)
    zTranslationSlider.on_changed(update)

    

    resetax = plt.axes([0.8, 0.01, 0.1, 0.04])
    resetButton = Button(resetax, 'Reset')


    def resetSliders(event):
        rollSlider.reset()
        pitchSlider.reset()
        yawSlider.reset()
        xTranslationSlider.reset()
        yTranslationSlider.reset()
        zTranslationSlider.reset()

    resetButton.on_clicked(resetSliders)
 

    dataString = updateDataString(r_B, r_P, lhl, ldl, leg_lengths, servo_angles)
    
    dataText = plt.figtext(0.02, .4, dataString, fontsize=14)

    plt.show()

    


if __name__ == "__main__":
    main()

