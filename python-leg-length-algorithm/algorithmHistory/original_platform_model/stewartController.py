import numpy as np
from mpl_toolkits.mplot3d import axes3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt

#This code is modified frmo Yeok 2022 Stewart Platform Implimentation
#https://github.com/Yeok-c/Stewart_Py

class Stewart_Platform(object):   
    def __init__(s, r_B, r_P, lhl, ldl, gamma_B, gamma_P, ref_rotation, actuatorClosedLength, actuatorStrokedLength, actuatorStrokeMargin):
        pi = np.pi
        beta = np.array([ 
            pi/2 + pi,        
            pi/2,
            2*pi/3 + pi/2 + pi , 
            2*pi/3 + pi/2,
            4*pi/3 + pi/2 + pi , 
            4*pi/3 + pi/2] )

        # Psi_B (Polar coordinates)
        psi_B = np.array([ 
            -gamma_B, 
            gamma_B,
            2*pi/3 - gamma_B, 
            2*pi/3 + gamma_B, 
            2*pi/3 + 2*pi/3 - gamma_B, 
            2*pi/3 + 2*pi/3 + gamma_B])

        # psi_P (Polar coordinates)
        # Direction of the points where the rod is attached to the platform.
        psi_P = np.array([ 
            pi/3 + 2*pi/3 + 2*pi/3 + gamma_P,
            pi/3 + -gamma_P, 
            pi/3 + gamma_P,
            pi/3 + 2*pi/3 - gamma_P, 
            pi/3 + 2*pi/3 + gamma_P, 
            pi/3 + 2*pi/3 + 2*pi/3 - gamma_P])

        psi_B = psi_B + np.repeat(ref_rotation, 6)
        psi_P = psi_P + np.repeat(ref_rotation, 6)
        beta = beta + np.repeat(ref_rotation, 6)

        # Coordinate of the points where servo arms 
        # are attached to the corresponding servo axis.
        B = r_B * np.array( [ 
            [ np.cos(psi_B[0]), np.sin(psi_B[0]), 0],
            [ np.cos(psi_B[1]), np.sin(psi_B[1]), 0],
            [ np.cos(psi_B[2]), np.sin(psi_B[2]), 0],
            [ np.cos(psi_B[3]), np.sin(psi_B[3]), 0],
            [ np.cos(psi_B[4]), np.sin(psi_B[4]), 0],
            [ np.cos(psi_B[5]), np.sin(psi_B[5]), 0] ])
        B = np.transpose(B)
            
        # Coordinates of the points where the rods 
        # are attached to the platform.
        P = r_P * np.array([ 
            [ np.cos(psi_P[0]),  np.sin(psi_P[0]), 0],
            [ np.cos(psi_P[1]),  np.sin(psi_P[1]), 0],
            [ np.cos(psi_P[2]),  np.sin(psi_P[2]), 0],
            [ np.cos(psi_P[3]),  np.sin(psi_P[3]), 0],
            [ np.cos(psi_P[4]),  np.sin(psi_P[4]), 0],
            [ np.cos(psi_P[5]),  np.sin(psi_P[5]), 0] ])
        P = np.transpose(P)

        # Save initialized variables
        s.r_B = r_B
        s.r_P = r_P
        s.lhl = lhl
        s.ldl = ldl
        s.gamma_B = gamma_B
        s.gamma_P = gamma_P

        # Calculated params
        s.beta = beta
        s.psi_B = psi_B
        s.psi_P = psi_P
        s.B = B
        s.P = P

        s.azimuthAngle = None
        s.elevationAngle = None

        # Definition of the platform home position.
        z = np.sqrt( s.ldl**2 + s.lhl**2 - (s.P[0] - s.B[0])**2 - (s.P[1] - s.B[1])**2)
        s. home_pos= np.array([0, 0, z[0] ])
        # s.home_pos = np.transpose(home_pos)

        # Allocate for variables
        s.l = np.zeros((3,6))
        s.lll = np.zeros((6))
        s.angles = np.zeros((6))
        s.H = np.zeros((3,6)) 
        s.actuatorClosedLength = actuatorClosedLength
        s.actuatorStrokedLength = actuatorStrokedLength
        s.actuatorStrokeMargin = actuatorStrokeMargin

    def calculate(s, trans, rotation):
        trans = np.transpose(trans)
        rotation = np.transpose(rotation)

        # Get rotation matrix of platform. RotZ* RotY * RotX -> matmul
        R = np.matmul( np.matmul(s.rotX(rotation[0]), s.rotY(rotation[1])), s.rotZ(rotation[2]) )

        # Get leg length for each leg
        s.l = np.repeat(trans[:, np.newaxis], 6, axis=1) + np.repeat(s.home_pos[:, np.newaxis], 6, axis=1) + np.matmul(R, s.P) - s.B 
        s.lll = np.linalg.norm(s.l, axis=0)

        # Position of leg in global frame
        s.L = s.l + s.B

        # Position of legs, wrt to their individual bases, split for clarity.
        lx = s.l[0, :]
        ly = s.l[1, :]
        lz = s.l[2, :]

        # Calculate auxiliary quatities g, f and e
        g = s.lll**2 - ( s.ldl**2 - s.lhl**2 )
        e = 2 * s.lhl * lz

        # Calculate servo angles for each leg
        for k in range(6):
            fk = 2 * s.lhl * (np.cos(s.beta[k]) * lx[k] + np.sin(s.beta[k]) * ly[k])
            
            # The wanted position could be achieved if the solution of this
            # equation is real for all i
            s.angles[k] = np.arcsin(g[k] / np.sqrt(e[k]**2 + fk**2)) - np.arctan2(fk,e[k])
            
            # Get postion of the point where a spherical joint connects servo arm and rod.
            s.H[:, k] = np.transpose([ s.lhl * np.cos(s.angles[k]) * np.cos(s.beta[k]) + s.B[0,k],s.lhl * np.cos(s.angles[k]) * np.sin(s.beta[k]) + s.B[1,k], s.lhl * np.sin(s.angles[k]) ])
        
        return s.angles, s.lll

    def plot3D_line(s, ax, vec_arr_origin, vec_arr_dest, color_):
        strokeRange = s.actuatorStrokedLength - s.actuatorClosedLength
        strokeMargin = s.actuatorStrokeMargin*strokeRange
        for i in range(6):

            origin = [vec_arr_origin[0, i], vec_arr_origin[1, i], vec_arr_origin[2, i]]
            destination = [vec_arr_dest[0, i], vec_arr_dest[1, i], vec_arr_dest[2, i]]

            ax.text(vec_arr_origin[0, i],vec_arr_origin[1, i],vec_arr_origin[2, i],  '%s' % (str(i+1)), size=18, zorder=1,  color='#586e75')

            if s.lll[i] > s.actuatorStrokedLength:
                ax.plot([vec_arr_origin[0, i] , vec_arr_dest[0, i]], [vec_arr_origin[1, i], vec_arr_dest[1, i]], [vec_arr_origin[2, i],vec_arr_dest[2, i]], color="#dc322f", linewidth=5)
            elif s.lll[i] >= (s.actuatorStrokedLength - strokeMargin):
                ax.plot([vec_arr_origin[0, i] , vec_arr_dest[0, i]], [vec_arr_origin[1, i], vec_arr_dest[1, i]], [vec_arr_origin[2, i],vec_arr_dest[2, i]], color="#cb4b16", linewidth=2)


            elif s.lll[i] < s.actuatorClosedLength:
                ax.plot([vec_arr_origin[0, i] , vec_arr_dest[0, i]], [vec_arr_origin[1, i], vec_arr_dest[1, i]], [vec_arr_origin[2, i],vec_arr_dest[2, i]], color="#dc322f", linewidth=5)
            elif s.lll[i] <= s.actuatorClosedLength + strokeMargin:
                ax.plot([vec_arr_origin[0, i] , vec_arr_dest[0, i]], [vec_arr_origin[1, i], vec_arr_dest[1, i]], [vec_arr_origin[2, i],vec_arr_dest[2, i]], color="#cb4b16", linewidth=2)
            else:
                ax.plot([vec_arr_origin[0, i] , vec_arr_dest[0, i]], [vec_arr_origin[1, i], vec_arr_dest[1, i]], [vec_arr_origin[2, i],vec_arr_dest[2, i]], color=color_, linewidth=2)

    def plot_platform(s):
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

        ax.axes.xaxis.set_ticklabels([])
        ax.axes.yaxis.set_ticklabels([])
        ax.axes.zaxis.set_ticklabels([])

        ax.add_collection3d(Poly3DCollection([list(np.transpose(s.B))], facecolors='#859900', alpha=0.6, edgecolors='#073642'))
        ax.add_collection3d(Poly3DCollection([list(np.transpose(s.L))], facecolors='#268bd2', alpha=0.6, edgecolors='#073642'))

        # s.plot3D_line(ax, s.B, s.H, '#2aa198') #Servo Horn Length
        # s.plot3D_line(ax, s.H, s.L, '#002b36') #Effective Length
        s.plot3D_line(ax, s.B, s.L, '#073642') #Rod Length
        return ax

    #Roll yaw pitch notation
    def rotX(s, phi):
        rotx = np.array([
            [1,     0    ,    0    ],
            [0,  np.cos(phi), np.sin(phi)],
            [0, -np.sin(phi), np.cos(phi)] ])
        return rotx

    def rotY(s, theta):    
        roty = np.array([
            [np.cos(theta), 0, -np.sin(theta) ],
            [0         , 1,     0       ],
            [np.sin(theta), 0,  np.cos(theta) ] ])   
        return roty
        
    def rotZ(s, psi):    
        rotz = np.array([
            [ np.cos(psi), np.sin(psi), 0 ],
            [-np.sin(psi), np.cos(psi), 0 ],
            [   0        ,     0      , 1 ] ])   
        return rotz