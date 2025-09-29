import tkinter as tk
from tkinter import scrolledtext
from tkinter import *
from PIL import Image, ImageTk
import threading
import serial
import cv2
import numpy as np
from printy import printy
from collections import deque
import time
from datetime import datetime
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import axes3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')


import image_utils
import stewartCalculations
import plottingTools

tennis_ball = [64, 186, 156]

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


feedbackQueLength = 6



def parse_telemetry_data(dataLine):
    packetCounter = None
    lastCommandedLengths = [None, None, None, None, None, None]
    feedbackLengths = [None, None, None, None, None, None]
    statusCode = None

    splitLine = dataLine.decode().strip().split(",")
    packetCounter = splitLine[0]
    lastCommandedLengths = [float(splitLine[1]), float(splitLine[2]), float(splitLine[3]), float(splitLine[4]), float(splitLine[5]), float(splitLine[6])]
    feedbackLengths = [float(splitLine[7]), float(splitLine[8]), float(splitLine[9]), float(splitLine[10]), float(splitLine[11]), float(splitLine[12])]
    statusCode = int(splitLine[13])
    outOfRangeFlag = int(splitLine[14])

    return np.array(lastCommandedLengths), np.array(feedbackLengths), statusCode, outOfRangeFlag



class feedbackQues_Class():
    def __init__(self):
        self.leg_1 = deque(maxlen=feedbackQueLength)
        self.leg_2 = deque(maxlen=feedbackQueLength)
        self.leg_3 = deque(maxlen=feedbackQueLength)
        self.leg_4 = deque(maxlen=feedbackQueLength)
        self.leg_5 = deque(maxlen=feedbackQueLength)
        self.leg_6 = deque(maxlen=feedbackQueLength)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Heliospace Stewart Platform V1.1")

        self.assemblyGeometry = stewartCalculations.SP_assemblyGeometry()
        self.assemblyGeometry.r_B = 220           # Base radius
        self.assemblyGeometry.r_P = 220           # Platform Radius
        self.assemblyGeometry.actuatorClosedLength = 152
        self.assemblyGeometry.actuatorFullLength = 252
        self.assemblyGeometry.baseAnchorAngleDegrees = 50 # angle from center out to leg pair in degrees
        self.assemblyGeometry.platformAnchorAngleDegrees = 32 # angle from center out to leg pair in degrees
        self.assemblyGeometry.refRotationDegrees = 0    # Assembly oriention around z axis

        self.assemblyGeometry.actuatorHomeLength = self.assemblyGeometry.actuatorClosedLength + (self.assemblyGeometry.actuatorFullLength-self.assemblyGeometry.actuatorClosedLength)/2
        self.assemblyGeometry.psi_B = stewartCalculations.calcPsiB(self.assemblyGeometry.baseAnchorAngleDegrees, self.assemblyGeometry.refRotationDegrees) #Radians
        self.assemblyGeometry.psi_P = stewartCalculations.calcPsiP(self.assemblyGeometry.platformAnchorAngleDegrees, self.assemblyGeometry.refRotationDegrees) #Radians

        self.assemblyGeometry.stroke = self.assemblyGeometry.actuatorFullLength-self.assemblyGeometry.actuatorClosedLength

        self.targetPointingActive = False
        self.center_box_size = 2

        # Setup GUI frames
        self.setup_frames()

        printy("Initializing Serial connection to microcontroller...", "cB")
        self.init_serial()


        printy("Initializing Target Detection Video Stream...", 'cB')
        self.init_video()

        self.platformOrientation = stewartCalculations.orientation() #Initialize orientation class for platform
        self.baseOrientation = stewartCalculations.orientation() #Initialize orientation class for base

        self.feedbackTracking = feedbackQues_Class()
        self.platform_in_motion = False

        self.lastCommandSentTime = None

        self.initializePlatformToHome()

        self.start_threads()


    def setup_frames(self):
        # Left Frame
        self.video_frame = tk.Frame(root, width=200, height=400, bg="white")
        self.video_frame.pack(side='left', fill='y')
        self.video_label = tk.Label(self.video_frame, text="Video Frame")
        self.video_label.pack(pady=20, padx=20)

        # Middle Frame
        self.middle_frame = tk.Frame(root, width=200, height=400, bg='white')  # Added a background color for visualization
        self.middle_frame.pack(side='left', fill='y', padx=10)  # Adjusted to pack it to the left, with padding for spacing
        # self.middle_label = tk.Label(self.middle_frame, text="Middle Frame")
        # self.middle_label.pack(pady=20)

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111, projection='3d')

        self.ax.set_xlabel('')
        self.ax.set_ylabel('')
        self.ax.set_zlabel('')

        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False

        # Now set color to white (or whatever is "invisible")
        self.ax.xaxis.pane.set_edgecolor('w')
        self.ax.yaxis.pane.set_edgecolor('w')
        self.ax.zaxis.pane.set_edgecolor('w')


        self.canvas = FigureCanvasTkAgg(self.fig, master=self.middle_frame)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)


        # Right Frame (contains two vertical sub-frames)
        self.right_frame = tk.Frame(root, width=200, height=400, bg='white')
        self.right_frame.pack(side='right', fill='both', expand=True)

        # Right Top Frame
        self.status_frame = tk.Frame(self.right_frame, width=200, height=200, bg='white')
        self.status_frame.pack(side='top', fill='both', expand=True, pady=20, padx=20)
        # self.status_label = tk.Label(self.status_frame, text="Status", bg='white')
        # self.status_label.pack()
        # self.status_label.grid(row=0, column=0, columnspan=2, pady=20)


        self.lc_leg1_label = tk.Label(self.status_frame, text="Last Commanded Leg#1:", bg='white')
        self.lc_leg1_label.grid(row=1, column=0, sticky=tk.W)
        self.lc_leg1_value = tk.Label(self.status_frame, text="Not Available", fg="red", bg='white')
        self.lc_leg1_value.grid(row=1, column=1, sticky=tk.W)

        self.lc_leg2_label = tk.Label(self.status_frame, text="Last Commanded Leg#2:", bg='white')
        self.lc_leg2_label.grid(row=2, column=0, sticky=tk.W)
        self.lc_leg2_value = tk.Label(self.status_frame, text="Not Available", fg="red", bg='white')
        self.lc_leg2_value.grid(row=2, column=1, sticky=tk.W)

        self.lc_leg3_label = tk.Label(self.status_frame, text="Last Commanded Leg#3:", bg='white')
        self.lc_leg3_label.grid(row=3, column=0, sticky=tk.W)
        self.lc_leg3_value = tk.Label(self.status_frame, text="Not Available", fg="red", bg='white')
        self.lc_leg3_value.grid(row=3, column=1, sticky=tk.W)

        self.lc_leg4_label = tk.Label(self.status_frame, text="Last Commanded Leg#4:", bg='white')
        self.lc_leg4_label.grid(row=4, column=0, sticky=tk.W)
        self.lc_leg4_value = tk.Label(self.status_frame, text="Not Available", fg="red", bg='white')
        self.lc_leg4_value.grid(row=4, column=1, sticky=tk.W)

        self.lc_leg5_label = tk.Label(self.status_frame, text="Last Commanded Leg#5:", bg='white')
        self.lc_leg5_label.grid(row=5, column=0, sticky=tk.W)
        self.lc_leg5_value = tk.Label(self.status_frame, text="Not Available", fg="red", bg='white')
        self.lc_leg5_value.grid(row=5, column=1, sticky=tk.W)

        self.lc_leg6_label = tk.Label(self.status_frame, text="Last Commanded Leg#6:", bg='white')
        self.lc_leg6_label.grid(row=6, column=0, sticky=tk.W)
        self.lc_leg6_value = tk.Label(self.status_frame, text="Not Available", fg="red", bg='white')
        self.lc_leg6_value.grid(row=6, column=1, sticky=tk.W)

        self.x_offset_label = tk.Label(self.status_frame, text="Target X offset:", bg='white')
        self.x_offset_label.grid(row=7, column=0, sticky=tk.W)
        self.x_offset_value = tk.Label(self.status_frame, text="Not Available", fg="red", bg='white')
        self.x_offset_value.grid(row=7, column=1, sticky=tk.W)

        self.y_offset_label = tk.Label(self.status_frame, text="Target Y offset:", bg='white')
        self.y_offset_label.grid(row=8, column=0, sticky=tk.W)
        self.y_offset_value = tk.Label(self.status_frame, text="Not Available", fg="red", bg='white')
        self.y_offset_value.grid(row=8, column=1, sticky=tk.W)


        self.fb_leg1_label = tk.Label(self.status_frame, text="Feedback Leg#1:", bg='white')
        self.fb_leg1_label.grid(row=1, column=2, sticky=tk.W)
        self.fb_leg1_value = tk.Label(self.status_frame, text="Not Available", fg="red", bg='white')
        self.fb_leg1_value.grid(row=1, column=3, sticky=tk.W)

        self.fb_leg2_label = tk.Label(self.status_frame, text="Feedback Leg#2:", bg='white')
        self.fb_leg2_label.grid(row=2, column=2, sticky=tk.W)
        self.fb_leg2_value = tk.Label(self.status_frame, text="Not Available", fg="red", bg='white')
        self.fb_leg2_value.grid(row=2, column=3, sticky=tk.W)

        self.fb_leg3_label = tk.Label(self.status_frame, text="Feedback Leg#3:", bg='white')
        self.fb_leg3_label.grid(row=3, column=2, sticky=tk.W)
        self.fb_leg3_value = tk.Label(self.status_frame, text="Not Available", fg="red", bg='white')
        self.fb_leg3_value.grid(row=3, column=3, sticky=tk.W)

        self.fb_leg4_label = tk.Label(self.status_frame, text="Feedback Leg#4:", bg='white')
        self.fb_leg4_label.grid(row=4, column=2, sticky=tk.W)
        self.fb_leg4_value = tk.Label(self.status_frame, text="Not Available", fg="red", bg='white')
        self.fb_leg4_value.grid(row=4, column=3, sticky=tk.W)

        self.fb_leg5_label = tk.Label(self.status_frame, text="Feedback Leg#5:", bg='white')
        self.fb_leg5_label.grid(row=5, column=2, sticky=tk.W)
        self.fb_leg5_value = tk.Label(self.status_frame, text="Not Available", fg="red", bg='white')
        self.fb_leg5_value.grid(row=5, column=3, sticky=tk.W)

        self.fb_leg6_label = tk.Label(self.status_frame, text="Feedback Leg#6:", bg='white')
        self.fb_leg6_label.grid(row=6, column=2, sticky=tk.W)
        self.fb_leg6_value = tk.Label(self.status_frame, text="Not Available", fg="red", bg='white')
        self.fb_leg6_value.grid(row=6, column=3, sticky=tk.W)

        self.status_code_label = tk.Label(self.status_frame, text="Status:", bg='white')
        self.status_code_label.grid(row=1, column=4, sticky=tk.W)
        self.status_code_value = tk.Label(self.status_frame, text="Not Available", fg="red", bg='white')
        self.status_code_value.grid(row=1, column=5, sticky=tk.W)

        self.out_of_range_label = tk.Label(self.status_frame, text="Out of Range:", bg='white')
        self.out_of_range_label.grid(row=2, column=4, sticky=tk.W)
        self.out_of_range_value = tk.Label(self.status_frame, text="Not Available", fg="red", bg='white')
        self.out_of_range_value.grid(row=2, column=5, sticky=tk.W)

        self.in_motion_label = tk.Label(self.status_frame, text="Platform In Motion:", bg='white')
        self.in_motion_label.grid(row=3, column=4, sticky=tk.W)
        self.in_motion_value = tk.Label(self.status_frame, text="Not Available", fg="red", bg='white')
        self.in_motion_value.grid(row=3, column=5, sticky=tk.W)


        self.activateTracking_button = tk.Button(self.status_frame, text="Tracking", command=self.on_activate_click, bg="red")
        self.activateTracking_button.grid(row=10, column=0, sticky=tk.W)

        self.center_box_size_entry = tk.Entry(self.status_frame)
        self.center_box_size_entry.grid(row=11, column=0, sticky=tk.W)
        self.apply_button = tk.Button(self.status_frame, text="Update Center Box Size", command=self.update_center_box_size)
        self.apply_button.grid(row=11, column=1, sticky=tk.W)


        self.send_home_button = tk.Button(self.status_frame, text="Home", command=self.on_send_home_click)
        self.send_home_button.grid(row=12, column=1, sticky=tk.W)




        # Right Bottom Frame
        self.telemetry_frame = tk.Frame(self.right_frame, width=200, height=200, bg='white')
        # self.telemetry_frame.pack(side='bottom', fill='both', expand=True)
        # self.telemetry_label = tk.Label(self.telemetry_frame, text="Raw Telemetry", bg='white')
        # self.telemetry_label.pack()
        self.telemetry_text = scrolledtext.ScrolledText(self.telemetry_frame, wrap=tk.WORD, height=10, width=100)
        # self.telemetry_text.pack(padx=10, pady=10)


    def update_center_box_size(self):
        try:
            float_value = float(self.center_box_size_entry.get())
            self.center_box_size = float_value
        except ValueError:
            # If the conversion fails, inform the user
            messagebox.showerror("Error", "Please enter a valid floating point number.")


    def on_activate_click(self):
        if self.targetPointingActive == False:
            self.targetPointingActive = True
            printy("Target tracking turned on", "cB")
            self.activateTracking_button.config(text="Tracking", bg="green")
        else:
            self.targetPointingActive = False
            printy("Target tracking turned off", "cB")
            self.activateTracking_button.config(text="Tracking", bg="red")

    def on_send_home_click(self):
        apply_thread = threading.Thread(target=self.send_home_button_thread)
        apply_thread.start()

    def send_home_button_thread(self):
        self.platformOrientation.rollDegrees = 0.0
        self.platformOrientation.pitchDegrees = 0.0
        self.targetPointingActive = False
        self.activateTracking_button.config(text="Tracking", bg="red")
        self.initializePlatformToHome()

    def init_video(self):
        try:
            self.cap = cv2.VideoCapture(1)
            self.target_aquired = False
            self.x_center_offset = None
            self.y_center_offset = None
        except serial.SerialException as e:
            print(f"Error opening video stream: {e}")
            self.cap = None


    def init_serial(self):
        try:
            self.ser = serial.Serial('COM5', 115200, timeout=1)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            self.ser = None

    def determine_if_moving(self):
        now = datetime.now()

        if (now - self.lastCommandSentTime).total_seconds() < 1.5:
            self.platform_in_motion = True
        else:
            if self.platform_in_motion == True:
                que_change_threshold = 3
            elif self.platform_in_motion == False:
                que_change_threshold = 8
            self.feedbackTracking.leg_1.append(self.feedbackLengths[0])
            self.feedbackTracking.leg_2.append(self.feedbackLengths[1])
            self.feedbackTracking.leg_3.append(self.feedbackLengths[2])
            self.feedbackTracking.leg_4.append(self.feedbackLengths[3])
            self.feedbackTracking.leg_5.append(self.feedbackLengths[4])
            self.feedbackTracking.leg_6.append(self.feedbackLengths[5])
            que_ranges = [max(self.feedbackTracking.leg_1) - min(self.feedbackTracking.leg_1), max(self.feedbackTracking.leg_2) - min(self.feedbackTracking.leg_2), max(self.feedbackTracking.leg_3) - min(self.feedbackTracking.leg_3), max(self.feedbackTracking.leg_4) - min(self.feedbackTracking.leg_4), max(self.feedbackTracking.leg_5) - min(self.feedbackTracking.leg_5), max(self.feedbackTracking.leg_6) - min(self.feedbackTracking.leg_6)]
            max_que_range = max(que_ranges)

            if len(self.feedbackTracking.leg_1) < feedbackQueLength:
                self.platform_in_motion = True
            elif max_que_range >= que_change_threshold:
                self.platform_in_motion = True
            else:
                self.platform_in_motion = False



    def PerformCalcs(self):

        B = stewartCalculations.calculateB(self.assemblyGeometry.psi_B, self.assemblyGeometry.r_B) # Calculates Base corner coords prior to applying tranforms for yaw, pitch, roll, etc.
        P = stewartCalculations.calculateP(self.assemblyGeometry.psi_P, self.assemblyGeometry.r_P) # Calculates Platform corner coords prior to applying tranforms for yaw, pitch, roll, etc.

        # Definition of the platform home position.
        z = np.sqrt(self.assemblyGeometry.actuatorHomeLength**2 - (P[0] - B[0])**2 - (P[1] - B[1])**2)
        # This is the transform to move P created above to its home position.
        platform_home_transformation = np.array([0, 0, z[0]])
        self.L, self.legLengths, self.B = stewartCalculations.calculateLegsAndBase(B, P, platform_home_transformation, self.baseOrientation, self.platformOrientation)
        self.PV = stewartCalculations.calcPlatformPointingVector(self.platformOrientation, platform_home_transformation)

    def updatePlot(self):
        

        self.ax.clear()

        self.ax.set_xlim3d(-self.assemblyGeometry.r_B, self.assemblyGeometry.r_B)
        self.ax.set_ylim3d(-self.assemblyGeometry.r_B, self.assemblyGeometry.r_B)
        self.ax.set_zlim3d(0, 2*self.assemblyGeometry.r_B)

        self.ax.axes.xaxis.set_ticklabels([])
        self.ax.axes.yaxis.set_ticklabels([])
        self.ax.axes.zaxis.set_ticklabels([])


        self.ax.add_collection3d(Poly3DCollection([list(np.transpose(self.B))], facecolors=baseFaceColor, alpha=baseAlpha, edgecolors=baseEdgeColor))
        self.ax.add_collection3d(Poly3DCollection([list(np.transpose(self.L))], facecolors=platFormFaceColor, alpha=platformAlpha, edgecolors=platformEdgeColor))

        legCollection = []
        legLabels = []
        for i in range(6):
            origin = np.matrix([self.B[0, i], self.B[1, i], self.B[2, i]])
            destination = np.matrix([self.L[0, i], self.L[1, i], self.L[2, i]])
            middle = (destination[0]+origin[0])
            leg = self.ax.plot([self.B[0, i] , self.L[0, i]], [self.B[1, i], self.L[1, i]], [self.B[2, i], self.L[2, i]], color=legDefaultColor, linewidth=1)
            legCollection.append(leg[0])

        self.canvas.draw()


    def updateStatus_via_main_thread(self):
        # Use after to schedule the updates on the main thread
        self.root.after(0, self.updateStatus)

    def updateStatus(self):
        # This is the actual update logic
        self.lc_leg1_value.config(text=str(self.lastCommandedLengths[0]), fg="black")
        self.lc_leg2_value.config(text=str(self.lastCommandedLengths[1]), fg="black")
        self.lc_leg3_value.config(text=str(self.lastCommandedLengths[2]), fg="black")
        self.lc_leg4_value.config(text=str(self.lastCommandedLengths[3]), fg="black")
        self.lc_leg5_value.config(text=str(self.lastCommandedLengths[4]), fg="black")
        self.lc_leg6_value.config(text=str(self.lastCommandedLengths[5]), fg="black")

        self.fb_leg1_value.config(text=str(self.feedbackLengths[0]), fg="black")
        self.fb_leg2_value.config(text=str(self.feedbackLengths[1]), fg="black")
        self.fb_leg3_value.config(text=str(self.feedbackLengths[2]), fg="black")
        self.fb_leg4_value.config(text=str(self.feedbackLengths[3]), fg="black")
        self.fb_leg5_value.config(text=str(self.feedbackLengths[4]), fg="black")
        self.fb_leg6_value.config(text=str(self.feedbackLengths[5]), fg="black")

        if self.platform_in_motion == True:
            self.in_motion_value.config(text="True", fg="black")
        else:
            self.in_motion_value.config(text="False", fg="black")

        if self.outOfRangeFlag == 1:
            self.out_of_range_value.config(text="True", fg="red")
        if self.outOfRangeFlag == 0:
            self.out_of_range_value.config(text="False", fg="black")

        self.x_offset_value.config(text=str(self.x_center_offset)+" px", fg="black")
        self.y_offset_value.config(text=str(self.y_center_offset)+" px", fg="black")

        self.status_code_value.config(text=str(self.statusCode), fg="black")



    def serial_event(self, frame_text_widget):
        if self.ser is not None:
            while True:
                if self.ser.in_waiting > 0:
                    telemetry_data = self.ser.readline()

                    self.lastCommandedLengths, self.feedbackLengths, self.statusCode, self.outOfRangeFlag = parse_telemetry_data(telemetry_data)

                    self.determine_if_moving()

                    # self.update_telemetry_via_main_thread(frame_text_widget, telemetry_data.decode('utf-8').rstrip())

                    self.updateStatus_via_main_thread()

        else:
            print("Serial port not open.")

    def print_command_info_to_console(self, commandString):
        printy(commandString)

    def main_event(self):
        while True:

            if (self.platform_in_motion == False) and (self.x_center_offset is not None) and (self.targetPointingActive == True):
                movementRequired = False
                preCommandPitch = self.platformOrientation.pitchDegrees
                preCommandRoll = self.platformOrientation.rollDegrees
                if self.x_center_offset > (self.center_box_size/2):
                    self.platformOrientation.rollDegrees -= abs(self.x_center_offset)/30
                    movementRequired = True
                elif self.x_center_offset < (-self.center_box_size/2):
                    self.platformOrientation.rollDegrees += abs(self.x_center_offset)/30
                    movementRequired = True
                if self.y_center_offset > (self.center_box_size/2):
                    self.platformOrientation.pitchDegrees += abs(self.y_center_offset)/20
                    movementRequired = True
                elif self.y_center_offset < (-self.center_box_size/2):
                    self.platformOrientation.pitchDegrees -= abs(self.y_center_offset)/20
                    movementRequired = True

                if movementRequired == True:
                    self.PerformCalcs()
                    self.updatePlot()
                    commandString = ",".join(map(lambda x: format(x, '.2f'), self.legLengths))

                    self.print_command_info_to_console(commandString)

                    self.ser.write(commandString.encode('utf-8'))
                    self.lastCommandSentTime = datetime.now()


                    self.platform_in_motion = True

            time.sleep(.05)
                    
    def video_event(self):
        if self.cap is not None:

            while True:
                ret, frame = self.cap.read()
                if ret:
                    convertedToRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert the frame color to RGB

                    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
                    hsvImage = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

                    lowerLimit, upperLimit = image_utils.get_limits(color=tennis_ball)
                    mask = cv2.inRange(hsvImage, lowerLimit, upperLimit)

                    mask = cv2.erode(mask, None, iterations=2)
                    mask = cv2.dilate(mask, None, iterations=2)
                    mask_ = Image.fromarray(mask)
                    bbox = mask_.getbbox()

                    height, width = frame.shape[:2]

                    center_x = width/2
                    center_y = height/2

                    frame = cv2.rectangle(frame, (int(center_x+(self.center_box_size/2)), int(center_y+(self.center_box_size/2))), (int(center_x-(self.center_box_size/2)), int(center_y-(self.center_box_size/2))), (0, 255, 0), 1)
                    frame = cv2.line(frame, (int(center_x), int(center_y - self.center_box_size)), (int(center_x), int(center_y + self.center_box_size)), (0, 255, 0), 1)
                    frame = cv2.line(frame, (int(center_x - self.center_box_size), int(center_y)), (int(center_x + self.center_box_size), int(center_y)), (0, 255, 0), 1)

                    if bbox is not None:
                        self.target_aquired = True
                        x1, y1, x2, y2 = bbox
                        target_center_x = int(x1 + (x2-x1)/2)
                        target_center_y = int(y1 + (y2-y1)/2)
                        if ((target_center_x <= (center_x+(self.center_box_size/2))) and (target_center_x >= -(center_x+(self.center_box_size/2)))) and (target_center_y <= (center_y+(self.center_box_size/2))) and (target_center_y >= -(center_y+(self.center_box_size/2))):
                            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        else:
                            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        target_x = x1 + ((x2-x1)/2)
                        target_y = y1 + ((y2-y1)/2)
                        self.x_center_offset = target_x - center_x
                        self.y_center_offset = center_y - target_y
                    else:
                        self.target_aquired = False
                        self.x_center_offset = None
                        self.y_center_offset = None

                    convertedToRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(convertedToRGB)
                    self.imgTk = ImageTk.PhotoImage(image=img)  # Keep a reference to the PhotoImage object
                    # Schedule the update on the main thread
                    self.root.after(0, self.update_video_label)

    def update_video_label(self):
        self.video_label.configure(image=self.imgTk)
        self.video_label.image = self.imgTk  # Keep a reference




    # def update_telemetry_via_main_thread(self, text_widget, text):
    #     # Ensure the text update is done in the main thread
    #     self.root.after(0, self.append_telmetry_line, text_widget, text)

    # def append_telmetry_line(self, text_widget, text):
    #     text_widget.configure(state='normal')  # Enable editing of the widget
    #     text_widget.insert(tk.END, text + "\n")  # Append text
    #     lines = text_widget.get('1.0', tk.END).splitlines()
    #     if len(lines) > 50:  # Keep only the last 50 lines
    #         text_widget.delete('1.0', '2.0')
    #     text_widget.configure(state='disabled')  # Disable editing of the widget
    #     text_widget.yview(tk.END)  # Autoscroll to the bottom




    def start_threads(self):
        if self.ser is not None:
            threading.Thread(target=self.serial_event, args=(self.telemetry_text,), daemon=True).start()
        else:
            print("Cannot start serial thread, serial port not initialized.")

        if self.cap is not None:
            threading.Thread(target=self.video_event, daemon=True).start()
        else:
            print("Cannot start serial thread, serial port not initialized.")


        if (self.cap is not None) and (self.ser is not None):
            threading.Thread(target=self.main_event, daemon=True).start()

    def close_serial(self):
        if self.ser is not None:
            self.ser.close()


    def initializePlatformToHome(self):
        printy("Initializing platform to home position...", "cB")
        
        self.PerformCalcs()

        commandString = ",".join(map(lambda x: format(x, '.2f'), self.legLengths))

        self.print_command_info_to_console(commandString)


        previous_telemetry_lengths = np.array([None, None, None, None, None, None])
        self.ser.write(commandString.encode('utf-8'))
        self.lastCommandSentTime = datetime.now()
        self.platform_in_motion = True
        time.sleep(3)
        while self.platform_in_motion == True:
            telemetry_data = self.ser.readline()
            self.lastCommandedLengths, self.feedbackLengths, self.statusCode, self.outOfRangeFlag = parse_telemetry_data(telemetry_data)
            self.determine_if_moving()
        self.updatePlot()


if __name__ == "__main__":
    root = tk.Tk()
    root.configure(background='white')
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", lambda: [app.close_serial(), root.destroy()])
    root.mainloop()
