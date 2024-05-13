#ifndef ARGPARSER_H
#define ARGPARSER_H

#include <stdbool.h>
#include <stdint.h>

void parse_arguments(int argc, char **argv);

extern int threshold;
extern char *image_file_name;

#endif
