#!/usr/bin/env python3 
import numpy as np
import os
from pathlib import Path
import serial
from printy import printy
import pyfiglet
import json
import time

os.system('cls')
print(pyfiglet.figlet_format("Soloh Research", font = "slant"))
pi = np.pi

import classes

def demo():
	actuateLegs = False
	generatePlot = True
	comport = "COM6"

	config_file = r"C:\Users\Brian\Desktop\Stewart Platform\Stewart_Platform\python-leg-length-algorithm\configs\EDU-1.json"
	with open(config_file, "r") as f:
		platform_config_dict = json.load(f)
	assemblyGeometry = classes.SP_assemblyGeometry()

	assemblyGeometry.ingest_dict(Path(config_file).stem, platform_config_dict)
	print("Loading settings for platform from " + os.path.basename(config_file))

	if actuateLegs == True:
		ser = serial.Serial(port=comport, baudrate=115200, timeout=0.1, write_timeout=0.5)
		ser.reset_input_buffer()
		ser.reset_output_buffer()
	else:
		ser = None

	baseOrientation = classes.orientation() #Initialize orientation class for base
	baseOrientation.xTranslation = 0
	baseOrientation.yTranslation = 0
	baseOrientation.zTranslation = 0
	baseOrientation.pitchDegrees = 0
	baseOrientation.rollDegrees = 0
	baseOrientation.yawDegrees = 0
	baseOrientation.pumpDistance = 0.0

	platformOrientation = classes.orientation() #Initialize orientation class for platform
	platformOrientation.xTranslation = -70.0
	platformOrientation.yTranslation = -280.0
	platformOrientation.zTranslation = -150.0
	platformOrientation.pitchDegrees = 10.0
	platformOrientation.rollDegrees = 10.0
	platformOrientation.yawDegrees = 0.0
	platformOrientation.pumpDistance = 0.0

	ser, results = assemblyGeometry.processPose(platformOrientation, baseOrientation, ser, generatePlot, actuateLegs)

	if ser is not None:
		time.sleep(0.1)  # Give device time to respond
		while ser.in_waiting > 0:
			response = ser.readline().decode('utf-8', errors='ignore').strip()
			if response:
				print(f"Device response: {response}")

	print("Closing serial port")
	if ser is not None:
		ser.close()

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
	baseOrientation.xTranslation = 0.0
	baseOrientation.yTranslation = 0.0
	baseOrientation.zTranslation = 0.0
	baseOrientation.pitchDegrees = 0.0
	baseOrientation.rollDegrees = 0.0
	baseOrientation.yawDegrees = 0.0

	platformOrientation = classes.orientation() #Initialize orientation class for platform

	platformOrientation.xTranslation = 0.0
	platformOrientation.yTranslation = 0.0
	platformOrientation.zTranslation = 0.0
	platformOrientation.pitchDegrees = 0.0
	platformOrientation.rollDegrees = 0.0
	platformOrientation.yawDegrees = 0.0

	ser, results = assemblyGeometry.processPose(platformOrientation, baseOrientation, ser, generatePlot, actuateLegs)

	printy("Done...", "cB")


demo()
# just_plot()
