#include "stewart_platform.h"

StewartPlatform::StewartPlatform()
{
    geometry.stroke = (geometry.actuatorFullLength - geometry.actuatorClosedLength);
    geometry.actuatorHomeLength = geometry.actuatorClosedLength + (geometry.stroke / 2);

    geometry.warningMinLength = geometry.actuatorClosedLength + (geometry.stroke * geometry.actuatorStrokeWarningMargin);
    geometry.warningMaxLength = geometry.actuatorFullLength - (geometry.stroke * geometry.actuatorStrokeWarningMargin);
    geometry.faultMinLength = geometry.actuatorClosedLength + (geometry.stroke * geometry.actuatorStrokeFaultMargin);
    geometry.faultMaxLength = geometry.actuatorFullLength - (geometry.stroke * geometry.actuatorStrokeFaultMargin);

    platformOrientation = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    baseOrientation = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
}

void StewartPlatform::initGeometry()
{
    calculatePsiB();
    calculatePsiP(); // calculate positions of base and platform anchors on unit circle
}

void StewartPlatform::initPlatformBaseTransform()
{
    calculateBaseAnchorHomeCoords();  // calculate cartesian coordinates of base anchors in home position
    calculatePlatformAnchorCoords();  // calculate cartesian coordinates of platform anchors
    calculatePlatformHomeTransform(); // calculate platform home position
}

float StewartPlatform::calculateAzimuth(float x, float y)
{
    if (y == 0)
    {
        if (x > 0)
        {
            pointingVector.azimuthAngle = 0;
        }
        else
        {
            pointingVector.azimuthAngle = 180;
        }
    }
    if (x == 0)
    {
        if (y > 0)
        {
            pointingVector.azimuthAngle = 270;
        }
        else
        {
            pointingVector.azimuthAngle = 90;
        }
    }
    if (x >= 0 && y  >= 0)
    {
        pointingVector.azimuthAngle = 360 - (atan(y / x) * 180 / M_PI);
    }
    if (x >= 0 && y <= 0)
    {
        pointingVector.azimuthAngle = (-atan(y / x) * 180 / M_PI);
    }
    if (x <= 0 && y <= 0)
    {
        pointingVector.azimuthAngle = 180 - (atan(y / x) * 180 / M_PI);
    }
    if (x <= 0 && y>= 0)
    {
        pointingVector.azimuthAngle = 180 - (atan(y / x) * 180 / M_PI);
    }
    return pointingVector.azimuthAngle;
}

float StewartPlatform::calculateElevation(float x, float y, float z)
{
    float xyProjection = sqrtf(pow(x, 2) + pow(y, 2));

    if (xyProjection > 0)
    {
        pointingVector.elevationAngle = atan(z / xyProjection) * 180 / M_PI;
    }
    else
    {
        pointingVector.elevationAngle = 0;
    }
    return pointingVector.elevationAngle;
}

void StewartPlatform::calculatePointingVector()
{
    pointingVector.tip << 
        0,
        0, 
        0;

    pointingVector.home <<
        0, 
        0, 
        40; // python sim hardcoded length

    platformTranslationVector << 
        platformOrientation.xTranslation, 
        platformOrientation.yTranslation, 
        platformOrientation.zTranslation;;

    platformRotationVector <<
        platformOrientation.pitch * M_PI / 180,
        platformOrientation.yaw * M_PI / 180,
        platformOrientation.roll * M_PI / 180;

    Matrix3x3f platformRotationMatrix = utils::rotationZ(platformRotationVector(2)) * utils::rotationY(platformRotationVector(1)) * utils::rotationX(platformRotationVector(0));

    Eigen::Vector3f pointingVectorHomeRotation = pointingVector.home.transpose() * platformRotationMatrix;
    Eigen::Vector3f pointingVectorTipRotation = pointingVector.tip.transpose() * platformRotationMatrix;

    pointingVector.home = platformTranslationVector + pointingVectorHomeRotation + platformHomeTransform;
    pointingVector.tip = platformTranslationVector + pointingVectorTipRotation + platformHomeTransform; 
    
    pointingVector.dX = pointingVector.tip(0) - pointingVector.home(0);
    pointingVector.dY = pointingVector.tip(1) - pointingVector.home(1);
    pointingVector.dZ = pointingVector.tip(2) - pointingVector.home(2);

    pointingVector.azimuthAngle = calculateAzimuth(pointingVector.dX, pointingVector.dY);
    pointingVector.elevationAngle = calculateElevation(pointingVector.dX, pointingVector.dY, pointingVector.dZ);
}


void StewartPlatform::calculatePsiB()
{
    float refRotationRadians = .5 * geometry.refRotationDegrees * M_PI / 180;
    float gammaB = .5 * geometry.baseAnchorAngleDegrees * M_PI / 180;
    psiB[0] = -gammaB + refRotationRadians;
    psiB[1] = gammaB + refRotationRadians;
    psiB[2] = (2 * M_PI / 3) - gammaB + refRotationRadians;
    psiB[3] = (2 * M_PI / 3) + gammaB + refRotationRadians;
    psiB[4] = (4 * M_PI / 3) - gammaB + refRotationRadians;
    psiB[5] = (4 * M_PI / 3) + gammaB + refRotationRadians;
}

void StewartPlatform::calculatePsiP()
{
    float refRotationRadians = .5 * geometry.refRotationDegrees * M_PI / 180;
    float gammaP = .5 * geometry.platformAnchorAngleDegrees * M_PI / 180;
    psiP[0] = (M_PI / 3) + (4 * M_PI / 3) + gammaP + refRotationRadians;
    psiP[1] = (M_PI / 3) - gammaP + refRotationRadians;
    psiP[2] = (M_PI / 3) + gammaP + refRotationRadians;
    psiP[3] = (M_PI / 3) + (2 * M_PI / 3) - gammaP + refRotationRadians;
    psiP[4] = (M_PI / 3) + (2 * M_PI / 3) + gammaP + refRotationRadians;
    psiP[5] = (M_PI / 3) + (4 * M_PI / 3) - gammaP + refRotationRadians;
}

void StewartPlatform::calculateBaseAnchorHomeCoords()
{
    float r = geometry.baseRadius;
    Matrix6x3f temp;
    temp << r * cos(psiB[0]), r * sin(psiB[0]), 0,
        r * cos(psiB[1]), r * sin(psiB[1]), 0,
        r * cos(psiB[2]), r * sin(psiB[2]), 0,
        r * cos(psiB[3]), r * sin(psiB[3]), 0,
        r * cos(psiB[4]), r * sin(psiB[4]), 0,
        r * cos(psiB[5]), r * sin(psiB[5]), 0;
    baseAnchorPositions = temp.transpose();
}

void StewartPlatform::calculatePlatformAnchorCoords()
{
    float r = geometry.platformRadius;
    Matrix6x3f temp;
    temp << r * cos(psiP[0]), r * sin(psiP[0]), 0,
        r * cos(psiP[1]), r * sin(psiP[1]), 0,
        r * cos(psiP[2]), r * sin(psiP[2]), 0,
        r * cos(psiP[3]), r * sin(psiP[3]), 0,
        r * cos(psiP[4]), r * sin(psiP[4]), 0,
        r * cos(psiP[5]), r * sin(psiP[5]), 0;
    platformAnchorPositions = temp.transpose();
}

void StewartPlatform::calculatePlatformHomeTransform() // distance formula
{
    platformHomeTransform(0) = 0.0;
    platformHomeTransform(1) = 0.0;
    platformHomeTransform(2) = sqrtf(pow(geometry.actuatorHomeLength, 2) - pow((platformAnchorPositions(0, 0) - baseAnchorPositions(0, 0)), 2) - pow((platformAnchorPositions(1, 0) - baseAnchorPositions(1, 0)), 2));
}

void StewartPlatform::calculateLegLengthsAndBase()
{
    // Assign base / platform rotation and translation vectors
    platformTranslationVector <<
        platformOrientation.xTranslation,
        platformOrientation.yTranslation,
        platformOrientation.zTranslation;

    platformRotationVector << // convert desired platform / base orientation to radians
        platformOrientation.roll * M_PI / 180,
        platformOrientation.pitch * M_PI / 180,
        platformOrientation.yaw * M_PI / 180;
        
    baseRotationVector <<
        baseOrientation.roll * M_PI / 180,
        baseOrientation.pitch * M_PI / 180,
        baseOrientation.yaw * M_PI / 180;

    // Rotate Base Anchor Coordinates
    TVector3f baseRotation = baseRotationVector.transpose(); // column to row vector
    baseRotationMatrix = utils::rotationX(baseRotation(0)) * utils::rotationY(baseRotation(1)) * utils::rotationZ(baseRotation(2));
    baseAnchorPositions = baseRotationMatrix * baseAnchorPositions; // Apply to base anchor coords

    // Rotate Platform Anchor Coordinates
    TVector3f platRotation = platformRotationVector.transpose();
    platformRotationMatrix = utils::rotationX(platRotation(0)) * utils::rotationY(platRotation(1)) * utils::rotationZ(platRotation(2));

    // Transpose Platform Anchor Coordinates
    Matrix3x6f platformTranslationContribution = platformTranslationVector.replicate(1, 6); // may be a problem in the future not exactly the same as np.repeat
    Matrix3x6f platformHomePositionContribution = platformHomeTransform.replicate(1, 6);
    Matrix3x6f platformRotationContribution = platformRotationMatrix * platformAnchorPositions;

    legPositions = platformTranslationContribution + platformHomePositionContribution + platformRotationContribution - baseAnchorPositions;
    legLengths = legPositions.colwise().norm();
    legPositions = legPositions + baseAnchorPositions;
}

void StewartPlatform::calculateStepPositions(int stepNumber, Orientation initialOri, Orientation finalOri)
{
    
}