import stewartCalculations
import actuatorCommander
import plottingTools

import numpy as np
from printy import printy
import matplotlib.pyplot as plt


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

		self.platform_center_z = None

	def ingest_dict(self, settings_dict):
		#Config Parameters:
		self.r_B = settings_dict["r_B"]
		self.r_P = settings_dict["r_P"]
		self.actuatorClosedLength = settings_dict["actuatorClosedLength"]
		self.actuatorFullLength = settings_dict["actuatorFullLength"]
		self.actuatorStrokeFaultMargin = settings_dict["actuatorStrokeFaultMargin"]
		self.actuatorStrokeWarningMargin = settings_dict["actuatorStrokeWarningMargin"]
		self.baseAnchorAngleDegrees = settings_dict["baseAnchorAngleDegrees"]
		self.platformAnchorAngleDegrees = settings_dict["platformAnchorAngleDegrees"]
		self.refRotationDegrees = settings_dict["refRotationDegrees"]


		#Calculated Variables:
		self.actuatorHomeLength = self.actuatorClosedLength + (self.actuatorFullLength-self.actuatorClosedLength)/2
		self.psi_B = stewartCalculations.calcPsiB(self.baseAnchorAngleDegrees, self.refRotationDegrees) #Radians
		self.psi_P = stewartCalculations.calcPsiP(self.platformAnchorAngleDegrees, self.refRotationDegrees) #Radians

		self.stroke = self.actuatorFullLength-self.actuatorClosedLength
		self.warningMinLength = self.actuatorClosedLength + self.stroke*self.actuatorStrokeWarningMargin
		self.warningMaxLength = self.actuatorFullLength - self.stroke*self.actuatorStrokeWarningMargin
		self.faultMinLength = self.actuatorClosedLength + self.stroke*self.actuatorStrokeFaultMargin
		self.faultMaxLength = self.actuatorFullLength - self.stroke*self.actuatorStrokeFaultMargin
	
	def processPose(self, platformOrientation, baseOrientation, ser, generatePlot, actuateLegs):
		platform_coords, legLengths, base_coords, PV, dataString = stewartCalculations.PerformCalcs(baseOrientation=baseOrientation, platformOrientation=platformOrientation, assemblyGeometry=self)
		self.platform_center_z = np.mean(platform_coords[2, :])
		if actuateLegs:
			if (actuatorCommander.validateLegLengths(legLengths, self)):
				# ser = actuatorCommander.sendActuationCommandSingleLegWFeedback(legLengths, assemblyGeometry, ser)
				ser = actuatorCommander.sendActuationCommand(legLengths, self, ser)
			else:
				printy("Aborting actuation command to fault leg lengths", "rB")
		# else:
		# 	printy("Not actuating legs because actuateLegs flag is set to False", "rB")
		# 	print(",".join(f"{x:.1f}" for x in legLengths))

		if generatePlot:
			plottingTools.generate3DPlot(InitialViewElevationAngle=4, InitialViewAzimuthAngle=-78, platform_coords=platform_coords, legLengths=legLengths, base_coords=base_coords, PV=PV, dataString=dataString, assemblyGeometry=self)
		# else:
		# 	printy("Not generating plots because generatePlots flag is set to False", "rB")
			# input("Press Enter to continue to next pose...")


		plt.show()
		return ser, legLengths