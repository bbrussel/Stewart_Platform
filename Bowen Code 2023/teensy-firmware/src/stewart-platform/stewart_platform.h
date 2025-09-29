#ifndef STEWART_PLATFORM_H
#define STEWARTJ_PLATFORM_H

#include "orientation_math.h"
#include "math/eigen_utils.h"

enum SimState
{
    INIT,               // Initializing Platform, Actuators, Sensors
    UPDATE,
    SENDING_DATA,
    PARSING_SERIAL,
    SENDING_ACTUATORS
};

class StewartPlatform
{
public:
    StewartPlatform();
    StewartPlatform(Orientation platOri, Orientation baseOri)
    {
        platformOrientation = platOri;
        baseOrientation = baseOri;

        thisLoopMicros = 0; // microsecond timestamp for current loop
        lastOriUpdate = 0; // microsecond timestamp for last ori update
    }

    // ===== GEOMETRY INFO ===== //
    struct Geometry
    {
        const float baseRadius;
        const float platformRadius;
        const float actuatorClosedLength;
        const float actuatorFullLength; // make sure the initial geometry is not somehow modified

        float baseAnchorAngleDegrees;
        float platformAnchorAngleDegrees;
        float refRotationDegrees;

        float actuatorStrokeFaultMargin;
        float actuatorStrokeWarningMargin;
        float warningMinLength;
        float warningMaxLength;
        float faultMinLength;
        float faultMaxLength;

        float actuatorHomeLength;
        float stroke;
    };
    Geometry geometry = {225.0, // base radius
                         225.0, // platform radius
                         160.0, // actuator closed length
                         260.0, // actuator full length
                         45.0,  // base anchor angle (deg)
                         22.0,  // platform anchor angle (deg)
                         0.0,   // ref rotation (deg)
                         0.03,  // actuator stroke fault margin
                         0.1};  // actuator stroke warning margin

    // ========================= //

    uint64_t thisLoopMicros;
    uint64_t lastOriUpdate;
    IMUOrientation measuredOrientation;

    struct PointingVector
    {
        float azimuthAngle;
        float elevationAngle;

        float dX;
        float dY;
        float dZ;

        Eigen::Vector3f tip;
        Eigen::Vector3f home;
    };
    PointingVector pointingVector;

    Matrix3x6f platformAnchorPositions;
    Matrix3x6f baseAnchorPositions;

    Orientation platformOrientation; // what are these mystery values?
    Orientation baseOrientation;

    Array6f legLengths;
    Matrix3x6f legPositions;

    void initGeometry();
    void initPlatformBaseTransform();

    void calculatePointingVector();
    void calculateLegLengthsAndBase();

    void calculateStepPositions(int stepNumber, Orientation initialOri, Orientation finalOri);

private:
    float platformHomeHeight[6];
    Eigen::Vector3f platformHomeTransform;
    float psiB[6];
    float psiP[6];

    Matrix3x3f platformRotationMatrix;
    Eigen::Vector3f platformRotationVector;
    Eigen::Vector3f platformTranslationVector;
    Matrix3x3f baseRotationMatrix;
    Eigen::Vector3f baseRotationVector;
    Eigen::Vector3f baseTranslationVector;

    float calculateAzimuth(float x, float y);
    float calculateElevation(float x, float y, float z);

    void calculatePsiB();
    void calculatePsiP();
    void calculateBaseAnchorHomeCoords();
    void calculatePlatformAnchorCoords();
    void calculatePlatformHomeTransform();
};

#endif