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


		leg = ax.plot([vec_arr_origin[0, i] , vec_arr_dest[0, i]], [vec_arr_origin[1, i], vec_arr_dest[1, i]], [vec_arr_origin[2, i],vec_arr_dest[2, i]], color=legDefaultColor, linewidth=1)
		# print("{:.1f}".format(legLengths[i]))

		legCollection.append(leg[0])

	return ax, legCollection, legLabels



def generate3DPlot(InitialViewElevationAngle, InitialViewAzimuthAngle, L, legLengths, B, PV, assemblyGeometry):

	printy("Generating Plot", "cB")
	ax = create3DModel(B, L, legLengths, assemblyGeometry)

	for mem in plt.gcf().texts:
		plt.gcf().texts.remove(mem)

	plt.title("Heliospace Stewart Platform")

	ax.plot([PV.home[0],PV.tip[0]], [PV.home[1],PV.tip[1]], [PV.home[2],PV.tip[2]], color=pvColor, linewidth=1, alpha=0.6)

	ax.view_init(elev=InitialViewElevationAngle, azim=InitialViewAzimuthAngle)


def create3DModel(Base, L, legLengths, assemblyGeometry):
	labelAxisTicks = False
	ax = plt.axes(projection='3d') # Data for a three-dimensional line
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
	ax.add_collection3d(Poly3DCollection([list(np.transpose(L))], facecolors=platFormFaceColor, alpha=platformAlpha, edgecolors=platformEdgeColor))
	plotLegs(ax, Base, L, legLengths, assemblyGeometry)

	return ax





