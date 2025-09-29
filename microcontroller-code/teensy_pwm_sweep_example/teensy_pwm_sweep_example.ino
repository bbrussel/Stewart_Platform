const int pwmPin = 3; // Choose a PWM pin. Example: Pin 2
const int pwmFreqHz = 1000; // Choose a PWM pin. Example: Pin 2

void setup() {
  pinMode(pwmPin, OUTPUT);

  // For Teensy 4.0, you can set the PWM frequency using analogWriteFrequency
  analogWriteFrequency(pwmPin, pwmFreqHz);  // Set PWM frequency to 1kHz
  analogWriteResolution(8);  // 8-bit resolution (0-255)
}

void loop() {
  for (int i = 0; i <= 255; i++) {
    analogWrite(pwmPin, i);  // Vary the PWM duty cycle
    delay(10);
  }
  for (int i = 255; i >= 0; i--) {
    analogWrite(pwmPin, i);
    delay(10);
  }
}