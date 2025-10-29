#!/usr/bin/env python3 
import numpy as np
import os
import matplotlib.pyplot as plt
import serial
from printy import printy
import pyfiglet
os.system('cls')
print(pyfiglet.figlet_format("Soloh Research", font = "slant"))
# np.seterr(divide='ignore')
# np.seterr(invalid='ignore')
# np.set_printoptions(suppress = True) #prevents printing arrays in scientific notation during debugging
# np.set_printoptions(linewidth=np.inf) #prevents line wrapping when printing arrays 
pi = np.pi

import plottingTools
import stewartCalculations
import actuatorCommander


class orientation():
	def __init__(self):
		self.xTranslation = None
		self.yTranslation = None
		self.zTranslation = None
		self.rollDegrees = None
		self.pitchDegrees = None
		self.yawDegrees = None

class SP_assemblyGeometry():
	def __init__(self):
		self.r_B = None
		self.r_P = None
		self.actuatorClosedLength = None
		self.actuatorFullLength = None
		self.actuatorStrokeFaultMargin = None
		self.actuatorStrokeWarningMargin = None
		self.actuatorHomeLength = None
		self.baseAnchorAngleDegrees = None
		self.platformAnchorAngleDegrees = None
		self.refRotationDegrees = None

		self.stroke = None
		self.warningMinLength = None
		self.warningMaxLength = None
		self.faultMinLength = None
		self.faultMaxLength = None



######################################################################################################################################
#Initialization Variables:

actuateLegs = False
generatePlot = True
comport = "COM3"

assemblyGeometry = SP_assemblyGeometry()
assemblyGeometry.r_B = 215           # Base radius
assemblyGeometry.r_P = 215           # Platform Radius
assemblyGeometry.actuatorClosedLength = 152
assemblyGeometry.actuatorFullLength = 252

assemblyGeometry.actuatorStrokeFaultMargin = .01
assemblyGeometry.actuatorStrokeWarningMargin = .1

assemblyGeometry.baseAnchorAngleDegrees = 60 # full angle from center out to leg pair in degrees
assemblyGeometry.platformAnchorAngleDegrees = 24 # full angle from center out to leg pair in degrees
assemblyGeometry.refRotationDegrees = 0    # Assembly oriention around z axis

#Calculated Variables:
assemblyGeometry.actuatorHomeLength = assemblyGeometry.actuatorClosedLength + (assemblyGeometry.actuatorFullLength-assemblyGeometry.actuatorClosedLength)/2
assemblyGeometry.psi_B = stewartCalculations.calcPsiB(assemblyGeometry.baseAnchorAngleDegrees, assemblyGeometry.refRotationDegrees) #Radians
assemblyGeometry.psi_P = stewartCalculations.calcPsiP(assemblyGeometry.platformAnchorAngleDegrees, assemblyGeometry.refRotationDegrees) #Radians

assemblyGeometry.stroke = assemblyGeometry.actuatorFullLength-assemblyGeometry.actuatorClosedLength
assemblyGeometry.warningMinLength = assemblyGeometry.actuatorClosedLength + assemblyGeometry.stroke*assemblyGeometry.actuatorStrokeWarningMargin
assemblyGeometry.warningMaxLength = assemblyGeometry.actuatorFullLength - assemblyGeometry.stroke*assemblyGeometry.actuatorStrokeWarningMargin
assemblyGeometry.faultMinLength = assemblyGeometry.actuatorClosedLength + assemblyGeometry.stroke*assemblyGeometry.actuatorStrokeFaultMargin
assemblyGeometry.faultMaxLength = assemblyGeometry.actuatorFullLength - assemblyGeometry.stroke*assemblyGeometry.actuatorStrokeFaultMargin


def processPose(platformOrientation, baseOrientation, assemblyGeometry, ser, generatePlot, actuateLegs):

	platform_coords, legLengths, base_coords, PV, dataString = stewartCalculations.PerformCalcs(baseOrientation=baseOrientation, platformOrientation=platformOrientation, assemblyGeometry=assemblyGeometry)

	if actuateLegs:
		if (actuatorCommander.validateLegLengths(legLengths, assemblyGeometry)):
			# ser = actuatorCommander.sendActuationCommandSingleLegWFeedback(legLengths, assemblyGeometry, ser)
			ser = actuatorCommander.sendActuationCommand(legLengths, assemblyGeometry, ser)
		else:
			printy("Aborting actuation command to fault leg lengths", "rB")
	else:
		printy("Not actuating legs because actuateLegs flag is set to False", "rB")
		print(",".join(f"{x:.1f}" for x in legLengths))

	if generatePlot:
		plottingTools.generate3DPlot(InitialViewElevationAngle=4, InitialViewAzimuthAngle=-78, platform_coords=platform_coords, legLengths=legLengths, base_coords=base_coords, PV=PV, dataString=dataString, assemblyGeometry=assemblyGeometry)
	else:
		printy("Not generating plots because generatePlots flag is set to False", "rB")
		input("Press Enter to continue to next pose...")


	plt.show()
	return ser

def demo():

	if actuateLegs == True:
		ser = serial.Serial(port=comport, baudrate=115200, timeout=0.1, write_timeout=0.5)
		ser.reset_input_buffer()
		ser.reset_output_buffer()
		# ser = actuatorCommander.sendHome(assemblyGeometry, ser)
		# ser = actuatorCommander.sendHomeSingleLegWFeedback(assemblyGeometry, ser)
	else:
		ser = None

	baseOrientation = orientation() #Initialize orientation class for base
	baseOrientation.xTranslation = 0
	baseOrientation.yTranslation = 0
	baseOrientation.zTranslation = 0
	baseOrientation.pitchDegrees = 0
	baseOrientation.rollDegrees = 0
	baseOrientation.yawDegrees = 0

	platformOrientation = orientation() #Initialize orientation class for platform


	platformOrientation.xTranslation = 0.0
	platformOrientation.yTranslation = 0.0
	platformOrientation.zTranslation = 0.0
	platformOrientation.pitchDegrees = 0.0
	platformOrientation.rollDegrees = 0.0
	platformOrientation.yawDegrees = 0.0
	ser = processPose(platformOrientation, baseOrientation, assemblyGeometry, ser, generatePlot, actuateLegs)

	# platformOrientation.zTranslation = 30.0
	# ser = processPose(platformOrientation, baseOrientation, assemblyGeometry, ser, generatePlot, actuateLegs)

	# platformOrientation.zTranslation = 20.0
	# ser = processPose(platformOrientation, baseOrientation, assemblyGeometry, ser, generatePlot, actuateLegs)

	# platformOrientation.zTranslation = 10.0
	# ser = processPose(platformOrientation, baseOrientation, assemblyGeometry, ser, generatePlot, actuateLegs)

	# platformOrientation.zTranslation = 0.0
	# ser = processPose(platformOrientation, baseOrientation, assemblyGeometry, ser, generatePlot, actuateLegs)

	# platformOrientation.zTranslation = -10.0
	# ser = processPose(platformOrientation, baseOrientation, assemblyGeometry, ser, generatePlot, actuateLegs)


	# # platformOrientation.pitchDegrees = 10.0
	# ser = processPose(platformOrientation, baseOrientation, assemblyGeometry, ser, generatePlot, actuateLegs)

	# platformOrientation.pitchDegrees = -10.0
	# ser = processPose(platformOrientation, baseOrientation, assemblyGeometry, ser, generatePlot, actuateLegs)

	# platformOrientation.pitchDegrees = -5.0
	# platformOrientation.rollDegrees = 3.0
	# ser = processPose(platformOrientation, baseOrientation, assemblyGeometry, ser, generatePlot, actuateLegs)

	# platformOrientation.zTranslation = 3.0
	# ser = processPose(platformOrientation, baseOrientation, assemblyGeometry, ser, generatePlot, actuateLegs)

	# platformOrientation.zTranslation = 6.0
	# ser = processPose(platformOrientation, baseOrientation, assemblyGeometry, ser, generatePlot, actuateLegs)

	# platformOrientation.zTranslation = 9.0
	# ser = processPose(platformOrientation, baseOrientation, assemblyGeometry, ser, generatePlot, actuateLegs)

	# platformOrientation.pitchDegrees = -8.0
	# platformOrientation.rollDegrees = 1.0
	# ser = processPose(platformOrientation, baseOrientation, assemblyGeometry, ser, generatePlot, actuateLegs)

	# platformOrientation.zTranslation = 15.0
	# ser = processPose(platformOrientation, baseOrientation, assemblyGeometry, ser, generatePlot, actuateLegs)

	# platformOrientation.xTranslation = 0.0
	# platformOrientation.yTranslation = 0.0
	# platformOrientation.zTranslation = 0.0
	# platformOrientation.pitchDegrees = 0.0
	# platformOrientation.rollDegrees = 0.0
	# platformOrientation.yawDegrees = 0.0
	# ser = processPose(platformOrientation, baseOrientation, assemblyGeometry, ser, generatePlot, actuateLegs)


	# print("Closing serial port")
	# ser.close()

	printy("Done...", "cB")


def just_plot():
	ser = None
	baseOrientation = orientation() #Initialize orientation class for base
	baseOrientation.xTranslation = 0
	baseOrientation.yTranslation = 0
	baseOrientation.zTranslation = 0
	baseOrientation.pitchDegrees = 0
	baseOrientation.rollDegrees = 0
	baseOrientation.yawDegrees = 0

	platformOrientation = orientation() #Initialize orientation class for platform

	platformOrientation.xTranslation = 0.0
	platformOrientation.yTranslation = 0.0
	platformOrientation.zTranslation = 52.2
	platformOrientation.pitchDegrees = 0.0
	platformOrientation.rollDegrees = 0.0
	platformOrientation.yawDegrees = 0.0
	ser = processPose(platformOrientation, baseOrientation, assemblyGeometry, ser, generatePlot, actuateLegs)

	printy("Done...", "cB")

just_plot()
