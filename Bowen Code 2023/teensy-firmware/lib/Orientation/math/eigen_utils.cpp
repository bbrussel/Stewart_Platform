#include "eigen_utils.h"

Matrix3x3f utils::rotationX(float phi)
{
    Matrix3x3f res;
    res(0, 0) = 1.0;
    res(0, 1) = 0.0;
    res(0, 2) = 0.0;
    res(1, 0) = 0.0;
    res(1, 1) = cos(phi);
    res(1, 2) = -sin(phi);
    res(2, 0) = 0.0;
    res(2, 1) = sin(phi);
    res(2, 2) = cos(phi);
    return res;
}
Matrix3x3f utils::rotationY(float theta)
{
    Matrix3x3f res;
    res(0, 0) = cos(theta);
    res(0, 1) = 0.0;
    res(0, 2) = sin(theta);
    res(1, 0) = 0.0;
    res(1, 1) = 1.0;
    res(1, 2) = 0.0;
    res(2, 0) = -sin(theta);
    res(2, 1) = 0.0;
    res(2, 2) = cos(theta);
    return res;
}
Matrix3x3f utils::rotationZ(float psi)
{
    Matrix3x3f res;
    res(0, 0) = cos(psi);
    res(0, 1) = -sin(psi);
    res(0, 2) = 0.0;
    res(1, 0) = sin(psi);
    res(1, 1) = cos(psi);
    res(1, 2) = 0.0;
    res(2, 0) = 0.0;
    res(2, 1) = 0.0;
    res(2, 2) = 1.0;
    return res;
}

void utils::resizeArray1x3ToMatrix3x3(Matrix3x3f a, Eigen::Vector3f b)
{
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 3; j++)
        {
            a(i, j) = b(i);
        }
    }
}

void utils::resizeArray1x3ToMatrix3x6(Matrix3x6f a, float b[3])
{
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 6; j++)
        {
            a(i, j) = b[i];
        }
    }
}

void utils::Matrix6x3NormRows(Matrix3x6f l, Array6f res)
{
    // normalize rows of input matrix l and assign them to each value of res[0] to res[5]
    for (int i = 0; i < 6; i++)
    {
        res(0, i) = sqrt(pow(l(0, i), 2) + pow(l(1, i), 2) + pow(l(2, i), 2));
    }
}