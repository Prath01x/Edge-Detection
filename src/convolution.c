#include "convolution.h"

#include <stdlib.h>

#include "image.h"

void convolve(float *result, const float *img, int w, int h, const float *M, int wM, int hM) {
    int a = wM / 2;
    int b = hM / 2;

    // Iterate over every pixel in the image
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            float sum = 0.0f;
            // Iterate over every value in the kernel
            for (int j = 0; j < hM; ++j) {
                for (int i = 0; i < wM; ++i) {
                    // Calculate the corresponding pixel in the image with mirror edge handling
                    int px = x - a + i;
                    int py = y - b + j;
                    float pixel = get_pixel_value(img, w, h, px, py);
                    float kernel_value = M[j * wM + i];
                    sum += pixel * kernel_value;
                }
            }
            // Assign the computed value to the result
            result[y * w + x] = sum;
        }
    }
}