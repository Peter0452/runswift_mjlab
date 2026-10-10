#pragma once

#include <cmath>
#include <vector>
#include <string>
#include <stdexcept>
#include "./print.h"

using namespace std;

// 角度转弧度
inline double deg2rad(double deg)
{
    return deg / 180.0 * M_PI;
}

// 弧度转角度
inline double rad2deg(double rad)
{
    return rad / M_PI * 180.0;
}

// 算术平均值
inline double mean(double x, double y)
{
    return (x + y) / 2;
}

// 把数字截断到一个范围内
inline double cap(double x, double upper_limit, double lower_limit)
{
    return max(min(x, upper_limit), lower_limit);
}

// 计算L2范数 (两个数的平方和开根号)
inline double norm(double x, double y)
{
    return sqrt(x * x + y * y);
}

// 计算L2范数 (两个数的平方和开根号)
inline double norm(vector<double> v)
{
    return sqrt(v[0] * v[0] + v[1] * v[1]);
}

// 把一个角度换算到 [-M_PI, M_PI) 区间.
inline double toPInPI(double theta)
{
    int n = static_cast<int>(fabs(theta / 2 / M_PI)) + 1;
    return fmod(theta + M_PI + 2 * n * M_PI, 2 * M_PI) - M_PI;
}

