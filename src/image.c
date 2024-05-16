#include "image.h"

#include <assert.h>
#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void apply_threshold(float *img, int w, int h, int T) {
   int size= w*h;
   for (int x=0;x<size;x++){
    if(img[x]>T){
        img[x]= 255;
    } else
    {
        img[x]=0;
    }
    
    

   }
    

}

void scale_image(float *result, const float *img, int w, int h) {
    float minimum=img[0];float maximum=img[0];
    for (int i = 1; i < w * h; ++i) {
        if (img[i] < minimum) {
            minimum = img[i];
        }
        if (img[i] > maximum) {
            maximum = img[i];
        }
    }
    if(maximum==minimum){
        for(int i=0;i<w*h;i++){
            result[i]= 0.0f; 
        }
    }
    else{for(int i =0;i<h*w; i++) {
        result[i]= ((img[i]-minimum)/(maximum-minimum))*255;
    }

    }
    
    
}




float get_pixel_value(const float *img, int w, int h, int x, int y) {
   
    if (x < 0) {
        x = -x - 1;
    } else if (x >= w) {
        x = 2 * w - x - 1;
    }

    
    if (y < 0) {
        y = -y - 1;
    } else if (y >= h) {
        y = 2 * h - y - 1;
    }
    return img[y * w + x];
}


float *array_init(int size) {
    return (float*)malloc(size * sizeof(float));
}

void array_destroy(float *m) {
    free(m);

   
}


// Function to read an image from a PGM file
float* read_image_from_file(const char* filename, int* w, int* h) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "Error: File %s does not exist.\n", filename);
        return NULL;
    }

    // Read the header
    char magic_number[3];
    if (!fgets(magic_number, sizeof(magic_number), file)) {
        fprintf(stderr, "Error: Invalid PGM file.\n");
        fclose(file);
        return NULL;
    }

    if (strcmp(magic_number, "P2") != 0) {
        fprintf(stderr, "Error: Unsupported PGM format. Only P2 format is supported.\n");
        fclose(file);
        return NULL;
    }

    // Skip comments
    char ch;
    while ((ch = fgetc(file)) == '#') {
        while (fgetc(file) != '\n');
    }
    ungetc(ch, file);

    // Read image dimensions
    if (fscanf(file, "%d %d", w, h) != 2 || *w <= 0 || *h <= 0) {
        fprintf(stderr, "Error: Invalid image dimensions.\n");
        fclose(file);
        return NULL;
    }

    // Read maximum gray value
    int max_gray_value;
    if (fscanf(file, "%d", &max_gray_value) != 1 || max_gray_value != 255) {
        fprintf(stderr, "Error: Invalid maximum gray value. Must be 255.\n");
        fclose(file);
        return NULL;
    }

    // Allocate memory for image data
    float* img = array_init(*w * *h);
    if (!img) {
        fprintf(stderr, "Error: Memory allocation failed.\n");
        fclose(file);
        return NULL;
    }

    // Read pixel data
    for (int i = 0; i < *w * *h; ++i) {
        int pixel_value;
        if (fscanf(file, "%d", &pixel_value) != 1 || pixel_value < 0 || pixel_value > 255) {
            fprintf(stderr, "Error: Invalid pixel value at position %d.\n", i);
            array_destroy(img);
            fclose(file);
            return NULL;
        }
        img[i] = (float)pixel_value;
    }

    fclose(file);
    return img;
}



void write_image_to_file(const float* img, int w, int h, const char* filename) {
    FILE* file = fopen(filename, "w");
    if (!file) {
        fprintf(stderr, "Error: Cannot open file %s for writing.\n", filename);
        return;
    }

    // Write the header
    fprintf(file, "P2\n%d %d\n255\n", w, h);

    // Write the pixel data
    for (int i = 0; i < w * h; ++i) {
        int pixel_value = (int)img[i];
        if (i % w == 0 && i != 0) {
            fprintf(file, "\n");
        }
        fprintf(file, "%d ", pixel_value);
    }

    fclose(file);
}
