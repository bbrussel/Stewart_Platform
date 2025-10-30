#!/usr/bin/env python3
import math
import numpy as np
from printy import printy
import plottingTools
pi = np.pi

class pointingVector():
	def __init__(self):
		self.azimuthAngle = None
		self.elevationAngle = None
		self.tip = None
		self.home = None


def getAzimuth(X, Y):
	azimuth = None
	if (X == 0.0) | (Y == 0.0) :
		if (Y == 0.0):
			if (X > 0.0):
				azimuth = 0.0
			else:
				azimuth = 180.0
		elif X == 0.0:
			if (Y > 0.0):
				azimuth = 270.0
			else:
				azimuth = 90.0
	else:
		if ((X >= 0.0) & (Y >= 0.0)):
			azimuth = 360 - math.degrees(math.atan(Y/X))

		elif ((X >= 0.0) & (Y <= 0.0)):
			azimuth = math.degrees(-math.atan(Y/X))

		elif ((X <= 0.0) & (Y <= 0.0)):
			azimuth = 180 - math.degrees(math.atan(Y/X))

		elif ((X <= 0.0) & (Y >= 0.0)):
			azimuth = 180 - math.degrees(math.atan(Y/X))

	return azimuth


def calcPsiB(baseAnchorAngleDegrees, refRotationDegrees):
	ref_rotation = .5*refRotationDegrees*np.pi/180
	gamma_B = .5*baseAnchorAngleDegrees*np.pi/180
	# Psi_B (Polar coordinates)
	psi_B = np.array([ 
		-gamma_B, 
		gamma_B,
		2*pi/3 - gamma_B, 
		2*pi/3 + gamma_B, 
		2*pi/3 + 2*pi/3 - gamma_B, 
		2*pi/3 + 2*pi/3 + gamma_B])

	psi_B = psi_B + np.repeat(ref_rotation, 6) #this is adding ref_rotation in radians to each value in the psi_B array



	return psi_B

def calcPsiP(platformAnchorAngleDegrees, refRotationDegrees):
	ref_rotation = .5*refRotationDegrees*np.pi/180
	gamma_P = .5*platformAnchorAngleDegrees*np.pi/180
	# psi_P (Polar coordinates)
	psi_P = np.array([ 
		pi/3 + 2*pi/3 + 2*pi/3 + gamma_P,
		pi/3 + -gamma_P, 
		pi/3 + gamma_P,
		pi/3 + 2*pi/3 - gamma_P, 
		pi/3 + 2*pi/3 + gamma_P, 
		pi/3 + 2*pi/3 + 2*pi/3 - gamma_P])
	psi_P = psi_P + np.repeat(ref_rotation, 6) #this is adding ref_rotation in radians to each value in the psi_P array


	return psi_P


#Rotation calculation functions
######################################################################################################################################
def rotX(phi):
	rotx = np.array([
		[1,     0    ,    0    ],
		[0,  np.cos(phi), -np.sin(phi)],
		[0, np.sin(phi), np.cos(phi)] ])
	return rotx

def rotY(theta):    
	roty = np.array([
		[np.cos(theta), 0, np.sin(theta) ],
		[0         , 1,     0       ],
		[-np.sin(theta), 0,  np.cos(theta) ] ])   
	return roty

def rotZ(psi):    
	rotz = np.array([
		[ np.cos(psi), -np.sin(psi), 0 ],
		[np.sin(psi), np.cos(psi), 0 ],
		[   0        ,     0      , 1 ] ])   
	return rotz
######################################################################################################################################

def calculateB(psi_B, r_B):
	# Coords for corners of base/bottom of legs.
	B = r_B * np.array( [
		[ np.cos(psi_B[0]), np.sin(psi_B[0]), 0],
		[ np.cos(psi_B[1]), np.sin(psi_B[1]), 0],
		[ np.cos(psi_B[2]), np.sin(psi_B[2]), 0],
		[ np.cos(psi_B[3]), np.sin(psi_B[3]), 0],
		[ np.cos(psi_B[4]), np.sin(psi_B[4]), 0],
		[ np.cos(psi_B[5]), np.sin(psi_B[5]), 0] ])
	B = np.transpose(B)

	return B

def calculateP(psi_P, r_P):

	#Defines shape of platform.  P is used later to apply a rotation matrix to when calculating a new position.  Notice P only occupies the XY Plane.
	P = r_P * np.array([ 
		[ np.cos(psi_P[0]),  np.sin(psi_P[0]), 0],
		[ np.cos(psi_P[1]),  np.sin(psi_P[1]), 0],
		[ np.cos(psi_P[2]),  np.sin(psi_P[2]), 0],
		[ np.cos(psi_P[3]),  np.sin(psi_P[3]), 0],
		[ np.cos(psi_P[4]),  np.sin(psi_P[4]), 0],
		[ np.cos(psi_P[5]),  np.sin(psi_P[5]), 0] ])
	P = np.transpose(P)

	return P

def calculateLegsAndBase(B, P, platform_home_transformation, baseOrientation, platformOrientation):
	# Init some temp variables used for calculations:
	l = np.zeros((3,6))

	platformTranslationVector = np.array([platformOrientation.xTranslation,platformOrientation.yTranslation,platformOrientation.zTranslation])  # Translation in X,Y,Z
	platformPitchRadians = platformOrientation.pitchDegrees*np.pi/180  #radians
	platformYawRadians = platformOrientation.yawDegrees*np.pi/180  #radians
	platformRollRadians = platformOrientation.rollDegrees*np.pi/180  #radians
	platformRotationVector = np.array([platformRollRadians, platformPitchRadians, platformYawRadians])  #radians


	basePitchRadians = baseOrientation.pitchDegrees*np.pi/180  #radians
	baseYawRadians = baseOrientation.yawDegrees*np.pi/180  #radians
	baseRollRadians = baseOrientation.rollDegrees*np.pi/180  #radians
	baseRotationVector = np.array([baseRollRadians, basePitchRadians, baseYawRadians])  #radians
	baseRotation = np.transpose(baseRotationVector)

	baseRotationX = rotX(baseRotation[0]);
	baseRotationY = rotY(baseRotation[1]);
	baseRotationZ = rotZ(baseRotation[2]);

	baseR = np.matmul(np.matmul(baseRotationZ, baseRotationY), baseRotationX)

	transformedBase = np.matmul(baseR, B) #Transform the home base position to return to be plotted etc.

	platformTrans = np.transpose(platformTranslationVector)
	platformRotation = np.transpose(platformRotationVector)
	platformRotationX = rotX(platformRotation[0]);
	platformRotationY = rotY(platformRotation[1]);
	platformRotationZ = rotZ(platformRotation[2]);

	platformR = np.matmul(np.matmul(platformRotationZ, platformRotationY), platformRotationX)

	# Get leg length for each leg.  np.newaxis is used to increase dimensions of an array.  axis=1 seems to choose whcih axis to expand into.

	platformTranslationContribution = np.repeat(platformTrans[:, np.newaxis], 6, axis=1)
	platformHomePositionContribution = np.repeat(platform_home_transformation[:, np.newaxis], 6, axis=1)

	platformRotationContribution = np.matmul(platformR, P)

	l = platformTranslationContribution + platformHomePositionContribution + platformRotationContribution - transformedBase

	legLengths = np.linalg.norm(l, axis=0)

	platform_coords = l + transformedBase



	return platform_coords, legLengths, transformedBase


def getElevation(X, Y, Z):
	elevation = None
	xyProjection = math.sqrt((Y**2) + (X**2))

	if xyProjection > 0:
		elevation = math.degrees(math.atan(Z/xyProjection))
	else:
		elevation = 90

	return elevation

def calcPlatformPointingVector(platformOrientation, platform_home_transformation):
	PV = pointingVector()
	pointingVectorLength = 40
	pointingVectorHome = [0,0,0]
	pointingVectorTip = [0,0,pointingVectorLength]
	platformTranslationVector = np.array([platformOrientation.xTranslation,platformOrientation.yTranslation,platformOrientation.zTranslation])
	platformPitchRadians = platformOrientation.pitchDegrees*np.pi/180  #radians
	platformYawRadians = platformOrientation.yawDegrees*np.pi/180  #radians
	platformRollRadians = platformOrientation.rollDegrees*np.pi/180  #radians
	platformRotationVector = np.array([platformRollRadians, platformPitchRadians, platformYawRadians])  #radians
	platformTrans = np.transpose(platformTranslationVector)
	platformRotation = np.transpose(platformRotationVector)
	platformRotationX = rotX(platformRotation[0]);
	platformRotationY = rotY(platformRotation[1]);
	platformRotationZ = rotZ(platformRotation[2]);
	platformR = np.matmul(np.matmul(platformRotationZ, platformRotationY), platformRotationX)
	pointingVectorHomeRotatation = np.matmul(platformR, pointingVectorHome)
	pointingVectorTipRotatation = np.matmul(platformR, pointingVectorTip)

	PV.home = platformTrans + pointingVectorHomeRotatation + platform_home_transformation
	PV.tip = platformTrans + pointingVectorTipRotatation + platform_home_transformation
	deltaX = PV.tip[0]-PV.home[0]
	deltaY = PV.tip[1]-PV.home[1]
	deltaZ = PV.tip[2]-PV.home[2]

	PV.azimuthAngle = getAzimuth(deltaX, deltaY)
	PV.elevationAngle = getElevation(deltaX, deltaY, deltaZ)
	# if plotPointingVector == True:
	# 	ax.plot([PVHome[0],PVTip[0]], [PVHome[1],PVTip[1]], [PVHome[2],PVTip[2]], color="red", linewidth=1, alpha=0.6)
	return PV


def PerformCalcs(baseOrientation, platformOrientation, assemblyGeometry):
	printy("\nPlatform and Base Geometry Initialization Variables:", "cB")
	printy("Base Radius = [cB]r_B@ = " + str(assemblyGeometry.r_B) + "mm")
	printy("Platform Radius = [cB]r_P@ = " + str(assemblyGeometry.r_P) + "mm")
	printy("Base anchor half-angle = [cB]baseAnchorAngleDegrees@ = " + "{0:.1f}".format(assemblyGeometry.baseAnchorAngleDegrees) + u'\N{DEGREE SIGN}')
	printy("Platform anchor half-angle = [cB]platformAnchorAngleDegrees@ = " + "{0:.1f}".format(assemblyGeometry.platformAnchorAngleDegrees) + u'\N{DEGREE SIGN}')
	printy("Actuator Home length = [cB]actuatorHomeLength@ = " + str(assemblyGeometry.actuatorHomeLength) + "mm")
	printy("Actuator Min length = [cB]actuatorClosedLength@ = " + str(assemblyGeometry.actuatorClosedLength) + "mm")
	printy("Actuator Max length = [cB]actuatorFullLength@ = " + str(assemblyGeometry.actuatorFullLength) + "mm")
	printy("System z-axis reference orientation = [cB]refRotationDegrees@ = " + str(assemblyGeometry.refRotationDegrees) + u'\N{DEGREE SIGN}')

	printy("\nInitializing platform data", "cB")

	B = calculateB(assemblyGeometry.psi_B, assemblyGeometry.r_B) # Calculates Base corner coords prior to applying tranforms for yaw, pitch, roll, etc.

	P = calculateP(assemblyGeometry.psi_P, assemblyGeometry.r_P) # Calculates Platform corner coords prior to applying tranforms for yaw, pitch, roll, etc.

	# Definition of the platform home position.
	z = np.sqrt(assemblyGeometry.actuatorHomeLength**2 - (P[0] - B[0])**2 - (P[1] - B[1])**2)

	# This is the transform to move P created above to its home position.
	platform_home_transformation = np.array([0, 0, z[0]])

	printy("Calculating Leg Lengths", "cB")
	platform_coords, legLengths, base_coords = calculateLegsAndBase(B, P, platform_home_transformation, baseOrientation, platformOrientation)

	printy("Calculating Pointing Vector", "cB")
	PV = calcPlatformPointingVector(platformOrientation, platform_home_transformation)

	printy("Generating Plot Info Message", "cB")
	dataString = plottingTools.generateDataString(platformOrientation, baseOrientation, platform_coords, base_coords, legLengths, PV.azimuthAngle, PV.elevationAngle, assemblyGeometry.actuatorFullLength, assemblyGeometry.actuatorClosedLength)

	return platform_coords, legLengths, base_coords, PV, dataString
