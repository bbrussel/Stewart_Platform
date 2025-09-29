

void checkLegLengths(float legLengths[6], bool& strokeTooLongError, bool& strokeTooShortError) {
  strokeTooShortError = false;
  strokeTooLongError = false;
  for (int i = 0; i < 6; i++) {
    if (legLengths[i] < actuatorClosedLength + strokeEndBuffer) {
      strokeTooShortError = true;
    }
    if (legLengths[i] > actuatorFullLength - strokeEndBuffer) {
      strokeTooLongError = true;
    }
  }


}

void sendPositionToActuators() {
  dutyCycles[0] = 100*(legLengths[0]-actuatorClosedLength)/(actuatorFullLength-actuatorClosedLength);
  dutyCycles[1] = 100*(legLengths[1]-actuatorClosedLength)/(actuatorFullLength-actuatorClosedLength);
  dutyCycles[2] = 100*(legLengths[2]-actuatorClosedLength)/(actuatorFullLength-actuatorClosedLength);
  dutyCycles[3] = 100*(legLengths[3]-actuatorClosedLength)/(actuatorFullLength-actuatorClosedLength);
  dutyCycles[4] = 100*(legLengths[4]-actuatorClosedLength)/(actuatorFullLength-actuatorClosedLength);
  dutyCycles[5] = 100*(legLengths[5]-actuatorClosedLength)/(actuatorFullLength-actuatorClosedLength);

  analogWrite(pwmPinLeg1, (dutyCycles[0])*255/100);
  analogWrite(pwmPinLeg2, (dutyCycles[1])*255/100);
  analogWrite(pwmPinLeg3, (dutyCycles[2])*255/100);
  analogWrite(pwmPinLeg4, (dutyCycles[3])*255/100);
  analogWrite(pwmPinLeg5, (dutyCycles[4])*255/100);
  analogWrite(pwmPinLeg6, (dutyCycles[5])*255/100);
}

void setupPWMPins() {
  pinMode(pwmPinLeg1, OUTPUT);
  pinMode(pwmPinLeg2, OUTPUT);
  pinMode(pwmPinLeg3, OUTPUT);
  pinMode(pwmPinLeg4, OUTPUT);
  pinMode(pwmPinLeg5, OUTPUT);
  pinMode(pwmPinLeg6, OUTPUT);
  analogWriteFrequency(pwmPinLeg1, pwmFreqHz);  // Set PWM frequency to 1kHz
  analogWriteFrequency(pwmPinLeg2, pwmFreqHz);  // Set PWM frequency to 1kHz
  analogWriteFrequency(pwmPinLeg3, pwmFreqHz);  // Set PWM frequency to 1kHz
  analogWriteFrequency(pwmPinLeg4, pwmFreqHz);  // Set PWM frequency to 1kHz
  analogWriteFrequency(pwmPinLeg5, pwmFreqHz);  // Set PWM frequency to 1kHz
  analogWriteFrequency(pwmPinLeg6, pwmFreqHz);  // Set PWM frequency to 1kHz
}

bool parsePositionInputString(String& input, float resultArray[], int maxSize) {
  int actualSize = 0;
  int startIndex = 0;
  int endIndex = 0;
  while ((endIndex = input.indexOf(',', startIndex)) != -1 || startIndex < (int)input.length()) {
    if (endIndex == -1) endIndex = input.length();
    String floatString = input.substring(startIndex, endIndex);
    float floatValue = floatString.toFloat();
    
    // Directly store the parsed floatValue
    if (actualSize < maxSize) {
      resultArray[actualSize++] = floatValue;
    } else {
      // Exceeded expected size, return false
      return false;
    }
    startIndex = endIndex + 1;
  }
  
  // Check if the actual number of parsed floats matches the expected count
  return actualSize == 6;
}