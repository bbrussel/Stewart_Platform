#include <Arduino.h>

#include "stewart-platform/stewart_platform.h"
#include "actuator_driver/actuator_driver.h"
#include "communication/data_bus.h"
#include <vector>

#include "BMI088.h"

// === Globals ===
SimState state;
DataBus bus;
StewartPlatform hexapod;
ActuatorDriver actuatorDriver;

// = Dashboard Recieving Globals = //
float tempRecieveVals[6];
float duty[6];
int sendState;
int iterCounter;

// === Sensing ===
Bmi088Accel accel(Wire, 0x19);
Bmi088Gyro gyro(Wire, 0x69);
float oldTempRecieveVals[6];

// === Task Times ===
struct TaskTime
{
    uint64_t thisLoopMicros = 0;
    uint64_t lastTaskUpdate = 0;
    int taskUpdateDelay = 0;
};
TaskTime serialTime = {0, 0, 1000000 / 200}; // 20 Hz
TaskTime sendTime = {0, 0, 1000000 / 100};  // 10 Hz
TaskTime posChangeTime = {0, 0, 1000000 / 5}; // UNK Hz

TaskTime calcTime = {0, 0, 0}; // 100 Hz
void test_calculationBenchmark()
{
    calcTime.thisLoopMicros = micros();
    uint64_t dtCalcTime = (calcTime.thisLoopMicros - calcTime.lastTaskUpdate);
    calcTime.lastTaskUpdate = calcTime.thisLoopMicros;


    // === Test === //
    hexapod.calculateLegLengthsAndBase();
    hexapod.calculatePointingVector();
    // === End Test === //


    Serial.print("Calculation Time: "); Serial.println(dtCalcTime);
}


void setup()
{
    // === Initial Setup === //
    state = INIT;
    Serial.begin(115200);
    Serial.setTimeout(1);

    // === Hardware Serial === //
    Serial1.begin(115200);
    Serial1.setTimeout(1);

    // === IMU Setup === // 
    /*
    int imuStatus = accel.begin();
    if (imuStatus < 0)
    {
        Serial.println("Accel Initialization Error");
        Serial.println(imuStatus);
        while(1) { }
    }
    imuStatus = gyro.begin();
    if (imuStatus < 0)
    {
        Serial.println("Gyro Initialization Error");
        Serial.println(imuStatus);
        while (1) { }
    }
    */

    // === Pointer Assignment === //
    actuatorDriver.hexapod = &hexapod; // pass pointer to hexapod to actuator driver
    bus.driver = &actuatorDriver;      // pass pointer to actuator driver to data bus
    hexapod.measuredOrientation = IMUOrientation(accel, gyro);

    //  ===Platform and Base Geometry === //
    hexapod.initGeometry();
    hexapod.initPlatformBaseTransform();

    // === Setup Time === //
    sendTime.thisLoopMicros = micros();

    state = INIT;
}


void loop()
{
    switch (state)
    {
        case INIT:
        {
            // === Init Z Translation ===
            hexapod.calculateLegLengthsAndBase(); // set platform to 0
            hexapod.calculatePointingVector();
            actuatorDriver.sendLegPositionsWithoutFeedback();

            state = UPDATE;
            break;
        }

        case UPDATE:
        {
            sendTime.thisLoopMicros = micros();
            double elapsedTime = ((double)sendTime.thisLoopMicros / 1000000.);

            if(sendTime.thisLoopMicros > sendTime.lastTaskUpdate + sendTime.taskUpdateDelay)
            {
                bus.sendDashboardData(0, (float)elapsedTime);
                bus.sendDBData(0, (float)elapsedTime);        // send to esp32->websocket->influxdb->grafana

                sendTime.lastTaskUpdate += sendTime.taskUpdateDelay;
            }

            state = PARSING_SERIAL;
            break;
        }

        case SENDING_DATA:
        {
            /*
            hexapod.thisLoopMicros = micros();
            if (gyro.getDrdyStatus())
            {
                hexapod.platformOrientation.zTranslation = 13;
                hexapod.platformOrientation.yaw = -5;
                float dtOri = (float)(hexapod.thisLoopMicros - hexapod.lastOriUpdate) / 1000000.; // Finds elapsed microseconds since last update, converts to float, and converts to seconds
                hexapod.lastOriUpdate = hexapod.thisLoopMicros;                                   // We have updated, set the new timestamp

                gyro.readSensor();

                hexapod.measuredOrientation.gyroRads << gyro.getGyroX_rads(), gyro.getGyroY_rads(), gyro.getGyroZ_rads();

                hexapod.measuredOrientation.update(dtOri);
                hexapod.measuredOrientation.toEuler();
            }
            */
            // bus.sendDashboardData(0);

            state = UPDATE;
            break;
        }

        case PARSING_SERIAL:
        {
            if (Serial.available())
            {
                String serialIn = Serial.readStringUntil('\n');

                if (serialIn != NULL && sscanf(serialIn.c_str(), "%d, %f,%f,%f,%f,%f,%f",
                                                &sendState,
                                                &tempRecieveVals[0],
                                                &tempRecieveVals[1],
                                                &tempRecieveVals[2],
                                                &tempRecieveVals[3],
                                                &tempRecieveVals[4],
                                                &tempRecieveVals[5]))
                {
                    if (sendState == 0) // Recieving Orientation
                    {
                        hexapod.platformOrientation.yaw = tempRecieveVals[0];
                        hexapod.platformOrientation.pitch = tempRecieveVals[1];
                        hexapod.platformOrientation.roll = tempRecieveVals[2];
                        hexapod.platformOrientation.xTranslation = tempRecieveVals[3];
                        hexapod.platformOrientation.yTranslation = tempRecieveVals[4];
                        hexapod.platformOrientation.zTranslation = tempRecieveVals[5];

                        hexapod.calculateLegLengthsAndBase();
                        hexapod.calculatePointingVector();
                        actuatorDriver.sendLegPositionsWithoutFeedback();
                    }
                    if (sendState == 1) // Recieving Leg Lengths
                    {
                        for (int i = 0; i < 6; i++)
                        {
                            duty[i] = tempRecieveVals[i];
                        }
                        actuatorDriver.testActuatorFromDuty(duty);
                    }
                }
            }

            state = UPDATE;
            break;
        }

        case SENDING_ACTUATORS:
        {
            hexapod.calculateLegLengthsAndBase();
            hexapod.calculatePointingVector();
            actuatorDriver.sendLegPositionsWithoutFeedback();

            state = UPDATE;
            break;
        }
    }
}