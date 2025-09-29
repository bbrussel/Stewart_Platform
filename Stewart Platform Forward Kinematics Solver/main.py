#!/usr/bin/env python3 
import numpy as np
import os
import math
from printy import printy
import pyfiglet
from datetime import datetime
import time
os.system('cls')
print(pyfiglet.figlet_format("Heliospace"))

pi = np.pi
import stewartCalculations


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
comport = "COM4"

assemblyGeometry = SP_assemblyGeometry()
assemblyGeometry.r_B = 220           # Base radius
assemblyGeometry.r_P = 220           # Platform Radius
assemblyGeometry.actuatorClosedLength = 152
assemblyGeometry.actuatorFullLength = 252

assemblyGeometry.baseAnchorAngleDegrees = 32 # angle from center out to leg pair in degrees
assemblyGeometry.platformAnchorAngleDegrees = 50 # angle from center out to leg pair in degrees
assemblyGeometry.refRotationDegrees = 0    # Assembly oriention around z axis

#Calculated Variables:
assemblyGeometry.actuatorHomeLength = assemblyGeometry.actuatorClosedLength + (assemblyGeometry.actuatorFullLength-assemblyGeometry.actuatorClosedLength)/2
assemblyGeometry.psi_B = stewartCalculations.calcPsiB(assemblyGeometry.baseAnchorAngleDegrees, assemblyGeometry.refRotationDegrees) #Radians
assemblyGeometry.psi_P = stewartCalculations.calcPsiP(assemblyGeometry.platformAnchorAngleDegrees, assemblyGeometry.refRotationDegrees) #Radians

assemblyGeometry.stroke = assemblyGeometry.actuatorFullLength-assemblyGeometry.actuatorClosedLength




starting_pitch_range=14.7
starting_roll_range=13.1
starting_yaw_range=25.4

initialStepSize = 2



#For a pitch of 5.0 and a roll of 7.0, we should expect the following leg lengths: [173.4312286377, 201.2346649170, 226.1464691162, 228.8561859131, 207.9405059814, 174.8859558105]

def searchRange(stepSize, pitch_lower, pitch_upper, yaw_lower, yaw_upper, roll_lower, roll_upper, platformOrientation, baseOrientation, assemblyGeometry, matchingLegLengths):
	lowestDiff = None
	closestPitch = None
	closestRoll = None
	closestYaw = None
	counter = 0
	startTime = datetime.now()
	for pitch in np.arange(pitch_lower, pitch_upper, stepSize):
		for roll in np.arange(roll_lower, roll_upper, stepSize):
			for yaw in np.arange(yaw_lower, yaw_upper, stepSize):
				counter += 1
				platformOrientation.xTranslation = 0
				platformOrientation.yTranslation = 0
				platformOrientation.zTranslation = 0
				platformOrientation.pitchDegrees = pitch
				platformOrientation.rollDegrees = roll
				platformOrientation.yawDegrees = yaw
				L, legLengths, B, PV = stewartCalculations.PerformCalcs(baseOrientation=baseOrientation, platformOrientation=platformOrientation, assemblyGeometry=assemblyGeometry)
				absolute_differences = np.abs(matchingLegLengths - legLengths)
				average_absolute_difference = np.mean(absolute_differences)
				if lowestDiff is None:
					lowestDiff = average_absolute_difference
					closestPitch = pitch
					closestRoll = roll
					closestYaw = yaw
				elif average_absolute_difference < lowestDiff:
					lowestDiff = average_absolute_difference
					closestPitch = pitch
					closestRoll = roll
					closestYaw = yaw


	# print("\nSearched between:")
	# print("Pitch:" + str(pitch_lower) + " and " + str(pitch_upper))
	# print("Roll:" + str(roll_lower) + " and " + str(roll_upper))
	# print("Yaw:" + str(yaw_lower) + " and " + str(yaw_upper))
	# print(str(counter) + " points sampled in " + str(datetime.now() - startTime) + " seconds")
	# print("Lowest Average Difference:" + str(lowestDiff))
	# print("Pitch: {:.2f}".format(closestPitch))
	# print("Roll: {:.2f}".format(closestRoll))
	# print("Yaw: {:.2f}".format(closestYaw))

	return closestPitch, closestRoll, closestYaw

def demo():

	totalStartTime = datetime.now()
	matchingLegLengths = np.array([160.2422790527, 176.4485626221, 205.8580322266, 246.5520935059, 234.4741058350, 190.7434082031])

	platformOrientation = orientation() #Initialize orientation class for platform
	baseOrientation = orientation() #Initialize orientation class for base
	baseOrientation.xTranslation = 0 #Not sure these are relevant for the base, but are included in the algorithm anyways.
	baseOrientation.yTranslation = 0 #Not sure these are relevant for the base, but are included in the algorithm anyways.
	baseOrientation.zTranslation = 0 #Not sure these are relevant for the base, but are included in the algorithm anyways.
	baseOrientation.pitchDegrees = 0 
	baseOrientation.rollDegrees = 0
	baseOrientation.yawDegrees = 0

	pitch_lower = -starting_pitch_range
	pitch_upper = starting_pitch_range
	roll_lower = -starting_roll_range
	roll_upper = starting_roll_range
	yaw_lower = -starting_yaw_range
	yaw_upper = starting_yaw_range
	

	pitch, roll, yaw = searchRange(initialStepSize, pitch_lower, pitch_upper, yaw_lower, yaw_upper, roll_lower, roll_upper, platformOrientation, baseOrientation, assemblyGeometry, matchingLegLengths)

	pitch_lower = pitch-1
	pitch_upper = pitch+1
	roll_lower = roll-1
	roll_upper = roll+1
	yaw_lower = yaw-1
	yaw_upper = yaw+1
	
	pitch, roll, yaw = searchRange(.3, pitch_lower, pitch_upper, yaw_lower, yaw_upper, roll_lower, roll_upper, platformOrientation, baseOrientation, assemblyGeometry, matchingLegLengths)

	pitch_lower = pitch-.5
	pitch_upper = pitch+.5
	roll_lower = roll-.5
	roll_upper = roll+.5
	yaw_lower = yaw-.5
	yaw_upper = yaw+.5
	
	pitch, roll, yaw = searchRange(.1, pitch_lower, pitch_upper, yaw_lower, yaw_upper, roll_lower, roll_upper, platformOrientation, baseOrientation, assemblyGeometry, matchingLegLengths)


	print("Pitch: {:.2f}".format(pitch))
	print("Roll: {:.2f}".format(roll))
	print("Yaw: {:.2f}".format(yaw))
	print("Elapsed time: " + str(datetime.now()-totalStartTime))


	# L, legLengths, B, PV, dataString = stewartCalculations.PerformCalcs(baseOrientation=baseOrientation, platformOrientation=platformOrientation, assemblyGeometry=assemblyGeometry)


demo()

# stepSize = 1
# center = 0
# width = 5
# lowerBound = center - width
# upperBound = center + width + stepSize

# for pitch in np.arange(lowerBound, upperBound, stepSize):
# 	print(pitch)