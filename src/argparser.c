#include "argparser.h"

#include <err.h>
#include <getopt.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int threshold = 10;
char *image_file_name = "test_image_1";

void parse_arguments(int const argc, char **const argv) {
    for (;;) {
        switch (getopt(argc, argv, "T:")) {
            case -1:
                if (argc - optind != 1) {
                    return;
                }
                image_file_name = argv[optind];
                return;

            case 'T': {
                char *end;
                threshold = strtoul(optarg, &end, 0);
                if (end == optarg || *end != '\0') {
                    errx(EXIT_FAILURE, "invalid threshold '%s'", optarg);
                }
                break;
            }
        }
    }
}
