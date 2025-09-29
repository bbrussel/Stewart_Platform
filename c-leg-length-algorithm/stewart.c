#include<stdio.h>
#include<math.h>
#include"hexapodCalculations.h"


const float r_B = 130.0;
const float r_P = 130.0;
const float actuatorHomeLength = 127.0;			// Rod length
const float baseAnchorAngleDegrees = 32.0; 		// angle from center out to leg pair in degrees
const float platformAnchorAngleDegrees = 50.0; 	// angle from center out to leg pair in degrees
const float refRotationDegrees = 0.0;    		// Base rotation about Z axis

const double gamma_B = (baseAnchorAngleDegrees*M_PI_2)/180;
const double gamma_P = (platformAnchorAngleDegrees*M_PI_2)/180;
const double ref_rotation = (refRotationDegrees*M_PI_2)/180;

struct geometry stewartPlatform;
double legLengths[6];

void initializePlatform(struct geometry *stewartPlatform){
	computePsiB(stewartPlatform->psi_B, gamma_B, ref_rotation);
	computePsiP(stewartPlatform->psi_P, gamma_P, ref_rotation);
	computeBPreTranspose(stewartPlatform->BPreTranspose, r_B, stewartPlatform->psi_B);
	transpose6by3(stewartPlatform->B, stewartPlatform->BPreTranspose);
	computePPreTranspose(stewartPlatform->PPreTranspose, r_P, stewartPlatform->psi_P);
	transpose6by3(stewartPlatform->P, stewartPlatform->PPreTranspose);
	stewartPlatform->platformHomeTransform[0] = 0.0;
	stewartPlatform->platformHomeTransform[1] = 0.0;
	stewartPlatform->platformHomeTransform[2] = sqrt(pow(actuatorHomeLength,2) - pow(stewartPlatform->P[0][0]-stewartPlatform->B[0][0], 2) - pow(stewartPlatform->P[1][0]-stewartPlatform->B[1][0], 2));
	// printPlatformGeomety(r_B, r_P, actuatorHomeLength, baseAnchorAngleDegrees, platformAnchorAngleDegrees, ref_rotation);
	// printGeometryCalculations(stewartPlatform);
}


int main() {

	initializePlatform(&stewartPlatform);
	
	struct position p;
	p.xTranslation = 0.0;
	p.yTranslation = 0.0;
	p.zTranslation = 0.0;
	p.pitchDegrees = 0.0;
	p.rollDegrees = 0.0;
	p.yawDegrees = 0.0;
	// printPositionInfo(p);
	calculateLegLengths(legLengths, p, stewartPlatform);

	p.xTranslation = 0.0;
	p.yTranslation = 2.0;
	p.zTranslation = 1.0;
	p.pitchDegrees = 2.0;
	p.rollDegrees = 5.2;
	p.yawDegrees = 0.0;
	// printPositionInfo(p);
	calculateLegLengths(legLengths, p, stewartPlatform);

	printf("\n\nExiting...\n\n");
	return 0;
}
