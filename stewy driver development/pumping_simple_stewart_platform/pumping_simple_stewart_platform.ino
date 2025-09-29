

const int pwmPinLeg1 = 2; // Choose a PWM pin. Example: Pin 3
const int pwmPinLeg2 = 3; // Choose a PWM pin. Example: Pin 3
const int pwmPinLeg3 = 4; // Choose a PWM pin. Example: Pin 3
const int pwmPinLeg4 = 5; // Choose a PWM pin. Example: Pin 3
const int pwmPinLeg5 = 6; // Choose a PWM pin. Example: Pin 3
const int pwmPinLeg6 = 7; // Choose a PWM pin. Example: Pin 3
const int pwmFreqHz = 1000; // Choose a PWM Frequency



class Orientation {
  public:
    float yaw;
    float pitch;
    float roll;
    float xTranslation;
    float yTranslation;
    float zTranslation;

    Orientation(float pitch, float roll, float yaw, float xTranslation, float yTranslation, float zTranslation) {
      this->pitch = pitch;
      this->roll = roll;
      this->yaw = yaw;
      this->xTranslation = xTranslation;
      this->yTranslation = yTranslation;
      this->zTranslation = zTranslation;
    }

    void printOrientation() {
      Serial.print(this->pitch);
      Serial.print(",");
      Serial.print(this->roll);
      Serial.print(",");
      Serial.print(this->yaw);
      Serial.print(",");
      Serial.print(this->xTranslation);
      Serial.print(",");
      Serial.print(this->yTranslation);
      Serial.print(",");
      Serial.println(this->zTranslation);


    }
};


float baseRadius = 220;
float platformRadius = 220;
float actuatorClosedLength = 152.0;
float actuatorFullLength = 252.0;

// mL12-50-100-12-I
// float actuatorClosedLength = 102.0;
// float actuatorFullLength = 152.0;

float baseAnchorAngleDegrees = 32.0;
float platformAnchorAngleDegrees = 50.0;
float refRotationDegrees = 0.0;

float actuatorHomeLength;
float psiB[6];
float psiP[6];

float stroke = (actuatorFullLength - actuatorClosedLength);

Orientation platformOrientation(0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
Orientation baseOrientation(0.0, 0.0, 0.0, 0.0, 0.0, 0.0);

Orientation inputPlatformOrientation = platformOrientation;

float baseAnchorHomeCoords[6][3];
float platformAnchorCoords[6][3];
float platformHomeHeight[6];
float platformHomeTransform[3];

float legLengths[6];

float dutyCycles[6];

bool validInput;
bool strokeTooLongError;
bool strokeTooShortError;
float strokeEndBuffer = 3.0;

bool toggle = false;

void setup() {

  Serial.println("\n\n\n\n\n#################################################\n\nStarting Simple Stewart Controller");

  setupPWMPins();

  Serial.begin(115200);
  actuatorHomeLength = actuatorClosedLength + (stroke/2);
  calculatePsiB(psiB, baseAnchorAngleDegrees, refRotationDegrees);
  calculatePsiP(psiP, platformAnchorAngleDegrees, refRotationDegrees);
  calculateBaseAnchorHomeCoords(baseAnchorHomeCoords, psiB, baseRadius);
  calculatePlatformAnchorCoords(platformAnchorCoords, psiP, platformRadius);
  calculatePlatformHomeTransform(platformHomeTransform, baseAnchorHomeCoords, platformAnchorCoords, actuatorHomeLength);


  calculateLegLengthsAndBase(legLengths, baseAnchorHomeCoords, platformAnchorCoords, platformHomeTransform, baseOrientation, platformOrientation);

  sendPositionToActuators();

  Serial.println("Leg Lengths(mm):");
  printArray(legLengths, 6);

}

void loop() {

  if (toggle) {
    platformOrientation.zTranslation = 5.0;
    // platformOrientation.xTranslation = 5.0;
    calculateLegLengthsAndBase(legLengths, baseAnchorHomeCoords, platformAnchorCoords, platformHomeTransform, baseOrientation, platformOrientation);
  } else {
    platformOrientation.zTranslation = -5.0;
    // platformOrientation.xTranslation = -5.0;
    calculateLegLengthsAndBase(legLengths, baseAnchorHomeCoords, platformAnchorCoords, platformHomeTransform, baseOrientation, platformOrientation);
  }

  sendPositionToActuators();

  toggle = !toggle;
  delay(100);



    // 
  

}
