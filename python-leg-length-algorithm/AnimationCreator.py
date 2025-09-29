#!/usr/bin/env python3 
import numpy as np
import os
import glob
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import serial
from printy import printy
import pyfiglet
import pandas
from PIL import Image
os.system('cls')
print(pyfiglet.figlet_format("Heliospace"))
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


assemblyGeometry = SP_assemblyGeometry()
assemblyGeometry.r_B = 130           # Base radius
assemblyGeometry.r_P = 130           # Platform Radius
assemblyGeometry.actuatorClosedLength = 102
assemblyGeometry.actuatorFullLength = 152

assemblyGeometry.actuatorStrokeFaultMargin = .03
assemblyGeometry.actuatorStrokeWarningMargin = .1

assemblyGeometry.baseAnchorAngleDegrees = 32 # angle from center out to leg pair in degrees
assemblyGeometry.platformAnchorAngleDegrees = 50 # angle from center out to leg pair in degrees
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



def createAnimation():


	inputFile = 'animations/Inputs/Random Base Movement w Pitch Sweep.xlsx'
	excel_data_df = pandas.read_excel(inputFile, sheet_name='Sheet1')

	caseName = os.path.basename(inputFile).split(".")[0]

	platformYaw = excel_data_df.iloc[1:, 0]
	platformPitch = excel_data_df.iloc[1:, 1]
	platformRoll = excel_data_df.iloc[1:, 2]
	platformXtranslation = excel_data_df.iloc[1:, 3]
	platformYtranslation = excel_data_df.iloc[1:, 4]
	platformZtranslation = excel_data_df.iloc[1:, 5]

	baseYaw = excel_data_df.iloc[1:, 6]
	basePitch = excel_data_df.iloc[1:, 7]
	baseRoll = excel_data_df.iloc[1:, 8]

	files = glob.glob('animations/Outputs/*.png')
	for f in files:
		os.remove(f)

	platformOrientation = orientation() #Initialize orientation class for platform
	baseOrientation = orientation() #Initialize orientation class for base
	for i in range(1,len(platformYaw)):
		print(i)

		platformOrientation.xTranslation = platformXtranslation[i]
		platformOrientation.yTranslation = platformYtranslation[i]
		platformOrientation.zTranslation = platformZtranslation[i]

		platformOrientation.pitchDegrees = platformPitch[i]
		platformOrientation.rollDegrees = platformRoll[i]
		platformOrientation.yawDegrees = platformYaw[i]

		baseOrientation.pitchDegrees = basePitch[i]
		baseOrientation.rollDegrees = baseRoll[i]
		baseOrientation.yawDegrees = baseYaw[i]

		L, legLengths, B, PV, dataString = stewartCalculations.PerformCalcs(baseOrientation=baseOrientation, platformOrientation=platformOrientation, assemblyGeometry=assemblyGeometry)

		plottingTools.generate3DPlot(InitialViewElevationAngle=4, InitialViewAzimuthAngle=-78, L=L, legLengths=legLengths, B=B, PV=PV, dataString=dataString, assemblyGeometry=assemblyGeometry)

		plt.savefig("animations/Outputs/" + str(i).zfill(4) + ".png")

		plt.close()

	frames = []
	imgs = glob.glob("animations/Outputs/*.png")
	for i in imgs:
	    new_frame = Image.open(i)
	    frames.append(new_frame)
	 
	# Save into a GIF file that loops forever
	frames[0].save('animations/Outputs/' + caseName + '.gif', format='GIF',append_images=frames[1:],save_all=True,duration=300, loop=0)

	files = glob.glob('animations/Outputs/*.png')
	for f in files:
		os.remove(f)


def createAnimatedPlot():

	inputFile = 'animations/Inputs/Random Base Movement w Pitch Sweep.xlsx'
	excel_data_df = pandas.read_excel(inputFile, sheet_name='Sheet1')

	caseName = os.path.basename(inputFile).split(".")[0]

	platformYaw = excel_data_df.iloc[1:, 0]
	platformPitch = excel_data_df.iloc[1:, 1]
	platformRoll = excel_data_df.iloc[1:, 2]
	platformXtranslation = excel_data_df.iloc[1:, 3]
	platformYtranslation = excel_data_df.iloc[1:, 4]
	platformZtranslation = excel_data_df.iloc[1:, 5]

	baseYaw = excel_data_df.iloc[1:, 6]
	basePitch = excel_data_df.iloc[1:, 7]
	baseRoll = excel_data_df.iloc[1:, 8]

	platformOrientation = orientation() #Initialize orientation class for platform
	baseOrientation = orientation() #Initialize orientation class for base

	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')

	plt.ion()


	platformPoly = ax.add_collection3d(Poly3DCollection([]))
	basePoly = ax.add_collection3d(Poly3DCollection([]))
	legCollection = []
	legLabels = []

	for i in range(1,len(platformYaw)):
		print(i)

		platformOrientation.xTranslation = platformXtranslation[i]
		platformOrientation.yTranslation = platformYtranslation[i]
		platformOrientation.zTranslation = platformZtranslation[i]

		platformOrientation.pitchDegrees = platformPitch[i]
		platformOrientation.rollDegrees = platformRoll[i]
		platformOrientation.yawDegrees = platformYaw[i]

		baseOrientation.pitchDegrees = basePitch[i]
		baseOrientation.rollDegrees = baseRoll[i]
		baseOrientation.yawDegrees = baseYaw[i]

		L, legLengths, B, PV, dataString = stewartCalculations.PerformCalcs(baseOrientation=baseOrientation, platformOrientation=platformOrientation, assemblyGeometry=assemblyGeometry)


		basePoly.remove()
		platformPoly.remove()
		for leg in legCollection:
			leg.remove()
		for label in legLabels:
			label.remove()

		ax, basePoly, platformPoly, legCollection, legLabels = plottingTools.generateAnimated3DPlot(ax=ax, InitialViewElevationAngle=4, InitialViewAzimuthAngle=-78, L=L, legLengths=legLengths, B=B, PV=PV, dataString=dataString, assemblyGeometry=assemblyGeometry)
		
		plt.draw()
		plt.pause(0.1)




	
# createAnimation()
createAnimatedPlot()

