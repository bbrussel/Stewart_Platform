#include "PID.h"


PID::PID(float _kp, float _ki, float _kd)
{
    P = _kp;
    I = _ki;
    D = _kd;
}

void PID::setSetpoint(float _setpoint)
{
    setpoint = _setpoint;
}

void PID::setSetpointRange(float strength)
{
    if (strength == 0 || bounded(strength, 0, 1))
    {
        outputFilter = strength;
    }
}

void PID::setOutputFilter(float _outputFilter)
{
    outputFilter = _outputFilter;
}

void PID::setMaxIOutput(float max)
{
    maxIOutput = max;
    if (I != 0)
    {
        maxError = maxIOutput / I;
    }
}

void PID::clampOutput(float min, float max)
{
    if (max < min) return;
    minOutput = min;
    maxOutput = max;

    if (maxIOutput == 0 || maxIOutput > (maxOutput - minOutput))
    {
        setMaxIOutput(max - min);
    }
}


float PID::getOutput(float actual, float _setpoint)
{
    float output;
    float pOutput, iOutput, dOutput, fOutput;

    setpoint = _setpoint;
    if (setpointRange != 0)
    {
        setpoint=constrain(setpoint, -setpointRange, setpointRange);
    }

    error = setpoint - actual;

    // P/F TERM
    pOutput = P * error;
    fOutput = F * setpoint;

    if (firstRun)
    {
        lastActual = actual;
        lastOutput = pOutput + fOutput;
        firstRun = false;
    }

    // D TERM
    dOutput = -D*(actual - lastActual);
    lastActual = actual;

    /*
    I TERM
    Measures to stabilize I: (https://github.com/tekdemo/MiniPID-Java/blob/master/src/com/stormbots/MiniPID.java)
    1. maxIoutput restricts the amount of output contributed by the integral term.
    2. prevent windup by not increasing errorSum if we're already running against our max I output
    3. prevent windup by not increasing errorSum if output is max 
    */
    iOutput = I * errorSum;
    if (maxIOutput != 0)
    {
		iOutput=constrain(iOutput, -maxIOutput, maxIOutput); 
	}    

    // OUTPUT
    output = pOutput + iOutput + dOutput + fOutput;

    // ERROR SUM
    if (minOutput != maxOutput)
    {
        errorSum = error; // reset error sum
    }
    else if(maxIOutput != 0)
    {
        errorSum = constrain(errorSum + error, -maxError, maxError); // prevent I windup
    }
    else
    {
        errorSum += error;
    }

    // OUTPUT FILTER
    if (minOutput != maxOutput)
    {
        output = constrain(output, minOutput, maxOutput);
    }
    if (outputFilter != 0)
    {
        output = lastOutput * outputFilter + output * (1 - outputFilter);
    }

    lastOutput = output;
    return output;
}

// === Getters === //
float PID::getSetpoint()
{
    return setpoint;
}

float PID::getP()
{
    return P;
}

float PID::getI()
{
    return I;
}

float PID::getD()
{
    return D;
}

float PID::getF()
{
    return F;
}


float PID::getError()
{
    return error;
}

float PID::getOutputFilter()
{
    return outputFilter;
}

void PID::reset()
{
    firstRun = true;
    errorSum = 0;
}

// Helpers
bool PID::bounded(double value, double min, double max)
{
    return (min < value) && (value < max);
}