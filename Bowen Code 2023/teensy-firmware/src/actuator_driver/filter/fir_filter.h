#ifndef FIR_FILTER
#define FIR_FILTER

#include <Arduino.h>


template <typename T, int ntaps> // https://github.com/LeemanGeophysicalLLC/FIR_Filter_Arduino_Library/blob/master/src/FIR.tpp
class FIR
{
public:
    FIR();

    void setGain(T newgain);
    T getGain();

    void setFilterCoeffs(T *coeffs);
    T processReading(T newval);

private:
    T values[ntaps];
    T fir_coeffs[ntaps];
    T gain;
    int k;
};

#endif