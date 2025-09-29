#include "actuator_driver.h"
#include "stewart-platform/stewart_platform.h"


#define DEFAULT_DUTY 0.0f
#define DEFAULT_FREQ 1000.0f

#define CORRECTION_FACTOR 2.0f;


ActuatorDriver::ActuatorDriver() // default initialize all pins to match controller schematic
{
    //     Kicad Schematic Pinout
    // ---------------------------------
    // PIN # | PWM  | FEEDBACK | NAME |
    //     2 | PWM1 | A9       | FB1  |
    //     3 | PWM2 | A8       | FB2  |
    //     4 | PWM3 | A7       | FB3  |
    //     5 | PWM4 | A6       | FB4  |
    //     6 | PWM5 | A5       | FB5  |
    //     7 | PWM6 | A4       | FB6  |
    // ---------------------------------
    actuator[0] = ActuatorData{
        2,
        A9,
        0,
        DEFAULT_FREQ
    };
    pwm[0] = new Teensy_PWM(actuator[0].pin, DEFAULT_FREQ, DEFAULT_DUTY);

    actuator[1] = ActuatorData{
        3,
        A8,
        0,
        DEFAULT_FREQ
    };
    pwm[1] = new Teensy_PWM(actuator[1].pin, DEFAULT_FREQ, DEFAULT_DUTY);

    actuator[2] = ActuatorData{
        4,
        A7,
        0,
        DEFAULT_FREQ
    };
    pwm[2] = new Teensy_PWM(actuator[2].pin, DEFAULT_FREQ, DEFAULT_DUTY);

    actuator[3] = ActuatorData{
        5,
        A6,
        0,
        DEFAULT_FREQ
    };
    pwm[3] = new Teensy_PWM(actuator[3].pin, DEFAULT_FREQ, DEFAULT_DUTY);

    actuator[4] = ActuatorData{
        6,
        A5,
        0,
        DEFAULT_FREQ
    };
    pwm[4] = new Teensy_PWM(actuator[4].pin, DEFAULT_FREQ, DEFAULT_DUTY);

    actuator[5] = ActuatorData{
        7,
        A4,
        0,
        DEFAULT_FREQ
    };
    pwm[5] = new Teensy_PWM(actuator[5].pin, DEFAULT_FREQ, DEFAULT_DUTY);
}

void ActuatorDriver::initFIRFilters()
{
    float coef[4] = { 1., 1., 1., 1.}; // 4 smoothing gains
    for (int i = 0; i < 6; i++)
    {
        legFeedbackFIR[i].setFilterCoeffs(coef);
    }
    // .processReading(i)
}

void ActuatorDriver::oldClamp(int i)
{
    if (hexapod->legLengths[i] > hexapod->geometry.warningMaxLength)
        hexapod->legLengths[i] = hexapod->geometry.warningMaxLength;
    if (hexapod->legLengths[i] < hexapod->geometry.warningMinLength)
        hexapod->legLengths[i] = hexapod->geometry.warningMinLength;
    invalidPositionReached = false;
} // only used for testing max and min lengths (REMOVE AFTER TEST ASAP)

void ActuatorDriver::updateActuatorData(int i)
{
    if (hexapod->legLengths[i] > hexapod->geometry.warningMaxLength || hexapod->legLengths[i] < hexapod->geometry.warningMinLength) invalidPositionReached = true;
    actuator[i].position = hexapod->legLengths[i];

    actuator[i].duty = positionToPercent(actuator[i].position);
    if (actuator[i].duty == 100.0f) actuator[i].duty = 99.9f; // 100 stalls the actuators

    // actuator[i].feedbackValue = bitsToPercent(analogRead(actuator[i].feedbackPin));

    actuator[i].error = actuator[i].duty - actuator[i].feedbackValue;
}

void ActuatorDriver::sendLegPositionsWithoutFeedback()
{
    invalidPositionReached = false;
    for (int i = 0; i < 6; i++)
    {
        updateActuatorData(i); 
    }
    if (!invalidPositionReached) 
    {
        for (int i = 0; i < 6; i++)
        {
            pwm[i]->setPWM(actuator[i].pin, DEFAULT_FREQ, actuator[i].duty);
        }
    }
}

// === Tests ===
void ActuatorDriver::testActuatorFromDuty(float duty[6]) // aIndex = index of actuator in ActuatorData array
{
    for (int i = 0; i < 6; i++)
    {
        pwm[i]->setPWM(actuator[i].pin, DEFAULT_FREQ, duty[i]); // send command to actuator
    }
}

// === Utils ===

// percent to bits: bits = ((percent/100.00)*255*.84);

int ActuatorDriver::percentToBits(int percent)
{  
  return ((percent / 100.00)  * 255 * .84);
}

int ActuatorDriver::bitsToPercent(int bits)
{
    return map(bits, 1010, 416, 0, 100) + CORRECTION_FACTOR;
}

float ActuatorDriver::bitsToPosition(int bits)
{
    return map(bits, 1023, 0, hexapod->geometry.actuatorClosedLength, hexapod->geometry.actuatorFullLength);
}

int ActuatorDriver::positionToPercent(float position)
{
    return ((position - hexapod->geometry.actuatorClosedLength) / (hexapod->geometry.actuatorFullLength - hexapod->geometry.actuatorClosedLength)) * 100;
}