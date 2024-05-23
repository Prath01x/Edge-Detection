#include <stdio.h>
#include <stdlib.h>

#include "argparser.h"
#include "convolution.h"
#include "derivation.h"
#include "gaussian_kernel.h"
#include "image.h"

int main(int const argc, char **const argv) {
    /**
     * Parse arguments. The parsed image file name and threshold are available
     * in the image_file_name and threshold global variables (see argparser.h).
     */
    parse_arguments(argc, argv);
    printf("Computing edges for image file %s with threshold %i\n",
           image_file_name, threshold);
 /**
     * Read Image from given file.
     *
     * If the input file is broken terminate with return value 1.
     *
     * Hint: The width and height of the image have to be accessible in the
     * scope of this function.
     */
    // TODO: Implement me!

     int w, h;
    float* img = read_image_from_file(image_file_name, &w, &h);
    if (img == NULL) {
        return 1;
    }
     

    /**
     * Blur the image by using convolve with the given Gaussian kernel matrix
     * gaussian_k (defined in gaussian_kernel.h). The width of the matrix is
     * gaussian_w, the height is gaussian_h.
     *
     * Afterwards, write the resulting blurred image to the file out_blur.pgm.
     */
    // TODO: Implement me!
    float* blurred_img = (float*)malloc(w * h * sizeof(float));
    convolve(blurred_img, img, w, h, gaussian_k, gaussian_w, gaussian_h);
    write_image_to_file(blurred_img, w,h,"out_blur.pgm");
    /**
     * Compute the derivation of the blurred image computed above in both x and
     * y direction.
     *
     * Afterwards, rescale both results and write them to the files out_d_x.pgm
     * and out_d_y.pgm respectively.
     */
    // TODO: Implement me!
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

    /**
     * Compute the gradient magnitude of the blurred image by using the
     * (unscaled!) derivations in x- and y-direction computed earlier.
     *
     * Afterwards, rescale the result and write it to out_gm.pgm.
     */
    // TODO: Implement me!
    float* grad_res=(float*)malloc(w * h * sizeof(float));
    gradient_magnitude(grad_res, blurredx, blurredy,  w,  h);
float* scaled_grad=(float*)malloc(w * h * sizeof(float));
scale_image(scaled_grad,grad_res,w,h);
write_image_to_file(scaled_grad, w,h,"out_gm.pgm");

    /**
     * Apply the threshold to the gradient magnitude.
     * Then write the result to the file out_edges.pgm.
     */
    // TODO: Implement me!
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
