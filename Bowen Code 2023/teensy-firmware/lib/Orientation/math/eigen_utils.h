#ifndef EIGEN_UTILS_H
#define EIGEN_UTILS_H

#include "ArduinoEigenDense.h"

struct Orientation
{
    float yaw;
    float pitch;
    float roll;
    float xTranslation;
    float yTranslation;
    float zTranslation;
};

using namespace Eigen;

// Eigen typedefs
typedef Matrix<float, 1, 6> Array6f;
typedef Matrix<float, 1, 3> Vector3f;
typedef Matrix<float, 3, 1> TVector3f;
typedef Matrix<float, 3, 3> Matrix3x3f;
typedef Matrix<float, 3, 6> Matrix3x6f;
typedef Matrix<float, 6, 3> Matrix6x3f;

// Utility functions (that Eigen either does not provide or I have not found yet)
namespace utils
{
    Matrix3x3f rotationX(float phi);
    Matrix3x3f rotationY(float theta);
    Matrix3x3f rotationZ(float psi);
    void resizeArray1x3ToMatrix3x3(Matrix3x3f a, Eigen::Vector3f b);
    void resizeArray1x3ToMatrix3x6(Matrix3x6f a, float b[3]);
    void Matrix6x3NormRows(Matrix3x6f l, Array6f res);
};

#endif