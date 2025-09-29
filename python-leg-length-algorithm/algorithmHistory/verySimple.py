#!/usr/bin/env python3
import numpy as np
from mpl_toolkits.mplot3d import axes3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import mpl_toolkits.mplot3d.art3d as art3d
from matplotlib.patches import Circle
import matplotlib.pyplot as plt
np.set_printoptions(suppress = True) #prevents printing arrays in scientific notation during debugging
np.set_printoptions(linewidth=np.inf) #prevents line wrapping when printing arrays 
pi = np.pi

r_P = 130           # Platform Radius
platformAnchorAngleDegrees = 50 # angle from center out to leg pair in degrees
gamma_P = .5*platformAnchorAngleDegrees*np.pi/180      # Half of angle between two anchors on the platform (radians)
ref_rotation = 0.0


# psi_P (Polar coordinates)
psi_P = np.array([ 
	pi/3 + 2*pi/3 + 2*pi/3 + gamma_P,
	pi/3 + -gamma_P, 
	pi/3 + gamma_P,
	pi/3 + 2*pi/3 - gamma_P, 
	pi/3 + 2*pi/3 + gamma_P, 
	pi/3 + 2*pi/3 + 2*pi/3 - gamma_P])
psi_P = psi_P + np.repeat(ref_rotation, 6) #this is adding ref_rotation in radians to each value in the psi_P array

P = r_P * np.array([ 
	[ np.cos(psi_P[0]),  np.sin(psi_P[0]), 0],
	[ np.cos(psi_P[1]),  np.sin(psi_P[1]), 0],
	[ np.cos(psi_P[2]),  np.sin(psi_P[2]), 0],
	[ np.cos(psi_P[3]),  np.sin(psi_P[3]), 0],
	[ np.cos(psi_P[4]),  np.sin(psi_P[4]), 0],
	[ np.cos(psi_P[5]),  np.sin(psi_P[5]), 0] ])
P = np.transpose(P)

pitchDegrees = 10.0
rollDegrees = 10.0
yawDegrees = 0.0



pitchRadians = pitchDegrees*np.pi/180  #radians
yawRadians = yawDegrees*np.pi/180  #radians
rollRadians = rollDegrees*np.pi/180  #radians

rx = np.array([
		[ 1, 0, 0 ],
		[0, np.cos(rollRadians), -np.sin(rollRadians) ],
		[0, np.sin(rollRadians), np.cos(rollRadians) ] ])

ry = np.array([
		[ np.cos(pitchRadians), 0, np.sin(pitchRadians)],
		[0, 1, 0],
		[-np.sin(pitchRadians), 0, np.cos(pitchRadians) ] ])


rz = np.array([
		[ np.cos(yawRadians), -np.sin(yawRadians), 0 ],
		[np.sin(yawRadians), np.cos(yawRadians), 0 ],
		[   0        ,     0      , 1 ] ])


R2 = np.matmul(np.matmul(rz, ry), rx)
rotated2 = np.matmul(R2, P)


alpha = yawRadians
beta = pitchRadians
gamma = rollRadians

combined = np.array([

		[ np.cos(alpha)*np.cos(beta),        np.cos(alpha)*np.sin(beta)*np.sin(gamma)-np.sin(alpha)*np.cos(gamma),      np.cos(alpha)*np.sin(beta)*np.cos(gamma)+np.sin(alpha)*np.sin(gamma) ],
		[ np.sin(alpha)*np.cos(beta),        np.sin(alpha)*np.sin(beta)*np.sin(gamma)+np.cos(alpha)*np.cos(gamma),      np.sin(alpha)*np.sin(beta)*np.cos(gamma)-np.cos(alpha)*np.sin(gamma) ],
		[   -np.sin(beta)        ,     np.cos(beta)*np.sin(gamma)        , np.cos(beta)*np.cos(gamma)] ])

rotated3 = np.matmul(combined, P)




ax = plt.axes(projection='3d') # Data for a three-dimensional line

ax.set_xlim3d(-150, 150)
ax.set_ylim3d(-150, 150)
ax.set_zlim3d(0, 150)
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

ax.add_collection3d(Poly3DCollection([list(np.transpose(P))], facecolors='#268bd2', alpha=0.6, edgecolors='#073642'))

ax.add_collection3d(Poly3DCollection([list(np.transpose(rotated2))], facecolors='cyan', alpha=0.6, edgecolors='#073642'))

ax.add_collection3d(Poly3DCollection([list(np.transpose(rotated3))], facecolors='magenta', alpha=0.6, edgecolors='#073642'))


for i in range(1,6):

	ax.text(P[0,i],P[1,i],P[2,i],  "%.1f" % P[0,i] + "," + "%.1f" % P[1,i] + "," + "%.1f" % P[2,i], size=10, zorder=1,  color='#586e75')

	ax.text(rotated3[0,i],rotated3[1,i],rotated3[2,i],  "%.1f" % rotated3[0,i] + "," + "%.1f" % rotated3[1,i] + "," + "%.1f" % rotated3[2,i], size=10, zorder=1,  color='#586e75')


ax.set_aspect('auto')

# platformPatch = Circle((0, 0), 130, fill=False, alpha=.5, edgecolor='#073642')
# ax.add_patch(platformPatch)
# art3d.pathpatch_2d_to_3d(platformPatch, z=0, zdir='z')



plt.show()