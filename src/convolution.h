#ifndef CONVOLUTION_H
#define CONVOLUTION_H

/**
 * Returns the convolution of the given image and matrix. To bypass the
 * uncovered parts of the matrix the image is mirrored at its boundaries
 * (Exercise 4).
 *
 * result: result of the convolution
 *
 * img: input image
 * w: width of the image
 * h: height of the image
 *
 * matrix: convolution matrix
 * w_m: width of the matrix
 * h_m: height of the matrix
 */
void convolve(float *result, const float *img, int w, int h,
              const float *matrix, int w_m, int h_m);

#endif
