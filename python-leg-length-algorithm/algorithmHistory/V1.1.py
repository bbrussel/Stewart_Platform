#!/usr/bin/env python3 
import numpy as np
from stewartController import Stewart_Platform
from termcolor import colored
import os
os.system('clear')
np.seterr(divide='ignore')
np.seterr(invalid='ignore')
np.set_printoptions(suppress = True) #prevents printing arrays in scientific notation during debugging
np.set_printoptions(linewidth=np.inf) #prevents line wrapping when printing arrays 
pi = np.pi






######################################################################################################################################
#Initialization Variables:
r_B = 130           # Base radius
r_P = 130           # Platform Radius
actuatorHomeLength = 127            # Rod length
baseAnchorAngleDegrees = 32 # angle from center out to leg pair in degrees
platformAnchorAngleDegrees = 50 # angle from center out to leg pair in degrees
refRotationDegrees = 10    # Base rotation about Z axis

#Calculated Variables:
gamma_B = .5*baseAnchorAngleDegrees*np.pi/180      # Half of angle between two anchors on the base (radians)
gamma_P = .5*platformAnchorAngleDegrees*np.pi/180      # Half of angle between two anchors on the platform (radians)
ref_rotation = .5*refRotationDegrees*np.pi/180
######################################################################################################################################




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



def main():
	print(colored("\nPlatform Initialization Variables:", "cyan"))
	print("Base Radius = " + colored("r_B", "green") + " = " + str(r_B))
	print("Platform Radius = " + colored("r_P", "green") + " = " + str(r_P))
	print("Base anchor half-angle = " + colored("gamma_B", "green") + " = " + "{0:.3f}".format(gamma_B) + " radians")
	print("Platform anchor half-angle = " + colored("gamma_P", "green") + " = " + "{0:.3f}".format(gamma_P) + " radians")
	print("Actuator Home length = " + colored("actuatorHomeLength", "green") + " = " + str(actuatorHomeLength))

	print("Base Rotation = " + colored("ref_rotation", "green") + " = " + str(ref_rotation))

	print(colored("\nInitializing platform data...", "cyan"))

	# Psi_B (Polar coordinates)
	psi_B = np.array([ 
		-gamma_B, 
		gamma_B,
		2*pi/3 - gamma_B, 
		2*pi/3 + gamma_B, 
		2*pi/3 + 2*pi/3 - gamma_B, 
		2*pi/3 + 2*pi/3 + gamma_B])

	# psi_P (Polar coordinates)
	psi_P = np.array([ 
		pi/3 + 2*pi/3 + 2*pi/3 + gamma_P,
		pi/3 + -gamma_P, 
		pi/3 + gamma_P,
		pi/3 + 2*pi/3 - gamma_P, 
		pi/3 + 2*pi/3 + gamma_P, 
		pi/3 + 2*pi/3 + 2*pi/3 - gamma_P])

	psi_B = psi_B + np.repeat(ref_rotation, 6) #this is adding ref_rotation in radians to each value in the psi_B array
	psi_P = psi_P + np.repeat(ref_rotation, 6) #this is adding ref_rotation in radians to each value in the psi_P array
	
	# Coords for corners of base/bottom of legs.
	B = r_B * np.array( [
		[ np.cos(psi_B[0]), np.sin(psi_B[0]), 0],
		[ np.cos(psi_B[1]), np.sin(psi_B[1]), 0],
		[ np.cos(psi_B[2]), np.sin(psi_B[2]), 0],
		[ np.cos(psi_B[3]), np.sin(psi_B[3]), 0],
		[ np.cos(psi_B[4]), np.sin(psi_B[4]), 0],
		[ np.cos(psi_B[5]), np.sin(psi_B[5]), 0] ])
	B = np.transpose(B)

	#P is used later to apply a roation matrix to when calculating a new position.  Notice P only occupies the XY Plane.
	P = r_P * np.array([ 
		[ np.cos(psi_P[0]),  np.sin(psi_P[0]), 0],
		[ np.cos(psi_P[1]),  np.sin(psi_P[1]), 0],
		[ np.cos(psi_P[2]),  np.sin(psi_P[2]), 0],
		[ np.cos(psi_P[3]),  np.sin(psi_P[3]), 0],
		[ np.cos(psi_P[4]),  np.sin(psi_P[4]), 0],
		[ np.cos(psi_P[5]),  np.sin(psi_P[5]), 0] ])
	P = np.transpose(P)



	# Definition of the platform home position.
	z = np.sqrt( actuatorHomeLength**2 - (P[0] - B[0])**2 - (P[1] - B[1])**2)

	# This is the transform to move P created above to its home position.
	platform_home_transformation = np.array([0, 0, z[0]])

	print(colored("\npsi_B", "green") + ":")
	print("Calculation depends on " + colored("gamma_B", "green") + ", and " + colored("ref_rotatation", "green"))
	print(psi_B)

	print(colored("\npsi_P", "green") + ":")
	print("Calculation depends on " + colored("gamma_P", "green") + ", and " + colored("ref_rotatation", "green"))
	print(psi_P)

	print(colored("\nB (Bottom of legs)", "green") + ":")
	print("Calculation depends on " + colored("psi_B", "green") + ", and " + colored("r_B", "green"))
	# print(B)
	print("Formatted for readability of coordinates (x,y,z):")
	for i in range(0,6):
		print(str(i+1) + ": (" + "{0:.1f}".format(B[0][i]) + "," + "{0:.1f}".format(B[1][i]) + "," + "{0:.1f}".format(B[2][i]) + ")")




	print(colored("\nP", "green") + ":")
	print("Calculation depends on " + colored("psi_P", "green") + ", and " + colored("r_P", "green"))
	# print(P)
	print("Formatted for readability of coordinates (x,y,z):")
	for i in range(0,6):
		print(str(i+1) + ": (" + "{0:.1f}".format(P[0][i]) + "," + "{0:.1f}".format(P[1][i]) + "," + "{0:.1f}".format(P[2][i]) + ")")

	print(colored("\nz", "green") + ":")
	print("Calculation depends on " + colored("actuatorHomeLength", "green") + ", " + colored("P", "green") + ", and " + colored("B", "green"))
	print(z)

	print(colored("\nplatform_home_transformation.  If you tranform P with this matrix you get the platform's \"home\" position.", "green") + ":")
	print("Calculation depends on " + colored("z[0]", "green"))
	print("Depends only on z because the platform is assumed to be centered over the base in its home position")
	print("(" + "{0:.1f}".format(platform_home_transformation[0]) + "," + "{0:.1f}".format(platform_home_transformation[1]) + "," + "{0:.1f}".format(platform_home_transformation[2]) + ")")


	##At this point, the platform has been initialized

	print(colored("\n\n***********************************************************************************","cyan"))
	print(colored("***********************************************************************************","cyan"))
	print("Now calculate a new position")
	print(colored("***********************************************************************************","cyan"))
	print(colored("***********************************************************************************","cyan"))

	#Enter platform movement variables here:
	xTranslation = 0
	yTranslation = 0
	zTranslation = 0
	pitchDegrees = 2
	rollDegrees = 3
	yawDegrees = 1

	# Init some temp variables used for calculations:
	l = np.zeros((3,6))
	lll = np.zeros((6))

	print(colored("roll", "cyan") + ": " + str(rollDegrees) + u"\u00b0")
	print(colored("pitch", "cyan") + ": " + str(pitchDegrees) + u"\u00b0")
	print(colored("yaw", "cyan") + ": " + str(yawDegrees) + u"\u00b0")
	print(colored("x", "cyan") + ": " + str(xTranslation))
	print(colored("y", "cyan") + ": " + str(yTranslation))
	print(colored("z", "cyan") + ": " + str(zTranslation))

	translationVector = np.array([xTranslation,yTranslation,zTranslation])  # Translation in X,Y,Z
	pitchRadians = pitchDegrees*np.pi/180  #radians
	yawRadians = yawDegrees*np.pi/180  #radians
	rollRadians = rollDegrees*np.pi/180  #radians

	# print(colored("roll", "cyan") + ": " + str(rollRadians) + " rad")
	# print(colored("pitch", "cyan") + ": " + str(pitchRadians) + " rad")
	# print(colored("yaw", "cyan") + ": " + str(yawRadians) + " rad")


	rotationVector = np.array([rollRadians, pitchRadians, yawRadians])  #radians

	print(colored("\ntranslationVector", "green") + ":")
	print(translationVector)

	print(colored("rotationVector", "green") + ":")
	print(rotationVector)

	trans = np.transpose(translationVector)
	rotation = np.transpose(rotationVector)

	print(colored("trans", "green") + ":")
	print(trans)

	print(colored("rotation", "green") + ":")
	print(rotation)

	# Get rotation matrix of platform. matmul( matmul(rx,ry) , rz)

	rotationX = rotX(rotation[0]);
	rotationY = rotY(rotation[1]);
	rotationZ = rotZ(rotation[2]);

	print(colored("rotationX", "green") + ":")
	print(rotationX)

	print(colored("rotationY", "green") + ":")
	print(rotationY)

	print(colored("rotationZ", "green") + ":")
	print(rotationZ)

	R = np.matmul(np.matmul(rotationZ, rotationY), rotationX)


	print(colored("\nR (rotation matrix for platform)", "green") + ":")
	print(R)


	# Get leg length for each leg.  np.newaxis is used to increase dimensions of an array.  axis=1 seems to choose whcih axis to expand into.

	translationContribution = np.repeat(trans[:, np.newaxis], 6, axis=1)

	homePositionContribution = np.repeat(platform_home_transformation[:, np.newaxis], 6, axis=1)

	rotationContribution = np.matmul(R, P)



	print(colored("\ntranslationContribution", "green") + ":")
	print(translationContribution)

	print(colored("\nhomePositionContribution", "green") + ":")
	print(homePositionContribution)

	print(colored("\nrotationContribution", "green") + ":")
	print(rotationContribution)

	l = translationContribution + homePositionContribution + rotationContribution - B

	print(colored("\nl (" + u"\u25b3" + " from bottom of leg to top of leg)", "green") + ":")
	# print(l)
	print("Formatted for readability of coordinates (x,y,z):")
	for i in range(0,6):
		print(str(i+1) + ": (" + "{0:.1f}".format(l[0][i]) + "," + "{0:.1f}".format(l[1][i]) + "," + "{0:.1f}".format(l[2][i]) + ")")

	#Get norm for each leg.  axis=0 seems to make sure each leg is calc'd individually instead of norming the entire matrix.
	legLengths = np.linalg.norm(l, axis=0)
	print(colored("\nlegLengths", "green") + " (leg lengths):")
	print(legLengths)

	# Position of leg in global frame
	L = l + B
	# print(colored("\nL (Top of legs)", "green") + ":")
	# # print(L)
	# print("Formatted for readability of coordinates (x,y,z):")
	# for i in range(0,6):
	# 	print(str(i+1) + ": (" + "{0:.1f}".format(L[0][i]) + "," + "{0:.1f}".format(L[1][i]) + "," + "{0:.1f}".format(L[2][i]) + ")")




	

main()