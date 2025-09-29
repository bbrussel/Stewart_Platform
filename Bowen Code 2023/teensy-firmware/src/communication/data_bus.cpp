#include <Arduino.h>

#include "data_bus.h"
#include "../stewart-platform/stewart_platform.h"
#include "../actuator_driver/actuator_driver.h"

void DataBus::sendGeometry()
{
    String r;
    r.append("VIZ");
    r.append(driver->hexapod->geometry.baseRadius);
    r.append(",");
    r.append(driver->hexapod->geometry.platformRadius);
    r.append(",");
    r.append(driver->hexapod->geometry.actuatorClosedLength);
    r.append(",");
    r.append(driver->hexapod->geometry.actuatorFullLength);
    r.append(",");
    r.append(driver->hexapod->geometry.baseAnchorAngleDegrees);
    r.append(",");
    r.append(driver->hexapod->geometry.platformAnchorAngleDegrees);
    r.append(",");
    r.append(driver->hexapod->geometry.refRotationDegrees);
    r.append(",");
    r.append(driver->hexapod->geometry.actuatorStrokeFaultMargin);
    r.append(",");
    r.append(driver->hexapod->geometry.actuatorStrokeWarningMargin);
    r.append(",");
    r.append(driver->hexapod->geometry.warningMinLength);
    r.append(",");
    r.append(driver->hexapod->geometry.warningMaxLength);
    r.append(",");
    r.append(driver->hexapod->geometry.faultMinLength);
    r.append(",");
    r.append(driver->hexapod->geometry.faultMaxLength);
    Serial.println(r);
}

void DataBus::sendOriData()
{
    Serial.print("w");
    Serial.print(driver->hexapod->measuredOrientation.orientation.w());
    Serial.print("w");
    Serial.print("a");
    Serial.print(driver->hexapod->measuredOrientation.orientation.x());
    Serial.print("a");
    Serial.print("b");
    Serial.print(driver->hexapod->measuredOrientation.orientation.y());
    Serial.print("b");
    Serial.print("c");
    Serial.print(driver->hexapod->measuredOrientation.orientation.z());
    Serial.print("c");
    Serial.print("\n");
}

void DataBus::sendMiscData(std::vector<double> data)
{
    for (double &i : data)
    {
        Serial.print(i);
        Serial.print(",");
    }
}

void DataBus::sendLegLengths()
{
    String r;
    r.append("LL");
    r.append(",");
    for (int i = 0; i < 5; i++)
    {
        r.append(driver->hexapod->legLengths[i]);
        r.append(",");
    }
    r.append(driver->hexapod->legLengths[5]);
    Serial.println(r);
}

String DataBus::concatActuatorData(float time)
{
    String r;
    r.append("ACTUATORDATA");
    r.append(",");
    r.append(time);
    r.append(",");
    for (int i = 0; i < 6; i++)
    {
        r.append(i);
        r.append(",");
        r.append(driver->actuator[i].position);
        r.append(",");
        r.append(driver->actuator[i].feedbackValue);
        r.append(",");
        r.append(driver->actuator[i].error);
        r.append(",");
    }
    return r;
}

void DataBus::sendSimData(float time)
{
    String r;
    r.append("TEENSYSTART");
    // LEG POSITIONS
    r.append("LEGPOS");
    r.append(",");
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 6; j++)
        {
            r.append(driver->hexapod->legPositions(i, j));
            r.append(",");
        }
    }
    // LEG LENGTHS
    r.append("LEGLEN");
    r.append(",");
    for (int i = 0; i < 6; i++)
    {
        r.append(driver->hexapod->legLengths[i]);
        r.append(",");
    }
    // BASE POSITION
    r.append("BASEPOS");
    r.append(",");
    for (int i = 0; i < 3; i++)
    {
        for(int j = 0; j < 6; j++)
        {
            r.append(driver->hexapod->baseAnchorPositions(i, j));
            r.append(",");
        }
    }
    r.append("PLATPOS");
    r.append(",");
    for (int i = 0; i < 3; i++)
    {
        for(int j = 0; j < 6; j++)
        {
            r.append(driver->hexapod->platformAnchorPositions(i, j));
            r.append(",");
        }
    }
    r.append("ASSEMGEO");
    r.append(",");
    r.append(driver->hexapod->geometry.baseRadius);
    r.append(",");
    r.append(driver->hexapod->geometry.platformRadius);
    r.append(",");
    r.append(driver->hexapod->geometry.actuatorClosedLength);
    r.append(",");
    r.append(driver->hexapod->geometry.actuatorFullLength);
    r.append(",");
    r.append(driver->hexapod->geometry.baseAnchorAngleDegrees);
    r.append(",");
    r.append(driver->hexapod->geometry.platformAnchorAngleDegrees);
    r.append(",");
    r.append(driver->hexapod->geometry.refRotationDegrees);
    r.append(",");
    r.append(driver->hexapod->geometry.actuatorStrokeFaultMargin);
    r.append(",");
    r.append(driver->hexapod->geometry.actuatorStrokeWarningMargin);
    r.append(",");
    r.append(driver->hexapod->geometry.warningMinLength);
    r.append(",");
    r.append(driver->hexapod->geometry.warningMaxLength);
    r.append(",");
    r.append(driver->hexapod->geometry.faultMinLength);
    r.append(",");
    r.append(driver->hexapod->geometry.faultMaxLength);
    r.append("PVEC");
    r.append(",");
    for (int i = 0; i < 3; i++)
    {
        r.append(driver->hexapod->pointingVector.home[i]);
        r.append(",");
    }
    for (int i = 0; i < 3; i++)
    {
        r.append(driver->hexapod->pointingVector.tip[i]);
        r.append(",");
    }
    r.append(concatActuatorData(time));
    r.append("TEENSYEND");
    Serial.println(r);
}

void DataBus::sendDashboardData(int sendState, float elapsedTime)
{
    Serial.print(sendState);
    Serial.print(",");
    Serial.print(driver->hexapod->platformOrientation.yaw);
    Serial.print(",");
    Serial.print(driver->hexapod->platformOrientation.pitch);
    Serial.print(",");
    Serial.print(driver->hexapod->platformOrientation.roll);
    Serial.print(",");
    Serial.print(driver->hexapod->platformOrientation.xTranslation);
    Serial.print(",");
    Serial.print(driver->hexapod->platformOrientation.yTranslation);
    Serial.print(",");
    Serial.print(driver->hexapod->platformOrientation.zTranslation);
    for (int i = 0; i < 6; i++)
    {
        Serial.print(",");
        Serial.print(driver->positionToPercent(driver->hexapod->legLengths[i]));
    }
    for (int i = 0; i < 6; i++)
    {
        Serial.print(",");
        Serial.print(driver->bitsToPercent(analogRead(driver->actuator[i].feedbackPin))); // Serial.print(driver->bitsToPercent(analogRead(driver->actuator[i].feedbackPin)));
    }
    Serial.print(",");
    Serial.print(elapsedTime);
    Serial.print("\n");
}

void DataBus::sendDBData(int sendState, float elapsedTime) // change Serail to Serial2 (export data to esp32 -> influxdb -> grafana)
{
    Serial1.print(sendState);
    Serial1.print(",");
    Serial1.print(driver->hexapod->platformOrientation.yaw);
    Serial1.print(",");
    Serial1.print(driver->hexapod->platformOrientation.pitch);
    Serial1.print(",");
    Serial1.print(driver->hexapod->platformOrientation.roll);
    Serial1.print(",");
    Serial1.print(driver->hexapod->platformOrientation.xTranslation);
    Serial1.print(",");
    Serial1.print(driver->hexapod->platformOrientation.yTranslation);
    Serial1.print(",");
    Serial1.print(driver->hexapod->platformOrientation.zTranslation);
    for (int i = 0; i < 6; i++)
    {
        Serial1.print(",");
        Serial1.print(driver->positionToPercent(driver->hexapod->legLengths[i]));
    }
    Serial1.print(",");
    Serial1.print(elapsedTime);
    
    Serial1.print("\n");
}