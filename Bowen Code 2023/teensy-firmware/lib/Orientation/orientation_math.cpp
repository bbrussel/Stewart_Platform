#include "orientation_math.h"

IMUOrientation::IMUOrientation(Bmi088Accel _accel, Bmi088Gyro _gyro)
{
    // Sensing - https://github.com/bolderflight/bmi088-arduino/tree/main
    accel = &_accel;
    gyro = &_gyro;

    orientation = Quaternionf::Identity();
    worldGravity = Quaternionf::Identity();
}

void IMUOrientation::toEuler()
{
    eulerOri = orientation.toRotationMatrix().eulerAngles(0, 1, 2);
}

void IMUOrientation::toQuaternion(Eigen::Vector3f e)
{
    orientation = AngleAxisf(e(0), Vector3f::UnitX()) * AngleAxisf(e(1), Vector3f::UnitY()) * AngleAxisf(e(2), Vector3f::UnitZ());
}

void IMUOrientation::update(float dt)
{
    float norm = gyroRads.norm();

    axisAng = Eigen::AngleAxisf((dt * norm), (gyroRads / norm));
    updateQuat = Quaternionf(axisAng);

    orientation = orientation * updateQuat;
}

void IMUOrientation::updateFromIMU(float dt)
{
    accel->readSensor();
    gyro->readSensor();
    gyroRads << gyro->getGyroX_rads(), gyro->getGyroY_rads(), gyro->getGyroZ_rads();

    auto norm = gyroRads.norm();
    float angle = dt * norm;
    Eigen::Vector3f axis = gyroRads / norm;

    AngleAxisf aa(angle, axis);
    Quaternionf updateQuat(aa);

    orientation = orientation * updateQuat;
}



void IMUOrientation::printGyroRads()
{
    Serial.print("G X: ");
    Serial.print(gyroRads.x());
    Serial.print("\t");
    Serial.print("G Y: ");
    Serial.print(gyroRads.y());
    Serial.print("\t");
    Serial.print("G Z: ");
    Serial.print(gyroRads.z());
    Serial.print("\n");
}

void IMUOrientation::printOrientationQuat()
{
    Serial.print("OriQ X: ");
    Serial.print(orientation.x());
    Serial.print("\t");
    Serial.print("OriQ Y: ");
    Serial.print(orientation.y());
    Serial.print("\t");
    Serial.print("OriQ Z: ");
    Serial.print(orientation.z());
    Serial.print("\n");
}

void IMUOrientation::printEulerAnglesDeg()
{
    Serial.print("Ori X: ");
    Serial.print(eulerOri.x() * RAD_TO_DEG);
    Serial.print("\t");
    Serial.print("Ori Y: ");
    Serial.print(eulerOri.y() * RAD_TO_DEG);
    Serial.print("\t");
    Serial.print("Ori Z: ");
    Serial.print(eulerOri.z() * RAD_TO_DEG);
    Serial.print("\n");
}