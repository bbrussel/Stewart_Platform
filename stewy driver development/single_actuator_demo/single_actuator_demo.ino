#include <Arduino.h>

const int pwmPin = 2; // Choose a PWM pin. Example: Pin 3
const int pwmFreqHz = 1000; // Choose a PWM Frequency

//variables for handling input commands from serial port
const byte numChars = 4;
char receivedChars[numChars];   // an array to store the received data
boolean newInputCommand = false;

int commandedBits;

void checkForSerialInput() {
    static byte ndx = 0;
    char endMarker = '\n';
    char rc;
    
    while (Serial.available() > 0 && newInputCommand == false) {
        rc = Serial.read();
        if (rc != endMarker) {
            receivedChars[ndx] = rc;
            ndx++;
            if (ndx >= numChars) {
                ndx = numChars - 1;
            }
        }
        else {
            receivedChars[ndx] = '\0'; // terminate the string
            ndx = 0;
            newInputCommand = true;
        }
    }
}


void setup() {
  Serial.println("\n\n\n\n\n#################################################\n\nStarting Simple Acutator Demo");
  pinMode(pwmPin, OUTPUT);
  analogWriteFrequency(pwmPin, pwmFreqHz);  // Set PWM frequency to 1kHz

  commandedBits = ((50))*255/100;
  analogWrite(pwmPin, commandedBits);
  Serial.begin(115200);
}

void loop() {
    checkForSerialInput();
    if (newInputCommand == true) {
        Serial.println("\nNew Input:");
        Serial.println(receivedChars);
        commandedBits = ((atoi(receivedChars)))*255/100;
        Serial.println(commandedBits);
        analogWrite(pwmPin, commandedBits);
        newInputCommand = false;
    }
    delay(1000);
}
