// Basic demo for readings from Adafruit BNO08x
#include <Adafruit_BNO08x.h>

#define BNO08X_RESET -1

Adafruit_BNO08x  bno08x(BNO08X_RESET);

sh2_SensorValue_t sensorValue;

void setReports(void) {
  Serial.println("Setting desired reports");
  if (! bno08x.enableReport(SH2_ROTATION_VECTOR)) {
    Serial.println("Could not enable game vector");
  }
}

void tare(void) {
  delay(100);
  if (sh2_setTareNow(0x07, SH2_TARE_BASIS_ROTATION_VECTOR) == SH2_OK) { // Assuming SH2_OK is the success status
    Serial.println("Tare successful. Current orientation set as reference.");
  } else {
    Serial.println("Tare failed.");
  }
}

void setup(void) {
  Serial.begin(115200);
  while (!Serial) delay(10);
  Serial.println("Starting Heliospace IMU Driver");
  if (!bno08x.begin_I2C()) {
    Serial.println("Failed to find BNO085 chip");
    while (1) { delay(10); }
  }
  Serial.println("BNO085 Found!");
  setReports();
  tare();
  Serial.println("Reading events");
  delay(100);
}


void loop() {
  delay(100);

  if (bno08x.wasReset()) {
    Serial.print("sensor was reset ");
    setReports();
  }
  
  if (! bno08x.getSensorEvent(&sensorValue)) {
    return;
  }
  
  switch (sensorValue.sensorId) {
    case SH2_ROTATION_VECTOR:
      Serial.print("Rotation Vector - r: ");
      Serial.print(sensorValue.un.rotationVector.real);
      Serial.print(" i: ");
      Serial.print(sensorValue.un.rotationVector.i);
      Serial.print(" j: ");
      Serial.print(sensorValue.un.rotationVector.j);
      Serial.print(" k: ");
      Serial.print(sensorValue.un.rotationVector.k);
      Serial.print(" accuracy: ");
      Serial.println(sensorValue.un.rotationVector.accuracy);
      break;
  }

}