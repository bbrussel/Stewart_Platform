#ifndef ORIENTATION_MATH_H
#define ORIENTATION_MATH_H

#include "BMI088.h"

#include "../Eigen/ArduinoEigenDense.h"

using namespace Eigen;

class IMUOrientation
{
public:
    IMUOrientation() {}
    IMUOrientation(Bmi088Accel _accel, Bmi088Gyro _gyro);

    Bmi088Accel *accel;
    Bmi088Gyro *gyro;

    Eigen::Vector3f gyroRads;

    Quaternionf orientation;
    Eigen::Vector3f eulerOri;
    Quaternionf worldGravity;
    
    Eigen::AngleAxisf axisAng;
    Quaternionf updateQuat;

    void toEuler();
    void toQuaternion(Eigen::Vector3f e);

    void remapAxes();

    void update(float dt);
    void updateFromIMU(float dt);

    void printGyroRads();
    void printOrientationQuat();
    void printEulerAnglesDeg();
};

/*

for (int i = 50; i < 115; i++)
        {
            hexapod.thisLoopMicros = micros();
            float dt = (float)(hexapod.thisLoopMicros - hexapod.lastOriUpdate) / 1000000.;
            hexapod.lastOriUpdate = hexapod.thisLoopMicros;

            hexapod.platformOrientation.pitch = i * 0.05;
            hexapod.calculateLegLengthsAndBase();
            hexapod.calculatePointingVector();
            actuatorDriver.updateLegPositions();
            bus.sendSimData(((double)hexapod.thisLoopMicros / 1000000.));
            delay(100);
        }

*/

#endif