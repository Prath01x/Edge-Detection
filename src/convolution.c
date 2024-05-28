#include "convolution.h"

#include <stdlib.h>

#include "image.h"

void convolve(float *result, const float *img, int w, int h, const float *M, int wM, int hM) {
    int a = wM / 2;
    int b = hM / 2;

    int y = 0;
    while (y < h) {
        int x = 0;
        while (x < w) {
            float sum = 0.0f;
            
            int c = 0;
            while (c < hM) {
                int d = 0;
                while (d < wM) {
                    
                    int px = x - a + d;
                    int py = y - b + c;
                    float pixel = get_pixel_value(img, w, h, px, py);
                    float kernel_value = M[c * wM + d];
                    sum += pixel * kernel_value;
                    d++;
                }
                c++;
            }
            
            result[y * w + x] = sum;
            x++;
        }
        y++;
    }
}
