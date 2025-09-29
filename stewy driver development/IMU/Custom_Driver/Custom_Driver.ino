// Basic demo for readings from Adafruit BNO08x
#include <Adafruit_BNO08x.h>

#define BNO08X_RESET -1

Adafruit_BNO08x  bno08x(BNO08X_RESET);

struct euler_t {
  float yaw;
  float pitch;
  float roll;
} ypr;

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

void quaternionToEuler(float qr, float qi, float qj, float qk, euler_t* ypr, bool degrees) {

    float sqr = sq(qr);
    float sqi = sq(qi);
    float sqj = sq(qj);
    float sqk = sq(qk);

    ypr->yaw = atan2(2.0 * (qi * qj + qk * qr), (sqi - sqj - sqk + sqr));
    ypr->pitch = asin(-2.0 * (qi * qk - qj * qr) / (sqi + sqj + sqk + sqr));
    ypr->roll = atan2(2.0 * (qj * qk + qi * qr), (-sqi - sqj + sqk + sqr));

    if (degrees) {
      ypr->yaw *= RAD_TO_DEG;
      ypr->pitch *= RAD_TO_DEG;
      ypr->roll *= RAD_TO_DEG;
    }
}

void quaternionToEulerRV(sh2_RotationVectorWAcc_t* rotational_vector, euler_t* ypr, bool degrees) {
    quaternionToEuler(rotational_vector->real, rotational_vector->i, rotational_vector->j, rotational_vector->k, ypr, degrees);
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
      // Serial.print("Rotation Vector - r: ");
      // Serial.print(sensorValue.un.rotationVector.real);
      // Serial.print(" i: ");
      // Serial.print(sensorValue.un.rotationVector.i);
      // Serial.print(" j: ");
      // Serial.print(sensorValue.un.rotationVector.j);
      // Serial.print(" k: ");
      // Serial.println(sensorValue.un.rotationVector.k);
      quaternionToEulerRV(&sensorValue.un.rotationVector, &ypr, true);
      Serial.print(" Yaw: ");
      Serial.print(ypr.yaw);                Serial.print("\t");
      Serial.print(" Pitch: ");
      Serial.print(ypr.pitch);              Serial.print("\t");
      Serial.print(" Roll: ");
      Serial.println(ypr.roll);


      break;
  }

}