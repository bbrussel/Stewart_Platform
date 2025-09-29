const int pwmPin = 3; // Choose a PWM pin. Example: Pin 3
const int pwmFreqHz = 1000; // Choose a PWM Frequency
const int pwmDutyCycle = 50;  // Choose a PWM Duty Cycle

void setup() {
  pinMode(pwmPin, OUTPUT);

  // For Teensy 4.0, you can set the PWM frequency using analogWriteFrequency
  analogWriteFrequency(pwmPin, pwmFreqHz);  // Set PWM frequency to 1kHz
  analogWriteResolution(8);  // 8-bit resolution (0-255)

  analogWrite(pwmPin, (100-pwmDutyCycle)*255/100);  // Vary the PWM duty cycle

}

void loop() {
  // Wait for a short period to make the output readable:
  delay(1000); // Delay for 1 second (1000 milliseconds)
}