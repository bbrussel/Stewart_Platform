
const int pwmPinLeg1 = 2;
const int pwmPinLeg2 = 3;
const int pwmPinLeg3 = 4;
const int pwmPinLeg4 = 5;
const int pwmPinLeg5 = 6;
const int pwmPinLeg6 = 7;
const int pwmFreqHz = 1000; // Choose a PWM Frequency

const int feedbackPinLeg1 = A9;
const int feedbackPinLeg2 = A8;
const int feedbackPinLeg3 = A7;
const int feedbackPinLeg4 = A6;
const int feedbackPinLeg5 = A5;
const int feedbackPinLeg6 = A4;
const float referenceVoltage = 3.3; // Define the reference voltage
const int adcResolution = 1023; // ADC resolution for a 10-bit ADC
float feedbackBits[6];
float feedbackLengths[6];
int telemetryCounter = 0;

float feedbackCalibrationMultiplier = .9896;
float feedbackCalibrationConstant = -7.7794;

float actuatorClosedLength = 152.0;
float actuatorFullLength = 252.0;
float strokeEndBuffer = 3.0;

float actuatorMinLength = 155.0;
float actuatorMaxLength = 240.0;

float legLengths[6];
float dutyCycles[6];

float lastCommandedLegLengths[6];

int statusCode = 0;
bool outOfRangeFlag = false;

float inputFloats[6]; // Array to hold the parsed input position floats

void setup() {
  setupPWMPins();
  Serial.begin(115200);
}

void parse_leg_length_command(String commandedLegLengths){
  int startIndex = 0; // Start of the substring to extract
  int commaIndex = 0; // Position of the comma in the string
  bool commandErrorFlag = false;

  for (int i = 0; i < 6; i++) {
    // Find the position of the next comma
    commaIndex = commandedLegLengths.indexOf(',', startIndex);
    if (commaIndex == -1) { // No more commas, take the rest of the string
      commaIndex = commandedLegLengths.length();
    }
    String numberString = commandedLegLengths.substring(startIndex, commaIndex);
    legLengths[i] = numberString.toFloat();
    startIndex = commaIndex + 1;
  }

  outOfRangeFlag = false;
  for (int i = 0; i < 6; i++) {
    if ((legLengths[i] < actuatorMinLength) | (legLengths[i] > actuatorMaxLength)) {
      outOfRangeFlag = true;
    }
  }
  if (commandErrorFlag == false) {
    statusCode = 1;
  }
}

void sendTelemetryPacket(){
  Serial.print(telemetryCounter);
  Serial.print(",");
  Serial.print(lastCommandedLegLengths[0]);
  Serial.print(",");
  Serial.print(lastCommandedLegLengths[1]);
  Serial.print(",");
  Serial.print(lastCommandedLegLengths[2]);
  Serial.print(",");
  Serial.print(lastCommandedLegLengths[3]);
  Serial.print(",");
  Serial.print(lastCommandedLegLengths[4]);
  Serial.print(",");
  Serial.print(lastCommandedLegLengths[5]);
  Serial.print(",");

  Serial.print(feedbackLengths[0]);
  Serial.print(",");
  Serial.print(feedbackLengths[1]);
  Serial.print(",");
  Serial.print(feedbackLengths[2]);
  Serial.print(",");
  Serial.print(feedbackLengths[3]);
  Serial.print(",");
  Serial.print(feedbackLengths[4]);
  Serial.print(",");
  Serial.print(feedbackLengths[5]);
  Serial.print(",");

  Serial.print(statusCode);

  Serial.print(",");
  Serial.println(outOfRangeFlag);
}

void getFeedback(){
  feedbackBits[0] = analogRead(feedbackPinLeg1);
  feedbackBits[1] = analogRead(feedbackPinLeg2);
  feedbackBits[2] = analogRead(feedbackPinLeg3);
  feedbackBits[3] = analogRead(feedbackPinLeg4);
  feedbackBits[4] = analogRead(feedbackPinLeg5);
  feedbackBits[5] = analogRead(feedbackPinLeg6);

  feedbackLengths[0] = actuatorFullLength - (feedbackBits[0]/adcResolution)*(actuatorFullLength-actuatorClosedLength);
  feedbackLengths[0] = feedbackCalibrationMultiplier*feedbackLengths[0] + feedbackCalibrationConstant;
  feedbackLengths[1] = actuatorFullLength - (feedbackBits[1]/adcResolution)*(actuatorFullLength-actuatorClosedLength);
  feedbackLengths[1] = feedbackCalibrationMultiplier*feedbackLengths[1] + feedbackCalibrationConstant;
  feedbackLengths[2] = actuatorFullLength - (feedbackBits[2]/adcResolution)*(actuatorFullLength-actuatorClosedLength);
  feedbackLengths[2] = feedbackCalibrationMultiplier*feedbackLengths[2] + feedbackCalibrationConstant;
  feedbackLengths[3] = actuatorFullLength - (feedbackBits[3]/adcResolution)*(actuatorFullLength-actuatorClosedLength);
  feedbackLengths[3] = feedbackCalibrationMultiplier*feedbackLengths[3] + feedbackCalibrationConstant;
  feedbackLengths[4] = actuatorFullLength - (feedbackBits[4]/adcResolution)*(actuatorFullLength-actuatorClosedLength);
  feedbackLengths[4] = feedbackCalibrationMultiplier*feedbackLengths[4] + feedbackCalibrationConstant;
  feedbackLengths[5] = actuatorFullLength - (feedbackBits[5]/adcResolution)*(actuatorFullLength-actuatorClosedLength);
  feedbackLengths[5] = feedbackCalibrationMultiplier*feedbackLengths[5] + feedbackCalibrationConstant;
}

void loop() {
    if (Serial.available() > 0){
      
      String commandedLegLengths = Serial.readString();
      parse_leg_length_command(commandedLegLengths);

      if ((statusCode == 1) & (outOfRangeFlag == false)) {
        // Serial.println("Sending Command to Actuators...");
        sendPositionToActuators();
        for (int i = 0; i < 6; i++) {
          lastCommandedLegLengths[i] = legLengths[i];
        }
      } else {
        Serial.println("Invalid");
      }
    }

    getFeedback();
    sendTelemetryPacket();
    telemetryCounter++;
    delay(50);

}
