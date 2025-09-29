
void calculatePsiB(float psiB[], float baseAnchorAngleDegrees, float refRotationDegrees) {
  // Serial.println("");
  // Serial.println("Calculating psiB");
  float refRotationRadians = .5*refRotationDegrees*M_PI/180;
  float gammaB = .5*baseAnchorAngleDegrees*M_PI/180;
  psiB[0] = -gammaB + refRotationRadians;
  psiB[1] = gammaB + refRotationRadians;
  psiB[2] = (2*M_PI/3)-gammaB + refRotationRadians;
  psiB[3] = (2*M_PI/3)+gammaB + refRotationRadians;
  psiB[4] = (4*M_PI/3)-gammaB + refRotationRadians;
  psiB[5] = (4*M_PI/3)+gammaB + refRotationRadians;
}

void calculatePsiP(float psiP[], float platformAnchorAngleDegrees, float refRotationDegrees) {
  // Serial.println("");
  // Serial.println("Calculating psiP");
  float refRotationRadians = .5*refRotationDegrees*M_PI/180;
  float gammaP = .5*platformAnchorAngleDegrees*M_PI/180;
  psiP[0] = (M_PI/3) + (4*M_PI/3) + gammaP + refRotationRadians;
  psiP[1] = (M_PI/3) - gammaP + refRotationRadians;
  psiP[2] = (M_PI/3) + gammaP + refRotationRadians;
  psiP[3] = (M_PI/3) + (2*M_PI/3) - gammaP + refRotationRadians;
  psiP[4] = (M_PI/3) + (2*M_PI/3) + gammaP + refRotationRadians;
  psiP[5] = (M_PI/3) + (4*M_PI/3) - gammaP + refRotationRadians;
}

void calculateBaseAnchorHomeCoords(float baseAnchorCoords[][3], float psiB[], float baseRadius){
  baseAnchorCoords[0][0] = baseRadius*cos(psiB[0]);
  baseAnchorCoords[0][1] = baseRadius*sin(psiB[0]);
  baseAnchorCoords[0][2] = 0;
  baseAnchorCoords[1][0] = baseRadius*cos(psiB[1]);
  baseAnchorCoords[1][1] = baseRadius*sin(psiB[1]);
  baseAnchorCoords[1][2] = 0;
  baseAnchorCoords[2][0] = baseRadius*cos(psiB[2]);
  baseAnchorCoords[2][1] = baseRadius*sin(psiB[2]);
  baseAnchorCoords[2][2] = 0;
  baseAnchorCoords[3][0] = baseRadius*cos(psiB[3]);
  baseAnchorCoords[3][1] = baseRadius*sin(psiB[3]);
  baseAnchorCoords[3][2] = 0;
  baseAnchorCoords[4][0] = baseRadius*cos(psiB[4]);
  baseAnchorCoords[4][1] = baseRadius*sin(psiB[4]);
  baseAnchorCoords[4][2] = 0;
  baseAnchorCoords[5][0] = baseRadius*cos(psiB[5]);
  baseAnchorCoords[5][1] = baseRadius*sin(psiB[5]);
  baseAnchorCoords[5][2] = 0;
}

void calculatePlatformAnchorCoords(float platformAnchorCoords[][3], float psiP[], float platformRadius){
  platformAnchorCoords[0][0] = platformRadius*cos(psiP[0]);
  platformAnchorCoords[0][1] = platformRadius*sin(psiP[0]);
  platformAnchorCoords[0][2] = 0;
  platformAnchorCoords[1][0] = platformRadius*cos(psiP[1]);
  platformAnchorCoords[1][1] = platformRadius*sin(psiP[1]);
  platformAnchorCoords[1][2] = 0;
  platformAnchorCoords[2][0] = platformRadius*cos(psiP[2]);
  platformAnchorCoords[2][1] = platformRadius*sin(psiP[2]);
  platformAnchorCoords[2][2] = 0;
  platformAnchorCoords[3][0] = platformRadius*cos(psiP[3]);
  platformAnchorCoords[3][1] = platformRadius*sin(psiP[3]);
  platformAnchorCoords[3][2] = 0;
  platformAnchorCoords[4][0] = platformRadius*cos(psiP[4]);
  platformAnchorCoords[4][1] = platformRadius*sin(psiP[4]);
  platformAnchorCoords[4][2] = 0;
  platformAnchorCoords[5][0] = platformRadius*cos(psiP[5]);
  platformAnchorCoords[5][1] = platformRadius*sin(psiP[5]);
  platformAnchorCoords[5][2] = 0;
}

void calculatePlatformHomeTransform(float platformHomeTransform[], float baseAnchorCoords[][3], float platformAnchorCoords[][3], float actuatorHomeLength){
  platformHomeTransform[0] = 0.0;
  platformHomeTransform[1] = 0.0;
  platformHomeTransform[2] = sqrt(sq(actuatorHomeLength) - sq(platformAnchorCoords[0][0] - baseAnchorCoords[0][0]) - sq(platformAnchorCoords[0][1] - baseAnchorCoords[0][1]));
}

void rotX(float array[][3], float phi){
  array[0][0] = 1.0;
  array[0][1] = 0.0;
  array[0][2] = 0.0;
  array[1][0] = 0.0;
  array[1][1] = cos(phi);
  array[1][2] = -sin(phi);
  array[2][0] = 0.0;
  array[2][1] = sin(phi);
  array[2][2] = cos(phi);
}

void rotY(float array[][3], float theta){
  array[0][0] = cos(theta);
  array[0][1] = 0.0;
  array[0][2] = sin(theta);
  array[1][0] = 0.0;
  array[1][1] = 1.0;
  array[1][2] = 0.0;
  array[2][0] = -sin(theta);
  array[2][1] = 0.0;
  array[2][2] = cos(theta);
}

void rotZ(float array[][3], float psi){
  array[0][0] = cos(psi);
  array[0][1] = -sin(psi);
  array[0][2] = 0.0;
  array[1][0] = sin(psi);
  array[1][1] = cos(psi);
  array[1][2] = 0.0;
  array[2][0] = 0.0;
  array[2][1] = 0.0;
  array[2][2] = 1.0;
}


void calculateL(float a[3][6], float b[3][6], float c[3][6], float d[3][6], float result[3][6]) {
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 6; j++) {
      result[i][j] = a[i][j] + b[i][j] + c[i][j] - d[i][j];
    }
  }
}

void calculateLegLengthsAndBase(float legLengths[6], float baseAnchorHomeCoords[6][3], float platformAnchorCoords[6][3], float platformHomeTransform[3], Orientation baseOrientation, Orientation platformOrientation){
  double platformTranslationVector[] = {platformOrientation.xTranslation, platformOrientation.yTranslation, platformOrientation.zTranslation};
  double platformRotationVector[] = {platformOrientation.roll*M_PI/180, platformOrientation.pitch*M_PI/180, platformOrientation.yaw*M_PI/180};
  double baseRotationVector[] = {baseOrientation.roll*M_PI/180, baseOrientation.pitch*M_PI/180, baseOrientation.yaw*M_PI/180};

  float baseRotationX[3][3];
  float baseRotationY[3][3];
  float baseRotationZ[3][3];
  float baseRotationMatrix[3][3];
  float transformedBase[3][6];
  
  rotX(baseRotationX, baseRotationVector[0]);
  rotY(baseRotationY, baseRotationVector[1]);
  rotZ(baseRotationZ, baseRotationVector[2]);

  float tempResult[3][3];
  matrixMultiply3x3(baseRotationZ, baseRotationY, tempResult);
  matrixMultiply3x3(tempResult, baseRotationX, baseRotationMatrix);

  float transposedBaseHomeCoords[3][6];
  transposeMatrix6x3(baseAnchorHomeCoords, transposedBaseHomeCoords);
  matrixMultiply3x3_3x6(baseRotationMatrix, transposedBaseHomeCoords, transformedBase);

  float platformRotationX[3][3];
  float platformRotationY[3][3];
  float platformRotationZ[3][3];
  float platformRotationMatrix[3][3];
  // float transformedPlatform[3][6];
  rotX(platformRotationX, platformRotationVector[0]);
  rotY(platformRotationY, platformRotationVector[1]);
  rotZ(platformRotationZ, platformRotationVector[2]);

  matrixMultiply3x3(platformRotationZ, platformRotationY, tempResult);
  matrixMultiply3x3(tempResult, platformRotationX, platformRotationMatrix);

  float platformTranslationContribution[3][6];
  for (int j = 0; j < 6; j++) {
    platformTranslationContribution[0][j] = platformTranslationVector[0];
  }
  for (int j = 0; j < 6; j++) {
    platformTranslationContribution[1][j] = platformTranslationVector[1];
  }
  for (int j = 0; j < 6; j++) {
    platformTranslationContribution[2][j] = platformTranslationVector[2];
  }

  float platformHomeContribution[3][6];
  for (int j = 0; j < 6; j++) {
    platformHomeContribution[0][j] = platformHomeTransform[0];
  }
  for (int j = 0; j < 6; j++) {
    platformHomeContribution[1][j] = platformHomeTransform[1];
  }
  for (int j = 0; j < 6; j++) {
    platformHomeContribution[2][j] = platformHomeTransform[2];
  }

  float platformRotationContribution[3][6];

  float transposedPlatformCoords[3][6];
  transposeMatrix6x3(platformAnchorCoords, transposedPlatformCoords);
  matrixMultiply3x3_3x6(platformRotationMatrix, transposedPlatformCoords, platformRotationContribution);

  float l[3][6];

  calculateL(platformTranslationContribution, platformHomeContribution, platformRotationContribution, transformedBase, l);

  legLengths[0] = sqrt(sq(l[0][0]) + sq(l[1][0]) + sq(l[2][0]));
  legLengths[1] = sqrt(sq(l[0][1]) + sq(l[1][1]) + sq(l[2][1]));
  legLengths[2] = sqrt(sq(l[0][2]) + sq(l[1][2]) + sq(l[2][2]));
  legLengths[3] = sqrt(sq(l[0][3]) + sq(l[1][3]) + sq(l[2][3]));
  legLengths[4] = sqrt(sq(l[0][4]) + sq(l[1][4]) + sq(l[2][4]));
  legLengths[5] = sqrt(sq(l[0][5]) + sq(l[1][5]) + sq(l[2][5]));
  
  // printArray(legLengths, 6);

}





