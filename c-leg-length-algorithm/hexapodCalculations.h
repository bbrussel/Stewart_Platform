#include<stdio.h>
#include<math.h>
#include"matrixMath.h"
#include"printMatrix.h"
#include"colors.h"

struct geometry {
	double psi_B[6];
	double psi_P[6];
	double BPreTranspose[6][3];
	double B[3][6];
	double PPreTranspose[6][3];
	double P[3][6];
	double platformHomeTransform[3];
};

struct position {
	double xTranslation;
	double yTranslation;
	double zTranslation;
	double pitchDegrees;
	double rollDegrees;
	double yawDegrees;

};



void printPositionInfo(struct position p){
	cyan();
	printf("\n\nPosition Request Data:");
	reset();
	printf("\nroll: %.2f deg\n", p.rollDegrees);
	printf("pitch: %.2f deg\n", p.pitchDegrees);
	printf("yaw: %.2f deg\n", p.yawDegrees);
	printf("x: %.2f\n", p.xTranslation);
	printf("y: %.2f\n", p.yTranslation);
	printf("z: %.2f\n", p.zTranslation);
	// printf("\ntranslation:\n");
	// print1DArrayDoubles(p.translation, sizeof p.translation / sizeof p.translation[0]);
	// printf("\n\nrotation:\n");
	// print1DArrayDoubles(p.rotation, sizeof p.rotation / sizeof p.rotation[0]);
}

void printGeometryCalculations(struct geometry *stewartPlatform){
	printf("\n\n*****************************************************************");
	printf("\n\nPerforming platform initialization calculations:");
	printf("\n\n");
	printf("psi_B:\n");
	print1DArrayDoubles(stewartPlatform->psi_B, sizeof stewartPlatform->psi_B / sizeof stewartPlatform->psi_B[0]);

	printf("\n\npsi_P:\n");
	print1DArrayDoubles(stewartPlatform->psi_P, sizeof stewartPlatform->psi_P / sizeof stewartPlatform->psi_P[0]);

	printf("\n\nB:");
	print3x6Array(stewartPlatform->B);

	printf("\n\nP:");
	print3x6Array(stewartPlatform->P);

	printf("\n\nplatformHomeTransform:");
	print1DArrayDoubles(stewartPlatform->platformHomeTransform, sizeof stewartPlatform->platformHomeTransform / sizeof stewartPlatform->platformHomeTransform[0]);
	printf("\n\n*****************************************************************");
}

void printPlatformGeomety(float r_B, float r_P, float actuatorHomeLength, float baseAnchorAngleDegrees, float platformAnchorAngleDegrees, float ref_rotation){
	cyan();
	printf("\n\n*****************************************************************");
	printf("\nStewart Platform Geometry:");
	printf("\nBase Radius: %.2f", r_B);
	printf("\nPlatform Radius: %.2f", r_P);
	printf("\nActuator Home: %.2f", actuatorHomeLength);
	printf("\nBase Anchor Angle: %.2f deg", baseAnchorAngleDegrees);
	printf("\nPlatform Anchor Angle: %.2f deg", platformAnchorAngleDegrees);
	printf("\nReference Rotation: %.2f deg", ref_rotation);
	printf("\n\n*****************************************************************");
	reset();
}

void debugRotationCalculation(double rotX[3][3], double rotY[3][3], double rotZ[3][3], double rotXrotYMatMul[3][3], double R[3][3]){
	printf("\n\nrotX:");
	print3x3Array(rotX);

	printf("\n\nrotY:");
	print3x3Array(rotY);

	printf("\n\nrotZ:");
	print3x3Array(rotZ);

	printf("\n\nR:");
	print3x3Array(R);
}

void calculateRotX(double rotX[3][3], double phi){
	rotX[0][0] = 1.0;
	rotX[0][1] = 0.0;
	rotX[0][2] = 0.0;
	rotX[1][0] = 0.0;
	rotX[1][1] = cos(phi);
	rotX[1][2] = -sin(phi);
	rotX[2][0] = 0.0;
	rotX[2][1] = sin(phi);
	rotX[2][2] = cos(phi);
}

void calculateRotY(double rotY[3][3], double theta){
	rotY[0][0] = cos(theta);
	rotY[0][1] = 0.0;
	rotY[0][2] = sin(theta);
	rotY[1][0] = 0.0;
	rotY[1][1] = 1.0;
	rotY[1][2] = 0.0;
	rotY[2][0] = -sin(theta);
	rotY[2][1] = 0.0;
	rotY[2][2] = cos(theta);
}

void calculateRotZ(double rotZ[3][3], double psi){
	rotZ[0][0] = cos(psi);
	rotZ[0][1] = -sin(psi);
	rotZ[0][2] = 0.0;
	rotZ[1][0] = sin(psi);
	rotZ[1][1] = cos(psi);
	rotZ[1][2] = 0.0;
	rotZ[2][0] = 0.0;
	rotZ[2][1] = 0.0;
	rotZ[2][2] = 1.0;
}


void computePsiB(double psi_B[6], double gamma_B, double ref_rotation){
	psi_B[0] = -gamma_B + ref_rotation;
	psi_B[1] = gamma_B + ref_rotation;
	psi_B[2] = (2*M_PI/3) - gamma_B + ref_rotation;
	psi_B[3] = (2*M_PI/3) + gamma_B + ref_rotation;
	psi_B[4] = (4*M_PI/3) - gamma_B + ref_rotation;
	psi_B[5] = (4*M_PI/3) + gamma_B + ref_rotation;
}

void computePsiP(double psi_P[6], double gamma_P, double ref_rotation){
	psi_P[0] = (M_PI/3) + 4*(M_PI/3) + gamma_P + ref_rotation;
	psi_P[1] = (M_PI/3) - gamma_P + ref_rotation;
	psi_P[2] = (M_PI/3) + gamma_P + ref_rotation;
	psi_P[3] = M_PI - gamma_P + ref_rotation;
	psi_P[4] = M_PI + gamma_P + ref_rotation;
	psi_P[5] = M_PI + (2*M_PI/3) - gamma_P + ref_rotation;
}

void computeBPreTranspose(double BPreTranspose[6][3],double r_B,double psi_B[6]){
	BPreTranspose[0][0] = r_B*cos(psi_B[0]);
	BPreTranspose[0][1] = r_B*sin(psi_B[0]);
	BPreTranspose[0][2] = 0.0;
	BPreTranspose[1][0] = r_B*cos(psi_B[1]);
	BPreTranspose[1][1] = r_B*sin(psi_B[1]);
	BPreTranspose[1][2] = 0.0;
	BPreTranspose[2][0] = r_B*cos(psi_B[2]);
	BPreTranspose[2][1] = r_B*sin(psi_B[2]);
	BPreTranspose[2][2] = 0.0;
	BPreTranspose[3][0] = r_B*cos(psi_B[3]);
	BPreTranspose[3][1] = r_B*sin(psi_B[3]);
	BPreTranspose[3][2] = 0.0;
	BPreTranspose[4][0] = r_B*cos(psi_B[4]);
	BPreTranspose[4][1] = r_B*sin(psi_B[4]);
	BPreTranspose[4][2] = 0.0;
	BPreTranspose[5][0] = r_B*cos(psi_B[5]);
	BPreTranspose[5][1] = r_B*sin(psi_B[5]);
	BPreTranspose[5][2] = 0.0;
}

void computePPreTranspose(double PPreTranspose[6][3],double r_P,double psi_P[6]){
	PPreTranspose[0][0] = r_P*cos(psi_P[0]);
	PPreTranspose[0][1] = r_P*sin(psi_P[0]);
	PPreTranspose[0][2] = 0.0;
	PPreTranspose[1][0] = r_P*cos(psi_P[1]);
	PPreTranspose[1][1] = r_P*sin(psi_P[1]);
	PPreTranspose[1][2] = 0.0;
	PPreTranspose[2][0] = r_P*cos(psi_P[2]);
	PPreTranspose[2][1] = r_P*sin(psi_P[2]);
	PPreTranspose[2][2] = 0.0;
	PPreTranspose[3][0] = r_P*cos(psi_P[3]);
	PPreTranspose[3][1] = r_P*sin(psi_P[3]);
	PPreTranspose[3][2] = 0.0;
	PPreTranspose[4][0] = r_P*cos(psi_P[4]);
	PPreTranspose[4][1] = r_P*sin(psi_P[4]);
	PPreTranspose[4][2] = 0.0;
	PPreTranspose[5][0] = r_P*cos(psi_P[5]);
	PPreTranspose[5][1] = r_P*sin(psi_P[5]);
	PPreTranspose[5][2] = 0.0;
}


void calculateContributions(double translationContribution[3][6], double homePositionContribution[3][6], double rotationContribution[3][6], double translationTransform[3], double rotationTransform[3], struct geometry stewartPlatform){
	double rotX[3][3];
	double rotY[3][3];
	double rotZ[3][3];
	double rotZrotYMatMul[3][3];
	double R[3][3];
	calculateRotX(rotX, rotationTransform[0]);
	calculateRotY(rotY, rotationTransform[1]);
	calculateRotZ(rotZ, rotationTransform[2]);

	matMult3by3(rotZ, rotY, rotZrotYMatMul);
	matMult3by3(rotZrotYMatMul, rotX, R);
	extendMatrix(translationContribution, translationTransform);
	extendMatrix(homePositionContribution, stewartPlatform.platformHomeTransform);
	matMult3by3And3by6(R, stewartPlatform.P, rotationContribution);


	// debugRotationCalculation(rotX, rotY, rotZ, rotXrotYMatMul, R);
	// printf("\n\ntranslationContribution:");
	// print3x6Array(translationContribution);
	// printf("\n\nhomePositionContribution:");
	// print3x6Array(homePositionContribution);
	// printf("\n\nrotationContribution:");
	// print3x6Array(rotationContribution);

}

void calculateLegLengths(double *legLengths, struct position p, struct geometry stewartPlatform){

	double pitchRadians;
	double yawRadians;
	double rollRadians;

	double translation[3];
	double rotation[3];
	double translationContribution[3][6];
	double homePositionContribution[3][6];
	double rotationContribution[3][6];
	double legTranslations[3][6];

	translation[0] = p.xTranslation;
	translation[1] = p.yTranslation;
	translation[2] = p.zTranslation;
	pitchRadians = p.pitchDegrees*M_PI/180.0;

	yawRadians = p.yawDegrees*M_PI/180.0;
	rollRadians = p.rollDegrees*M_PI/180.0;
	rotation[0] = pitchRadians;
	rotation[1] = yawRadians;
	rotation[2] = rollRadians;

	calculateContributions(translationContribution, homePositionContribution, rotationContribution, translation, rotation, stewartPlatform);

	calculateLegTranslations(legTranslations, translationContribution, homePositionContribution, rotationContribution, stewartPlatform.B);

	calculateLegVectorNorms(legLengths, legTranslations);

	printf("\nlegLengths:");
	print1DArrayDoubles(legLengths, 6);


}