#ifndef ACTUATOR_DRIVER_H
#define ACTUATOR_DRIVER_H

#include <Arduino.h>
#include "../lib/Teensy_PWM/Teensy_PWM.h"
#include "filter/fir_filter.h"

class StewartPlatform; // forward declaration 

class ActuatorDriver
{
public:
    ActuatorDriver();

    StewartPlatform* hexapod;
    Teensy_PWM *pwm[6];

    struct ActuatorData
    {
        uint8_t pin;
        uint8_t feedbackPin;
        
        float feedbackValue;
        float error;

        float position;
        float duty;

        bool actuating = false;
    };
    ActuatorData actuator[6];

    FIR<float, 4> legFeedbackFIR[6];

    bool invalidPositionReached;

    void initFIRFilters();

    void sendLegPositionsWithoutFeedback();

    // Tests
    void testActuatorFromDuty(float duty[6]);

    // Utils
    int bitsToPercent(int bits); // all for converting between leg positions (float), duty cycle (percent) and adc feedback (bits)
    int positionToPercent(float position);

private:
    void updateActuatorData(int i);

    String commandString; // contain command string to send / recieve from serial

    // Utils
    float bitsToPosition(int bits);
    int percentToBits(int percent);
    
    void oldClamp(int i);
};

#endif