#include "gaussian_kernel.h"

const float gaussian_k[25] = {0.024, 0.034, 0.038, 0.034, 0.024, 0.034, 0.049,
                              0.055, 0.049, 0.034, 0.038, 0.055, 0.063, 0.055,
                              0.038, 0.034, 0.049, 0.055, 0.049, 0.034, 0.024,
                              0.034, 0.038, 0.034, 0.024};

const int gaussian_w = 5;
const int gaussian_h = 5;
