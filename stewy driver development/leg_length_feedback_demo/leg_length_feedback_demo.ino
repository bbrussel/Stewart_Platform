const int pwmPinLeg = 2; // Choose a PWM pin. Example: Pin 3
const int pwmFreqHz = 1000; // Choose a PWM Frequency
float actuatorClosedLength = 152.0;
float actuatorFullLength = 252.0;
float requestedLegLength;
float dutyCycle;

const int feedbackPinLeg = A9;
const float referenceVoltage = 3.296; // Define the reference voltage
const int adcResolution = 1023; // ADC resolution for a 10-bit ADC
float feedbackBits;
float feedbackVoltage;

int loopDelay = 1000;

void setup() {
  Serial.println("\n\n\n\n\n#################################################\n\nStarting Simple Leg Length Feedback Demo");
  Serial.begin(115200);
  pinMode(pwmPinLeg, OUTPUT);  // Set pin to output mode
  analogWriteFrequency(pwmPinLeg, pwmFreqHz);  // Set PWM frequency to 1kHz
}
void loop() {
  if (Serial.available() > 0){
    String requestedLegLength = Serial.readString();
    requestedLegLength.trim();
    if (requestedLegLength.toFloat() >= actuatorClosedLength && requestedLegLength.toFloat() <= actuatorFullLength) {
      Serial.print("Commanded to:");
      Serial.println(requestedLegLength);
      dutyCycle = 100*(requestedLegLength.toFloat()-actuatorClosedLength)/(actuatorFullLength-actuatorClosedLength);
      analogWrite(pwmPinLeg, (dutyCycle)*255/100);
    } else {
      Serial.println("Invalid Leg Length Request");
    }
  }
  feedbackBits = analogRead(feedbackPinLeg);
  feedbackVoltage = (feedbackBits * referenceVoltage) / adcResolution;
  Serial.print(actuatorFullLength - (feedbackBits/adcResolution)*(actuatorFullLength-actuatorClosedLength));
  Serial.println("mm");
  delay(loopDelay);
}
