#ifndef IMAGE_H
#define IMAGE_H

/**
 * Assigns all pixels with a value larger than the threshold T the value of 255
 * and less or equal to T a value of 0 (Exercise 1).
 *
 * There is no new image created. Instead the pixel values in the given image
 * are adapted.
 */
void apply_threshold(float *img, int w, int h, int T);

/**
 * Rescales the pixel values such that they range from 0 to 255 (Exercise 3).
 * If all pixels have the same value a complete black image should be returned.
 */
void scale_image(float *result, const float *img, int w, int h);

/**
 * Returns the gray value of the image at position (x,y). If the position is
 * outside the image the value of the pixel mirrored at the image border is
 * returned (Exercise 4).
 *
 * w: width of the image
 * h: height of the image
 * x: x coordinate of the pixel
 * y: y coordinate of the pixel
 */
float get_pixel_value(const float *img, int w, int h, int x, int y);

/**
 * Initializes an one dimensional float array of the given size (Exercise 5+6).
 */
float *array_init(int size);

/**
 * Frees the given dynamically allocated memory (Exercise 5+6).
 */
void array_destroy(float *m);

/**
 * Reads an image from a portable graymap (.pgm) file (Exercise 5).
 *
 * Memory allocation is dealt with inside the function.
 * You are responsible to call array_destroy on the result.
 * w and h should be used to access the width and height of the image in the
 * scope calling this function.
 */
float *read_image_from_file(const char *filename, int *w, int *h);

/**
 * Writes an image to a portable graymap (.pgm) file (Exercise 5).
 *
 * Hint: Each pixel value is rounded down to an integer value before it is
 * written.
 */
void write_image_to_file(const float *img, int w, int h, const char *filename);

#endif
