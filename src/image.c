#include "image.h"

#include <assert.h>
#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

void apply_threshold(float *img, int w, int h, int T) {
  int area = w * h;
int idx = 0;
while (idx < area) {
    if (img[idx] > T) {
        img[idx] = 255;
    } else {
        img[idx] = 0;
    }
    idx++;
}

    

}

void scale_image(float *result, const float *img, int w, int h) {
float minVal = img[0];
float maxVal = img[0];
int idx = 1;
int totalPixels = w * h;

while (idx < totalPixels) {
    if (img[idx] < minVal) {
        minVal = img[idx];
    }
    if (img[idx] > maxVal) {
        maxVal = img[idx];
    }
    idx++;
}

if (maxVal == minVal) {
    int jdx = 0;
    while (jdx < totalPixels) {
        result[jdx] = 0.0f;
        jdx++;
    }
} else {
    int kdx = 0;
    while (kdx < totalPixels) {
        result[kdx] = ((img[kdx] - minVal) / (maxVal - minVal)) * 255;
        kdx++;
    }
}
}





   
    float get_pixel_value(const float *img, int w, int h, int x, int y) {
    switch (x < 0) {
        case 1:
            x = -x - 1;
            break;
        case 0:
            if (x >= w) {
                x = 2*w -x -1;
            }
            break;
    }

    switch (y < 0) {
        case 1:
            y = -y - 1;
            break;
        case 0:
            if (y >= h) {
                y = 2*h -y -1;
            }
            break;
    }
    
    return img[y * w + x];
}



float *array_init(int size) {
    return (float*)malloc(size * sizeof(float));
}

void array_destroy(float *m) {
    free(m);

   
}




float* read_image_from_file(const char* filename, int* w, int* h) {
    FILE *fp = fopen(filename, "r");
    if (!fp) {
        fprintf(stderr, "Error\n");
        return NULL;
    }

    char buf[3];
    if (!fgets(buf, sizeof(buf), fp)) {
        fprintf(stderr, "Error\n");
        return NULL;
    }
    if (strcmp(buf, "P2") != 0) {
        fprintf(stderr, "Error\n");
        fclose(fp);
        return NULL;
    }

    if (fscanf(fp, "%d %d", w, h) != 2 || *w <= 0 || *h <= 0) {
        fprintf(stderr, "Error\n");
        fclose(fp);
        return NULL;
    }

    int maxVal;
    if (fscanf(fp, "%d", &maxVal) != 1 || maxVal != 255) {
        fprintf(stderr, "Error\n");
        fclose(fp);
        return NULL;
    }

    float* imgData = (float*)malloc(*w * *h * sizeof(float));
    if (!imgData) {
        fprintf(stderr, "Error\n");
        fclose(fp);
        return NULL;
    }

    for (int i = 0; i < *w * *h; ++i) {
        int pix;
        if (fscanf(fp, "%d", &pix) != 1 || pix < 0 || pix > 255) {
            fprintf(stderr, "Error\n");
            free(imgData);
            fclose(fp);
            return NULL;
        }
        imgData[i] = (float)pix;
    }
    
    int extra;
    if (fscanf(fp, "%d", &extra) == 1) {
        fprintf(stderr, "Error\n");
        free(imgData);
        fclose(fp);
        return NULL;
    }

    fclose(fp);
    return imgData;
}





void write_image_to_file(const float* img, int w, int h, const char* filename) {
    FILE* abc = fopen(filename, "w");
    if (!abc) {
        fprintf(stderr, "Error");
        return;
    }

    fprintf(abc, "P2\n%d %d\n255\n", w, h);

    int i = 0;
    while (i < w * h) {
        int def = (int)img[i];
        if (i % w == 0 && i != 0) {
            fprintf(abc, "\n");
        }
        fprintf(abc, "%d ", def);
        i++;
    }

    fclose(abc);
}

