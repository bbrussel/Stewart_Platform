#ifndef DATA_BUS_H
#define DATA_BUS_H

#include <Arduino.h>
#include <vector>

// https://forum.pjrc.com/threads/66265-Fastest-way-to-transfer-data-to-from-Teensy-4-0-4-1-and-Windows-10
// https://forum.arduino.cc/t/demo-sending-binary-data-from-pc-to-arduino/254004/3

class ActuatorDriver;
class StewartPlatform;

class DataBus
{
public:
    ActuatorDriver* driver;

    void sendGeometry();
    void sendOriData();

    void sendMiscData(std::vector<double> data);

    void sendLegLengths();
    void sendSimData(float time);

    void sendDashboardData(int sendState, float elapsedTime);
    void sendDBData(int sendState, float elapsedTime);
    
private:
    bool connected = false; // true when connected to python viewer
    String concatActuatorData(float time);
};


/*
In the future a buffer design is probably the way to go, parsing data into a string sending commands / data to a fifo buffer 
Sending buffer contents to serial
Reading the contents into a python fifo
Parsing the data in python
Displaying the data 
*/

#endif