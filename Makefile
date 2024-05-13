DEBUG     = -O0 -g
CFLAGS   += -std=c11 -Wextra -Wall -pedantic -Werror -Wshadow
CFLAGS   += ${DEBUG}
LDFLAGS  += -lm
FLAGS    += ${CFLAGS} ${LDFLAGS}

SRC_DIR    = src
BIN_DIR    = bin
TEST_DIR   = test
BUILD_DIR  = build

SOURCES      = $(wildcard ${SRC_DIR}/*.c)
OBJECTS      = $(patsubst ${SRC_DIR}/%.c,${BUILD_DIR}/%.o,${SOURCES})

LIBS         = ${BIN_DIR}/image.so ${BIN_DIR}/convolution.so ${BIN_DIR}/derivation.so ${BIN_DIR}/main.so


.PHONY: clean tests

all: ${BIN_DIR}/edgedetection ${LIBS}

${BUILD_DIR}/%.o: ${SRC_DIR}/%.c
	$(shell mkdir -p $(dir $@))
	-$(CC) $< -c ${CFLAGS} -o $@

${BIN_DIR}/edgedetection: ${OBJECTS}
	$(shell mkdir -p ${BIN_DIR})
	-$(CC) -o ${BIN_DIR}/edgedetection ${CFLAGS} ${OBJECTS} ${LDFLAGS}

${BIN_DIR}/image.so: ${SRC_DIR}/image.c
	$(shell mkdir -p ${BIN_DIR})
	-$(CC) -shared -fPIC -o ${BIN_DIR}/image.so ${CFLAGS} ${LDFLAGS} ${SRC_DIR}/image.c

${BIN_DIR}/convolution.so: ${SRC_DIR}/convolution.c ${SRC_DIR}/image.c
	$(shell mkdir -p ${BIN_DIR})
	-$(CC) -shared -fPIC -o ${BIN_DIR}/convolution.so ${CFLAGS} ${LDFLAGS} ${SRC_DIR}/convolution.c ${SRC_DIR}/image.c

${BIN_DIR}/derivation.so: ${SRC_DIR}/derivation.c ${SRC_DIR}/convolution.c ${SRC_DIR}/image.c
	$(shell mkdir -p ${BIN_DIR})
	-$(CC) -shared -fPIC -o ${BIN_DIR}/derivation.so ${CFLAGS} ${LDFLAGS} ${SRC_DIR}/derivation.c ${SRC_DIR}/convolution.c ${SRC_DIR}/image.c

${BIN_DIR}/main.so: ${SOURCES}
	$(shell mkdir -p ${BIN_DIR})
	-$(CC) -shared -fPIC -o ${BIN_DIR}/main.so ${CFLAGS} ${LDFLAGS} ${SOURCES}

tests: ${LIBS}
	${TEST_DIR}/run-tests.py

clean:
	rm -rf ${BIN_DIR} ${BUILD_DIR}
