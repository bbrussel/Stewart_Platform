import java.awt.Frame;
import java.awt.BorderLayout;
import javax.swing.JOptionPane;
import controlP5.*;
import processing.serial.*;

import java.util.Date;
import java.text.SimpleDateFormat;

// === DATALOGGER === // 
PrintWriter datalog;

// ===== SCREEN DIMENSIONS ===== //
final int screenWidth = 1950;
final int screenHeight = 930;

// ===== GRAPH DIMENSIONS ===== //
final int yprGraphX = 75;
final int yprGraphY = 250;
final int yprGraphYStep = 195;

final int transGraphX = yprGraphX + 275;
final int transGraphY = yprGraphY;
final int transGraphYStep = 195;

final int graphBorderXStep = 55;
final int graphBorderYStep = 20;

final int graphBorderXSize =  280;
final int graphBorderYSize = 600;

final int connY = 830;

// ===== CONTROL DIMENSIONS ===== //
final int ctrlX = 1220;
final int ctrlY = 210;

final int ctrlSlidersX = 1580;
final int ctrlSlidersY = yprGraphY - graphBorderYStep * 3;

// ===== COLOR PALLETE ===== //
final color foregroundColor = color(255, 255, 255);
final color gaugeColor = color(0, 200, 20);
final color backgroundColor = color(10, 20, 30);
final color controlBackgroundColor = color(20, 30, 40);
final color darkControlBackgroundColor = color(5, 15, 20);

CColor redButtonColor = new CColor();
CColor greenButtonColor = new CColor();

// ===== IMAGE OBJECTS ===== // 
PImage logo;
PImage sub;

// ===== FONTS ===== //
PFont titleFont;
PFont largeSectionFont;
PFont sectionFont;
PFont itemFont;

ControlFont smallControlFont;
ControlFont largeControlFont;

// ===== TELEMETRY VALUES ===== // 
float yaw;
float pitch;
float roll;
float xtrans;
float ytrans;
float ztrans;
float[] legLengths;
float[] legFeedback;

// ===== CONTROL P5 OBJECTS ===== //
ControlP5 cp5;

// ===== GRAPH OBJECTS ===== //
float[] timeValues;

float[] yawValues;
Graph yawGraph;

float[] pitchValues;
Graph pitchGraph;

float[] rollValues;
Graph rollGraph;

float[] xtransValues;
Graph xtransGraph;

float[] ytransValues;
Graph ytransGraph;

float[] ztransValues;
Graph ztransGraph;

float[][] legFeedbackValues;
Graph legFeedbackGraph;

float[][] legLengthValues;
color[] legLengthGraphColors = new color[6];
Graph legLengthGraph;

double elapsedTime;

long lastGraphUpdate = 0;
int graphUpdateDelay = 1000 / 20; // 20Hz graph update

// ===== CONTROL OBJECTS ===== //
Slider2D xytransCommand;
Textarea conArea;
Slider yawSlider;
Slider pitchSlider;
Slider rollSlider;
Slider xtransSlider;
Slider ytransSlider;
Slider ztransSlider;

// ===== STATE OBJECTS ===== //
boolean armed = false;

// ===== SERIAL OBJECTS ===== //
String COMt = "N/A";
String COMx = "N/A";
Serial port;
boolean connected = false;

// ===== SERIAL FUNCTIONS ===== //
boolean notConnected()
{
  if(!connected) JOptionPane.showMessageDialog(null, "Not connected to a COM port");
  return !connected;
}

void serialSelect()
{
  COMx = "COM3"; // Change this to be whatever port you have the teensy attached to
}

void connect()
{
  if(connected) return;

  if(COMx != "N/A")
  {
    try
    {
      port = new Serial(this, COMx, 115200); // Change to baud rate used (115200 standard in Stewart Platform codebase)
      port.clear();
      port.bufferUntil('\n'); // buffer until newline appears

      lastGraphUpdate = millis();

      String timestamp = new SimpleDateFormat("yyyy-MM-dd_HH-mm-ss").format(new Date());
      datalog = createWriter("SP_DASHBOARD_DATA/" + timestamp + ".csv");
      datalog.print("yaw,pitch,roll,xtrans,ytrans,ztrans,leglength1,leglength2,leglength3,leglength4,leglength5,leglength6,legfeedback1,legfeedback2,legfeedback3,legfeedback4,legfeedback5,legfeedback6,elapsedTime\n"); // write header for datalog csv file (database format in firmware)
      connected = true;
    }
    catch (Exception e)
    {
      JOptionPane.showMessageDialog(null, "COM port " + COMx + " is not available (maybe in use by another program)");
      COMx = "N/A";
    }
  }
  else
  {
    JOptionPane.showMessageDialog(null, "No COM port selected");
  }
}

void disconnect()
{
  if(notConnected()) return;
  
  port.stop();
  connected = false;

  try
  {
    datalog.flush();
    datalog.close();
  }
  catch (Exception e)
  {
    return;
  }

  println("Disconnected");
}

// ===== MAIN SETUP FUNCTION ===== //
void setup()
{
  // Load images and fonts
  logo = loadImage("./img/HS_logo.png");
  sub = loadImage("./img/platform_real.png");
  
  titleFont = loadFont("./fonts/CascadiaCode60.vlw");
  largeSectionFont = loadFont("./fonts/CascadiaCode40.vlw");
  sectionFont = loadFont("./fonts/CascadiaCode20.vlw");
  itemFont = loadFont("./fonts/CascadiaCode12.vlw");

  //smallControlFont = new ControlFont();
  largeControlFont = new ControlFont(itemFont);
  
  // Place surfaces, buttons
  surface.setTitle("Heliospace Hexapod Testing GUI");
  surface.setResizable(false);
  surface.setLocation(750, 250);

  redButtonColor.setActive(color(255, 0, 0));
  redButtonColor.setForeground(color(224, 0, 0));
  redButtonColor.setBackground(color(164, 0, 0));

  greenButtonColor.setActive(color(0, 255, 0));
  greenButtonColor.setForeground(color(0, 224, 0));
  greenButtonColor.setBackground(color(0, 164, 0));

  // Assign graph line colors
  legLengthGraphColors[0] = color(131, 255, 20);
  legLengthGraphColors[1] = color(232, 158, 12);
  legLengthGraphColors[2] = color(255, 0, 0);
  legLengthGraphColors[3] = color(62, 12, 232);
  legLengthGraphColors[4] = color(13, 255, 243);
  legLengthGraphColors[5] = color(200, 46, 232);

  // Setup graph time values
  timeValues = new float[(5 * 20) + 1];
  yawValues = new float[timeValues.length];
  pitchValues = new float[timeValues.length];
  rollValues = new float[timeValues.length];
  xtransValues = new float[timeValues.length];
  ytransValues = new float[timeValues.length];
  ztransValues = new float[timeValues.length];
  
  legLengths = new float[6];
  legLengthValues = new float[6][timeValues.length];

  legFeedback = new float[6];
  legFeedbackValues = new float[6][timeValues.length];

  // Assign graph time values (5 seconds of time values)
  for(int t = 0; t <= 5 * 20; t++)
  {
    timeValues[t] = (float)t / 20;

    yawValues[t] = 0;
    pitchValues[t] = 0;
    rollValues[t] = 0;
    xtransValues[t] = 0;
    ytransValues[t] = 0;
    ztransValues[t] = 0;
    for (int i = 0; i < 6; i++)
    {
      legLengthValues[i][t] = 0;
      legFeedbackValues[i][t] = 0;
    }
  }

  gui();
}

void settings()
{
  smooth(2);
  size(screenWidth, screenHeight);
}

// ===== MAIN GUI FUNCTION ===== //
void gui()
{
  cp5 = new ControlP5(this);

  // ===== SERIAL CONTROL BUTTONS ===== //
  cp5.addButton("serialSelect") // add button to select, connect and disconnect from serial port
     .setPosition(10, connY)
     .setSize(180, 90)
     .setLabel("Choose Serial Port")
     .getCaptionLabel().setFont(largeControlFont);

  cp5.addButton("connect")
      .setPosition(210, connY)
      .setSize(180, 90)
      .setLabel("Connect")
      .setColor(greenButtonColor)
      .getCaptionLabel().setFont(largeControlFont);

  cp5.addButton("disconnect")
      .setPosition(410, connY)
      .setSize(180, 90)
      .setLabel("Disconnect")
      .setColor(redButtonColor)
      .getCaptionLabel().setFont(largeControlFont);
      
  conArea = cp5.addTextarea("conArea") // debug console, write to this using print() or println()
               .setPosition(ctrlX, ctrlY + 290)
               .setSize(280, 340)
               .setLineHeight(12)
               .setColorBackground(darkControlBackgroundColor)
               .setColorForeground(foregroundColor)
               .scroll(1)
               .hideScrollbar();
  cp5.addConsole(conArea);

  cp5.setAutoDraw(false);

  // ===== SENDER (LISTENERS) ===== //
  CallbackListener posCmdSender = new CallbackListener() 
  {
    public void controlEvent(CallbackEvent theEvent) 
    {
      posSend(); // sender called with 6 1d sliders for each DOF
    }
  };

  CallbackListener setpointSender = new CallbackListener() 
  {
    public void controlEvent(CallbackEvent theEvent) 
    {
      posSlideSender(); // sender called with 2d slider for x/y translation
    }
  };

  // ===== SLIDER 1/2D DEFINITIONS ===== //
  xytransCommand = cp5.addSlider2D("xyTransCommand")
                         .setBroadcast(false)
                         .setPosition(ctrlX + 30, ctrlY + 20)
                         .setSize(200, 200)
                         .setMinMax(-75, 75, 75, -75)
                         .setValue(0, 0)
                         .setLabel("X/Y");
  xytransCommand.onRelease(posCmdSender);

  // YPR / XYZ Trans Sliders
  yawSlider = cp5.addSlider("yawSlider")
                    .setBroadcast(false)
                    .setPosition(ctrlSlidersX, ctrlSlidersY + 50)
                    .setSize(200, 20)
                    .setRange(-25, 25)
                    .setValue(0)
                    .setLabel("Yaw")
                    .setSliderMode(Slider.FLEXIBLE);
  yawSlider.onRelease(setpointSender);

  pitchSlider = cp5.addSlider("pitchSlider")
                    .setBroadcast(false)
                    .setPosition(ctrlSlidersX, ctrlSlidersY + 100)
                    .setSize(200, 20)
                    .setRange(-15, 15)
                    .setValue(0)
                    .setLabel("Pitch")
                    .setSliderMode(Slider.FLEXIBLE);
  pitchSlider.onRelease(setpointSender);

  rollSlider = cp5.addSlider("rollSlider")
                    .setBroadcast(false)
                    .setPosition(ctrlSlidersX, ctrlSlidersY + 150)
                    .setSize(200, 20)
                    .setRange(-15, 15)
                    .setValue(0)
                    .setLabel("Roll")
                    .setSliderMode(Slider.FLEXIBLE);
  rollSlider.onRelease(setpointSender);


  xtransSlider = cp5.addSlider("xtransSlider")
                   .setBroadcast(false)
                   .setPosition(ctrlSlidersX, ctrlSlidersY + 200)
                   .setSize(200, 20)
                   .setRange(-50, 50)
                   .setValue(0)
                   .setLabel("X Translation")
                   .setSliderMode(Slider.FLEXIBLE);
  xtransSlider.onRelease(setpointSender);

  ytransSlider = cp5.addSlider("ytransSlider")
                   .setBroadcast(false)
                   .setPosition(ctrlSlidersX, ctrlSlidersY + 250)
                   .setSize(200, 20)
                   .setRange(-50, 50)
                   .setValue(0)
                   .setLabel("Y Translation")
                   .setSliderMode(Slider.FLEXIBLE);
  ytransSlider.onRelease(setpointSender);

  ztransSlider = cp5.addSlider("ztransSlider")
                   .setBroadcast(false)
                   .setPosition(ctrlSlidersX, ctrlSlidersY + 300)
                   .setSize(200, 20)
                   .setRange(-48, 45)
                   .setValue(0)
                   .setLabel("Z Translation")
                   .setSliderMode(Slider.FLEXIBLE);
  ztransSlider.onRelease(setpointSender);

  // ===== GRAPH DEFINITIONS ===== //
  yawGraph = new Graph(yprGraphX, yprGraphY, 200, 120, color(255, 0, 0));
  yawGraph.Title = "Yaw (deg)";
  yawGraph.xLabel = "";
  yawGraph.yLabel = "";
  yawGraph.xMax = 0;
  yawGraph.xMin = -5;
  yawGraph.yMax = 15;
  yawGraph.yMin = -15;
  yawGraph.StrokeColor = foregroundColor;
  
  pitchGraph = new Graph(yprGraphX, yprGraphY + yprGraphYStep, 200, 120, color(255, 0, 0));
  pitchGraph.Title = "Pitch (deg)";
  pitchGraph.xLabel = "";
  pitchGraph.yLabel = "";
  pitchGraph.xMax = 0;
  pitchGraph.xMin = -5;
  pitchGraph.yMax = 15;
  pitchGraph.yMin = -15;
  pitchGraph.StrokeColor = foregroundColor;

  rollGraph = new Graph(yprGraphX, yprGraphY + yprGraphYStep * 2, 200, 120, color(255, 0, 0));
  rollGraph.Title = "Roll (deg)";
  rollGraph.xLabel = "";
  rollGraph.yLabel = "";
  rollGraph.xMax = 0;
  rollGraph.xMin = -5;
  rollGraph.yMax = 15;
  rollGraph.yMin = -15;
  rollGraph.StrokeColor = foregroundColor;

  xtransGraph = new Graph(transGraphX, transGraphY, 200, 120, color(255, 0, 0));
  xtransGraph.Title = "X Translation (mm)";
  xtransGraph.xLabel = "";
  xtransGraph.yLabel = "";
  xtransGraph.xMax = 0;
  xtransGraph.xMin = -5;
  xtransGraph.yMax = 75;
  xtransGraph.yMin = -75;
  xtransGraph.StrokeColor = foregroundColor;

  ytransGraph = new Graph(transGraphX, transGraphY + transGraphYStep, 200, 120, color(255, 0, 0));
  ytransGraph.Title = "Y Translation (mm)";
  ytransGraph.xLabel = "";
  ytransGraph.yLabel = "";
  ytransGraph.xMax = 0;
  ytransGraph.xMin = -5;
  ytransGraph.yMax = 75;
  ytransGraph.yMin = -75;
  ytransGraph.StrokeColor = foregroundColor;

  ztransGraph = new Graph(transGraphX, transGraphY + transGraphYStep * 2, 200, 120, color(255, 0, 0));
  ztransGraph.Title = "Z Translation (mm)";
  ztransGraph.xLabel = "";
  ztransGraph.yLabel = "";
  ztransGraph.xMax = 0;
  ztransGraph.xMin = -5;
  ztransGraph.yMax = 75;
  ztransGraph.yMin = -75;
  ztransGraph.StrokeColor = foregroundColor;

  legLengthGraph = new Graph(ctrlSlidersX, ctrlSlidersY + 370, 200, 120, color(255, 0, 0));
  legLengthGraph.Title = "Leg Lengths (%DC)";
  legLengthGraph.xLabel = "";
  legLengthGraph.yLabel = "";
  legLengthGraph.xMax = 0;
  legLengthGraph.xMin = -5;
  legLengthGraph.yMax = 100; // lim +-10% of stroke
  legLengthGraph.yMin = 0;
  legLengthGraph.StrokeColor = foregroundColor;

  legFeedbackGraph = new Graph(ctrlSlidersX, ctrlSlidersY + 570, 200, 120, color(255, 0, 0));
  legFeedbackGraph.Title = "Leg Feedback (%DC)";
  legFeedbackGraph.xLabel = "";
  legFeedbackGraph.yLabel = "";
  legFeedbackGraph.xMax = 0;
  legFeedbackGraph.xMin = -5;
  legFeedbackGraph.yMax = 100;
  legFeedbackGraph.yMin = 0;
  legFeedbackGraph.StrokeColor = foregroundColor;
}

void parseSerialData(Serial p)
{
  // Buffer has reached linefeed, process incoming data
  String s = p.readStringUntil('\n');
  if(s == null) return;
  s = s.trim();

  if(s.length() > 0)
  {
    if(s.charAt(0) == '0')
    {
      // split s by commas into an array of floats
      String[] data = split(s, ',');

      // === UPDATE VALUES === // 
      // uses firmwware dashbaord format see (send_serial.cpp concatDashboardData() function)
      yaw = Float.parseFloat(data[1]);
      pitch = Float.parseFloat(data[2]);
      roll = Float.parseFloat(data[3]);
      xtrans = Float.parseFloat(data[4]);
      ytrans = Float.parseFloat(data[5]);
      ztrans = Float.parseFloat(data[6]);
      print("LL: ");
      for (int i = 0; i < 6; i++)
      {
        legLengths[i] = Float.parseFloat(data[i + 7]);
        print(legLengths[i] + " ");
      }
      print("\tLFB: ");
      for (int i = 0; i < 6; i++)
      {
        legFeedback[i] = Float.parseFloat(data[i + 13]);
        print(legFeedback[i] + " ");
      }
      println();
      elapsedTime = Float.parseFloat(data[19]);

      // Write to CSV //
      // again uses dashboard format
      datalog.print(yaw + "," + pitch + "," + roll + "," + xtrans + "," + ytrans + "," + ztrans + ",");
      datalog.print(legLengths[0] + "," + legLengths[1] + "," + legLengths[2] + "," + legLengths[3] + "," + legLengths[4] + "," + legLengths[5] + ",");
      datalog.print(legFeedback[0] + "," + legFeedback[1] + "," + legFeedback[2] + "," + legFeedback[3] + "," + legFeedback[4] + "," + legFeedback[5] + "," + elapsedTime + "\n");
    }
    else
    {
      print(" ERROR "); println(s);
    }
  }
  else
  {
    // Incoming message, display
    println(" ERROR ");
  }
}

void update()
{
  long loopTime = millis();

  // Update Loop (20 Hz, same as SendSerial task update rate)
  if(connected && loopTime > lastGraphUpdate + graphUpdateDelay)
  {
    for(int i = 1; i < timeValues.length; i++) // Graph update
    {
      yawValues[i - 1] = yawValues[i];
      pitchValues[i - 1] = pitchValues[i];
      rollValues[i - 1] = rollValues[i];
      xtransValues[i - 1] = xtransValues[i];
      ytransValues[i - 1] = ytransValues[i];
      ztransValues[i - 1] = ztransValues[i];
      for (int j = 0; j < 6; j++)
      {
        legLengthValues[j][i - 1] = legLengthValues[j][i];
        legFeedbackValues[j][i - 1] = legFeedbackValues[j][i];
      }
    }

    yawValues[timeValues.length - 1] = yaw;
    pitchValues[timeValues.length - 1] = pitch;
    rollValues[timeValues.length - 1] = roll;
    xtransValues[timeValues.length - 1] = xtrans;
    ytransValues[timeValues.length - 1] = ytrans;
    ztransValues[timeValues.length - 1] = ztrans;
    for (int i = 0; i < 6; i++)
    {
      legLengthValues[i][timeValues.length - 1] = legLengths[i];
      legFeedbackValues[i][timeValues.length - 1] = legFeedback[i];
    }
    parseSerialData(port);
    lastGraphUpdate += graphUpdateDelay;
  }
}

void posSend() // see senders above
{
  if(notConnected()) return;
  port.write("0" +
             "," + 0.0 +
             "," + 0.0 +
             "," + 0.0 +
             "," + round(xytransCommand.getArrayValue()[0]) +
             "," + round(xytransCommand.getArrayValue()[1]) +
             "," + 0.0 +
             "\n");
}

void posSlideSender()
{
  if(notConnected()) return;
  port.write("0" +
             "," + yawSlider.getValue() +
             "," + pitchSlider.getValue() +
             "," + rollSlider.getValue() +
             "," + xtransSlider.getValue() +
             "," + ytransSlider.getValue() +
             "," + ztransSlider.getValue() +
             "\n");
}

void serialEvent(Serial p) // any time serial data is received
{
  try
  {
    parseSerialData(p);
  }
  catch (Exception e)
  {
    e.printStackTrace();
  }
}

void draw()
{
  update();
  
  background(backgroundColor);
  imageMode(CORNER);
  image(logo, 10, 0, 120, 120);

  // ===== CONTROL SECTION RECTANGLE ===== //
  noStroke();
  fill(controlBackgroundColor);
  rect(ctrlX - 30, yprGraphY - graphBorderYStep * 3, graphBorderXSize + 60, graphBorderYSize + 75);
  stroke(foregroundColor);

  // ===== LEG SECTION RECTANGLE ===== //
  noStroke();
  fill(controlBackgroundColor);
  rect(ctrlX + 300, yprGraphY - graphBorderYStep * 3, graphBorderXSize + 60, graphBorderYSize + 120);
  stroke(foregroundColor);

  // ===== TITLES ===== //
  fill(foregroundColor);
  noStroke();
  textFont(titleFont);
  textAlign(LEFT, CENTER);
  text("Heliospace", 140, 60);

  textFont(largeSectionFont);
  textAlign(LEFT, CENTER);
  text("Platform Orientation", graphBorderXSize - 210, 160);
  text("Control", ctrlX, ctrlY - 50);

  textFont(sectionFont);
  textAlign(CENTER, BOTTOM);
  text("X/Y Pos", ctrlX + 130, ctrlY + 10);
  text("Console", ctrlX + 140, ctrlY + 280);
  text("Manual Orientation", ctrlSlidersX + 100, ctrlY + 10);

  cp5.draw();

  // ===== PLACE IMAGE ===== //
  imageMode(CENTER);
  image(sub, 900, 460, 500, ((float)sub.height / sub.width) * 500);

  // ===== GRAPH BORDERS ===== //
  noStroke();
  fill(controlBackgroundColor);
  rect(yprGraphX - graphBorderXStep, yprGraphY - graphBorderYStep * 3, graphBorderXSize, graphBorderYSize);
  stroke(foregroundColor);

  noStroke();
  fill(controlBackgroundColor);
  rect(transGraphX - graphBorderXStep, yprGraphY - graphBorderYStep * 3, graphBorderXSize, graphBorderYSize);
  stroke(foregroundColor);

  // ===== DRAW GRAPH AXES ===== //
  yawGraph.DrawAxis();
  pitchGraph.DrawAxis();
  rollGraph.DrawAxis();
  xtransGraph.DrawAxis();
  ytransGraph.DrawAxis();
  ztransGraph.DrawAxis();
  legLengthGraph.DrawAxis();
  legFeedbackGraph.DrawAxis();

  // ===== DRAW GRAPH LINES ===== //
  yawGraph.LineGraph(timeValues, yawValues);
  pitchGraph.LineGraph(timeValues, pitchValues);
  rollGraph.LineGraph(timeValues, rollValues);
  xtransGraph.LineGraph(timeValues, xtransValues);
  ytransGraph.LineGraph(timeValues, ytransValues);
  ztransGraph.LineGraph(timeValues, ztransValues);
  for (int i = 0; i < 6; i++) // 12 lines, 6 leg lengths and 6 leg feedbacks
  {
    legLengthGraph.GraphColor = legLengthGraphColors[i];
    legLengthGraph.LineGraph(timeValues, legLengthValues[i]);

    legFeedbackGraph.GraphColor = legLengthGraphColors[i];
    legFeedbackGraph.LineGraph(timeValues, legFeedbackValues[i]);
  }

  // Draw extra telemetry
  fill(foregroundColor);
  noStroke();
  textFont(titleFont);

  // Draw serial port 
  fill(foregroundColor);
  noStroke();
  textFont(sectionFont);
  textAlign(CENTER, BOTTOM);
  text("Selected: " + COMx, 100, connY - 10);

  if(connected)
  {
    text("Connected", 300, connY - 10);
  }
}

// called on program closing
void stop() 
{
  try
  {
    datalog.flush();
    datalog.close();
  }
  catch (Exception e)
  {
    return;
  }
}