#!/usr/bin/env python3
from printy import printy
import numpy as np
from mpl_toolkits.mplot3d import axes3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import mpl_toolkits.mplot3d.art3d as art3d
from matplotlib.patches import Circle
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
figureTitle = "Stewart Platform Model"

platFormFaceColor = '#268bd2'
platformAlpha = .6
platformEdgeColor = '#073642'
baseFaceColor = '#859900'
baseAlpha = .6
baseEdgeColor = '#073642'
legDefaultColor = '#073642'
legWarningColor = "orange"
legFaultColor = "red"
pvColor = "blue"


def plotLegs(ax, vec_arr_origin, vec_arr_dest, legLengths, assemblyGeometry):
	legCollection = []
	legLabels = []
	for i in range(6):
		origin = np.matrix([vec_arr_origin[0, i], vec_arr_origin[1, i], vec_arr_origin[2, i]])
		destination = np.matrix([vec_arr_dest[0, i], vec_arr_dest[1, i], vec_arr_dest[2, i]])
		middle = (destination[0]+origin[0])

		# ax.text(vec_arr_dest[0, i],vec_arr_dest[1, i],vec_arr_dest[2, i],  '%s' % (str(i+1)), size=10, zorder=1,  color='#586e75')
		label = ax.text(vec_arr_origin[0, i],vec_arr_origin[1, i],vec_arr_origin[2, i],  '%s' % (str(i+1)), size=10, zorder=1,  color='#586e75')

		legLabels.append(label)

		if (legLengths[i] < assemblyGeometry.warningMaxLength) & (legLengths[i] > assemblyGeometry.warningMinLength):
			leg = ax.plot([vec_arr_origin[0, i] , vec_arr_dest[0, i]], [vec_arr_origin[1, i], vec_arr_dest[1, i]], [vec_arr_origin[2, i],vec_arr_dest[2, i]], color=legDefaultColor, linewidth=1)
			print("{:.1f}".format(legLengths[i]))
		elif (legLengths[i] < assemblyGeometry.faultMaxLength) & (legLengths[i] > assemblyGeometry.faultMinLength):
			leg = ax.plot([vec_arr_origin[0, i] , vec_arr_dest[0, i]], [vec_arr_origin[1, i], vec_arr_dest[1, i]], [vec_arr_origin[2, i],vec_arr_dest[2, i]], color=legWarningColor, linewidth=1)
			printy("{:.1f}".format(legLengths[i]), "oB")
		else:
			leg = ax.plot([vec_arr_origin[0, i] , vec_arr_dest[0, i]], [vec_arr_origin[1, i], vec_arr_dest[1, i]], [vec_arr_origin[2, i],vec_arr_dest[2, i]], color=legFaultColor, linewidth=2)
			printy("{:.1f}".format(legLengths[i]), "rB")
		legCollection.append(leg[0])

	return ax, legCollection, legLabels


def generateDataString(platformOrientation, baseOrientation, platform_coords, base_coords, legLengths, azimuth, elevation):

	dataString = "Base:\n"
	dataString += "Roll: " + "{0:.1f}".format(baseOrientation.rollDegrees) + "$^\circ$\n"
	dataString += "Pitch: " + "{0:.1f}".format(baseOrientation.pitchDegrees) + "$^\circ$\n"
	dataString += "Yaw: " + "{0:.1f}".format(baseOrientation.yawDegrees) + "$^\circ$\n"
	dataString += "\nPlatform:\n"
	dataString += "Roll: " + "{0:.1f}".format(platformOrientation.rollDegrees) + "$^\circ$\n"
	dataString += "Pitch: " + "{0:.1f}".format(platformOrientation.pitchDegrees) + "$^\circ$\n"
	dataString += "Yaw: " + "{0:.1f}".format(platformOrientation.yawDegrees) + "$^\circ$\n"
	dataString += "\u0394X: " + str(platformOrientation.xTranslation) + "\n"
	dataString += "\u0394Y: " + str(platformOrientation.yTranslation) + "\n"
	dataString += "\u0394z: " + str(platformOrientation.zTranslation) + "\n"
	dataString += "\nAz: " + "{0:.1f}".format(azimuth) + "$^\circ$\n"
	dataString += "El: " + "{0:.1f}".format(elevation) + "$^\circ$\n"
	
	dataString += f"\nMax Z: {np.max(platform_coords[2, :]):.1f}\n"
	dataString += f"Min Z: {np.min(platform_coords[2, :]):.1f}\n"

	dataString += "\nLeg Lengths:\n"
	counter = 1
	for leg in legLengths:
		dataString += "(" + str(counter) + ") " +  "{0:.1f}".format(leg) + "\n"
		counter += 1

	return dataString

def generateAnimated3DPlot(ax, InitialViewElevationAngle, InitialViewAzimuthAngle, platform_coords, legLengths, base_coords, PV, dataString, assemblyGeometry):

	printy("Generating Animated Plot", "cB")
	ax, basePoly, platformPoly, legCollection, legLabels = createAnimated3DModel(ax, base_coords, platform_coords, legLengths, assemblyGeometry)
	plt.title("Stewart Platform")

	return ax, basePoly, platformPoly, legCollection, legLabels




def generate3DPlot(InitialViewElevationAngle, InitialViewAzimuthAngle, platform_coords, legLengths, base_coords, PV, dataString, assemblyGeometry):

	printy("Generating Plot", "cB")
	ax = create3DModel(base_coords, platform_coords, legLengths, assemblyGeometry)

	for mem in plt.gcf().texts:
		plt.gcf().texts.remove(mem)

	plt.title("Stewart Platform")

	# img = mpimg.imread('logo.png')
	# # Create an inset_axes instance with different parameters
	# axins = inset_axes(ax, width="5%", height="5%", loc='upper center')
	# # Turn off axis for the inset axes
	# axins.axis('off')
	# # Display image on the inset_axes
	# axins.imshow(img)

	dataText = plt.figtext(0.02, .1, dataString, fontsize=10)

	dataText.set_text(dataString)

	ax.plot([PV.home[0],PV.tip[0]], [PV.home[1],PV.tip[1]], [PV.home[2],PV.tip[2]], color=pvColor, linewidth=1, alpha=0.6)

	ax.view_init(elev=InitialViewElevationAngle, azim=InitialViewAzimuthAngle)


def create3DModel(Base, platform_coords, legLengths, assemblyGeometry):
	labelAxisTicks = False
	fig = plt.figure(figsize=(8, 6))  # e.g. 8x6 inches
	ax = fig.add_subplot(111, projection='3d')
	ax.set_xlim3d(-assemblyGeometry.r_B, assemblyGeometry.r_B)
	ax.set_ylim3d(-assemblyGeometry.r_B, assemblyGeometry.r_B)
	ax.set_zlim3d(0, assemblyGeometry.r_B*1.5)
	ax.set_xlabel('')
	ax.set_ylabel('')
	ax.set_zlabel('')

	ax.xaxis.pane.fill = False
	ax.yaxis.pane.fill = False
	ax.zaxis.pane.fill = False

	# Now set color to white (or whatever is "invisible")
	ax.xaxis.pane.set_edgecolor('w')
	ax.yaxis.pane.set_edgecolor('w')
	ax.zaxis.pane.set_edgecolor('w')

	if labelAxisTicks == False:
		ax.axes.xaxis.set_ticklabels([])
		ax.axes.yaxis.set_ticklabels([])
		ax.axes.zaxis.set_ticklabels([])

	ax.set_xlabel('x')
	ax.set_ylabel('y')
	ax.set_zlabel('z')


	ax.add_collection3d(Poly3DCollection([list(np.transpose(Base))], facecolors=baseFaceColor, alpha=baseAlpha, edgecolors=baseEdgeColor))
	ax.add_collection3d(Poly3DCollection([list(np.transpose(platform_coords))], facecolors=platFormFaceColor, alpha=platformAlpha, edgecolors=platformEdgeColor))
	plotLegs(ax, Base, platform_coords, legLengths, assemblyGeometry)

	return ax


def createAnimated3DModel(ax, Base, platform_coords, legLengths, assemblyGeometry):
	labelAxisTicks = False

	ax.set_xlim3d(-assemblyGeometry.r_B, assemblyGeometry.r_B)
	ax.set_ylim3d(-assemblyGeometry.r_B, assemblyGeometry.r_B)
	ax.set_zlim3d(0, assemblyGeometry.r_B*1.5)
	ax.set_xlabel('')
	ax.set_ylabel('')
	ax.set_zlabel('')

	ax.xaxis.pane.fill = False
	ax.yaxis.pane.fill = False
	ax.zaxis.pane.fill = False

	# Now set color to white (or whatever is "invisible")
	ax.xaxis.pane.set_edgecolor('w')
	ax.yaxis.pane.set_edgecolor('w')
	ax.zaxis.pane.set_edgecolor('w')

	if labelAxisTicks == False:
		ax.axes.xaxis.set_ticklabels([])
		ax.axes.yaxis.set_ticklabels([])
		ax.axes.zaxis.set_ticklabels([])

	ax.set_xlabel('x')
	ax.set_ylabel('y')
	ax.set_zlabel('z')


	basePoly = ax.add_collection3d(Poly3DCollection([list(np.transpose(Base))], facecolors=baseFaceColor, alpha=baseAlpha, edgecolors=baseEdgeColor))
	platformPoly = ax.add_collection3d(Poly3DCollection([list(np.transpose(platform_coords))], facecolors=platFormFaceColor, alpha=platformAlpha, edgecolors=platformEdgeColor))
	ax, legCollection, legLabels = plotLegs(ax, Base, platform_coords, legLengths, assemblyGeometry)

	return ax, basePoly, platformPoly, legCollection, legLabels


