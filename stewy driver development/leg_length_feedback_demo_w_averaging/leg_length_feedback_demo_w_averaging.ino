const int pwmPinLeg = 2; // Choose a PWM pin. Example: Pin 3
const int pwmFreqHz = 1000; // Choose a PWM Frequency
float actuatorClosedLength = 152.0;
float actuatorFullLength = 252.0;
float requestedLegLength;
float dutyCycle;
float lastRequestedLengh;

const int feedbackPinLeg = A9;
const float referenceVoltage = 3.296; // Define the reference voltage
const int adcResolution = 1023; // ADC resolution for a 10-bit ADC
float feedbackBits;
float feedbackVoltage;
float calculatedLegLength;

int loopDelay = 300;

const int stackSize = 6;
float stack[stackSize]; // Stack to hold the last 6 values
int topIndex = -1;
void push(int value) {
  if (topIndex < stackSize - 1) {
    topIndex++;
    stack[topIndex] = value;
  } else {
    for(int i = 1; i < stackSize; i++) {
      stack[i - 1] = stack[i];
    }
    stack[topIndex] = value;
  }
}

void printAverage() {
  if (topIndex == -1) {
    // If the stack is empty, there's nothing to average
    Serial.println("Stack is empty.");
  } else {
    float sum = 0; // Use a float for the sum to ensure the average calculation is accurate
    for (int i = 0; i <= topIndex; i++) {
      sum += stack[i];
    }
    float average = sum / (topIndex + 1); // Calculate the average
    Serial.print("Average of stack values: ");
    Serial.println(average, 2); // Print the average with two decimal places
  }
}



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
      lastRequestedLengh = requestedLegLength.toFloat();
      Serial.println(requestedLegLength);
      dutyCycle = 100*(requestedLegLength.toFloat()-actuatorClosedLength)/(actuatorFullLength-actuatorClosedLength);
      analogWrite(pwmPinLeg, (dutyCycle)*255/100);
    } else {
      Serial.println("Invalid Leg Length Request");
    }
  }
  feedbackBits = analogRead(feedbackPinLeg);
  feedbackVoltage = (feedbackBits * referenceVoltage) / adcResolution;
  calculatedLegLength = actuatorFullLength - (feedbackBits/adcResolution)*(actuatorFullLength-actuatorClosedLength);
  Serial.println("");
  Serial.print("Requested:");
  Serial.print(lastRequestedLengh);
  Serial.println(" mm");
  Serial.print("Calculated:");
  Serial.print(calculatedLegLength);
  Serial.println(" mm");
  push(calculatedLegLength);
  printAverage();
  delay(loopDelay);
}
