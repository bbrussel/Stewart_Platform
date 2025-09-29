#ifndef PID_H
#define PID_H

#include <Arduino.h>


class PID
{
public:
    PID(float _kp, float _ki, float _kd);

    void setSetpoint(float _setpoint);
    void setSetpointRange(float _setpointRange);
    void setOutputFilter(float strength);

    float getOutput(float actual, float _setpoint);
    void clampOutput(float min, float max);

    void setMaxIOutput(float max);

    float getSetpoint();
    float getP();
    float getI();
    float getD();
    float getF();
    float getError();
    float getOutputFilter();

    void reset();
    bool bounded(double value, double min, double max);
    
private:
    float P; // Proportional gain
    float I; // Integral gain
    float D; // Derivative gain
    float F; // Feedforward gain

    float setpoint;
    float error;
    float errorSum;
    float maxError;

    float maxIOutput;

    float lastActual;
    float lastOutput;

    float outputFilter = 0;
    float minOutput, maxOutput;
    float setpointRange = 0;

    bool firstRun = true;
};

#endif