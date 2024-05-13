#ifndef DERIVATION_H
#define DERIVATION_H

/**
 * Computes the gradient magnitude of the discrete derivation in x and
 * y direction (Exercise 2).
 *
 * result: resulting gradient magnitude
 *
 * d_x: discrete derivation in x direction
 * d_y: discrete derivation in y direction
 * w: width of result, d_x and d_y
 * h: height of result, d_y and d_y
 */
void gradient_magnitude(float *result, const float *d_x, const float *d_y,
                        int w, int h);

/**
 * Computes the discrete derivation of 'img' in x direction and stores the
 * result in 'result'.
 */
void derivation_x_direction(float *result, const float *img, int w, int h);

/**
 * Computes the discrete derivation of 'img' in y direction and stores the
 * result in 'result'.
 */
void derivation_y_direction(float *result, const float *img, int w, int h);

#endif
