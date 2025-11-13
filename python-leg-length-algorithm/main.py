#!/usr/bin/env python3 
import numpy as np
import os
import matplotlib.pyplot as plt
import serial
from printy import printy
import pyfiglet
import json

os.system('cls')
print(pyfiglet.figlet_format("Soloh Research", font = "slant"))
# np.seterr(divide='ignore')
# np.seterr(invalid='ignore')
# np.set_printoptions(suppress = True) #prevents printing arrays in scientific notation during debugging
# np.set_printoptions(linewidth=np.inf) #prevents line wrapping when printing arrays 
pi = np.pi

import classes

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
	actuateLegs = False
	generatePlot = True
	comport = "COM3"
	config_file = r"C:\Users\Brian\Desktop\Stewart Platform\Stewart_Platform\python-leg-length-algorithm\configs\OSBS_24.json"
	with open(config_file, "r") as f:
		platform_config_dict = json.load(f)


	assemblyGeometry = classes.SP_assemblyGeometry()

	assemblyGeometry.ingest_dict(platform_config_dict)


	ser = None
	baseOrientation = classes.orientation() #Initialize orientation class for base
	baseOrientation.xTranslation = 0
	baseOrientation.yTranslation = 0
	baseOrientation.zTranslation = 0.0
	baseOrientation.pitchDegrees = 0
	baseOrientation.rollDegrees = 0
	baseOrientation.yawDegrees = 0

	platformOrientation = classes.orientation() #Initialize orientation class for platform

	platformOrientation.xTranslation = 180.1253
	platformOrientation.yTranslation = 0.0
	platformOrientation.zTranslation = -92.8859
	platformOrientation.pitchDegrees = 0.0
	platformOrientation.rollDegrees = 0.0
	platformOrientation.yawDegrees = 0.0

	ser, results = assemblyGeometry.processPose(platformOrientation, baseOrientation, ser, generatePlot, actuateLegs)

	printy("Done...", "cB")

just_plot()
