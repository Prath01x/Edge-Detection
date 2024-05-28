#include <stdio.h>
#include <stdlib.h>

#include "argparser.h"
#include "convolution.h"
#include "derivation.h"
#include "gaussian_kernel.h"
#include "image.h"

int main(int const argc, char **const argv) {
    
    parse_arguments(argc, argv);
    printf("Computing edges for image file %s with threshold %i\n",
           image_file_name, threshold);


     int w, h;
    float* img = read_image_from_file(image_file_name, &w, &h);
    if (img == NULL) {
        return 1;
    }
     

    float* blurred_img = (float*)malloc(w * h * sizeof(float));
    convolve(blurred_img, img, w, h, gaussian_k, gaussian_w, gaussian_h);
    write_image_to_file(blurred_img, w,h,"out_blur.pgm");
    
    float* blurredx =(float*)malloc(w * h * sizeof(float));
    float* blurredy = (float*)malloc(w * h * sizeof(float));

    derivation_x_direction( blurredx,blurred_img,w ,h);
    derivation_y_direction( blurredy,blurred_img,w ,h);
    
    float* resultx=(float*)malloc(w * h * sizeof(float));
    float* resulty=(float*)malloc(w * h * sizeof(float));

    scale_image(resultx,blurredx,  w, h);
    scale_image(resulty,blurredy,  w, h);

    write_image_to_file(resultx, w,h,"out_d_x.pgm");
    write_image_to_file(resulty, w,h,"out_d_y.pgm");

    
    float* grad_res=(float*)malloc(w * h * sizeof(float));
    gradient_magnitude(grad_res, blurredx, blurredy,  w,  h);
float* scaled_grad=(float*)malloc(w * h * sizeof(float));
scale_image(scaled_grad,grad_res,w,h);
write_image_to_file(scaled_grad, w,h,"out_gm.pgm");

   
apply_threshold(grad_res, w, h,threshold);
write_image_to_file(grad_res,w,h,"out_edges.pgm");
free(img);
    free(blurred_img);
    free(blurredx);
    free(blurredy);
    free(resultx);
    free(resulty);
    free(grad_res);
    free(scaled_grad);
    
return 0;
}
