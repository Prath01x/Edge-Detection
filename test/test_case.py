import ctypes as ct
import errno
import os.path

from config import VERBOSE, colors
from matrix import Matrix, pretty_print, matrix_from_file, matrix_from_values
from timeout_error import TimeoutError


# helper functions

def compare_values(actual, expected, tolerance):
    return abs(actual - expected) <= tolerance

def compare_array(actual, expected, tolerance):
    return all(compare_values(actual[i], expected[i], tolerance) for i in range(len(expected)))

def compare_image_file_with_matrix(actual, expected_w, expected_h, expected_values, tolerance, allow_none=False):
    actual = actual.split()

    if len(actual) < 4:
        return "Invalid file format."

    if actual[0] != 'P2':
        return "Missing file type specifier (should be P2)."

    if actual[1] != '{:d}'.format(expected_w):
        return f"Incorrect width (expected {expected_w} but was {actual[1]})."

    if actual[2] != '{:d}'.format(expected_h):
        return f"Incorrect height (expected {expected_h} but was {actual[2]})."

    if actual[3] != '255':
        return f"Incorrect maximum value (expected 255 but was {actual[3]})."

    if len(actual) != len(expected_values) + 4:
        return "Number of pixels does not match."

    for i in range(4, len(actual)):
        try:
            actual_value = int(actual[i])
            expected_value = expected_values[i - 4]
            if not ((allow_none and expected_value is None) or compare_values(actual_value, expected_value, tolerance)):
                return f"Incorrect pixel color at pixel {i-4} (expected {expected_value} but was {actual_value})."
        except ValueError:
            return f"Failed to parse pixel value {actual[i]}."

    return None

def compare_image_files(actual, expected, tolerance):
    expected = expected.split()
    return compare_image_file_with_matrix(actual, int(expected[1]), int(expected[2]),
                                          [int(expected[i]) for i in range(4, len(expected))], tolerance)

def read_pgm(path):
    with open(path, 'r') as pgmfile:
        content = pgmfile.read().split()
    assert len(content) >= 4
    w = int(content[1])
    h = int(content[2])
    return matrix_from_values(w, h, content[4:])

def read_min_max(path):
    with open(path, 'r') as minmaxfile:
        content = minmaxfile.read().split()
    assert len(content) == 2
    return float(content[0]), float(content[1])


SMALL_EPSILON = 0.00001
LARGE_EPSILON = 0.1

TEST_DIR = os.path.dirname(__file__)
BUILD_DIR = os.path.join(TEST_DIR, '..', 'bin')
INPUT_DATA_DIR = os.path.join(TEST_DIR, 'data', 'input')
EXPECTED_DATA_DIR = os.path.join(TEST_DIR, 'data', 'expected')


# test cases

class TestCase(object):
    def __init__(self, test_type, module, function, input_file, expected_file, name=None, verbose=VERBOSE):
        self.test_type = test_type
        self.module = module
        self.function = function
        assert input_file is None or os.path.exists(self._get_input_file_name(input_file))
        self.input_file = self._get_input_file_name(input_file) if input_file is not None else None
        assert expected_file is None or os.path.exists(self._get_expected_file_name(expected_file))
        self.expected_file = self._get_expected_file_name(expected_file) if expected_file is not None else None
        self.name = name
        self.verbose = verbose

    def _get_input_file_name(self, input_file):
        return os.path.join(INPUT_DATA_DIR, input_file + '.matrix')

    def _get_expected_file_name(self, expected_file):
        return os.path.join(EXPECTED_DATA_DIR, expected_file + '.matrix')

    def _get_name(self):
        return self.name or os.path.basename(self.input_file).split('.')[0]

    def get_name(self):
        return '.'.join([self.test_type, self.function, self._get_name()])

    def get_name_tuple(self):
        return (self.test_type, self.function, self._get_name())

    def _initialize_lib(self):
        pass

    def run_test(self, timeout=20, color=False):
        path = os.path.join(BUILD_DIR, '{}.so'.format(self.module))
        self.lib = ct.CDLL(path) if os.path.exists(path) else None

        if self.lib:
            self._initialize_lib()
        else:
            return 'Failed to build {}.'.format(self.module)

        return self._run_test(color)

    def _run_test(self, color):
        pass


class GetPixelValueTestCase(TestCase):
    def __init__(self, test_type, input_file, test_cases, name=None):
        self.test_cases = test_cases
        super(GetPixelValueTestCase, self).__init__(test_type, 'image', 'get_pixel_value', input_file, None, name=name)

    def _initialize_lib(self):
        self.lib.get_pixel_value.argtypes = (ct.POINTER(ct.c_float), ct.c_int, ct.c_int, ct.c_int, ct.c_int)
        self.lib.get_pixel_value.restype = ct.c_float

    def _run_test(self, color):
        assert self.input_file is not None
        input_matrix = matrix_from_file(self.input_file, False)
        input_array = input_matrix.get_as_c_array()

        for x, y, expected_value in self.test_cases:
            actual = self.lib.get_pixel_value(ct.cast(input_array, ct.POINTER(ct.c_float)),
                                              input_matrix.w, input_matrix.h, x, y)

            if not compare_values(actual, expected_value, SMALL_EPSILON):
                if color:
                    return (f"{colors.FAIL}Incorrect result after calling get_pixel_value with:{colors.END}\n"
                        f"{colors.BOLD}x:{colors.END} {x}\n"
                        f"{colors.BOLD}y:{colors.END} {y}\n"
                        f"{colors.BOLD}img:{colors.END}\n{input_matrix}\n"
                        f"{colors.BOLD}result:{colors.END} {actual}\n"
                        f"{colors.BOLD}expected:{colors.END} {expected_value}"
                        if self.verbose else
                        f"{colors.FAIL}Incorrect result for get_pixel_value:{colors.END} expected {expected_value} but was {actual}.")
                else:
                    return (f"Incorrect result after calling get_pixel_value with:\n"
                        f"x: {x}\n"
                        f"y: {y}\n"
                        f"img:\n{input_matrix}\n"
                        f"result: {actual}\n"
                        f"expected: {expected_value}"
                        if self.verbose else
                        f"Incorrect result for get_pixel_value: expected {expected_value} but was {actual}.")

        return None



class ApplyThresholdTestCase(TestCase):
    def __init__(self, test_type, input_file, expected_file, threshold, **kwargs):
        self.threshold = threshold
        super(ApplyThresholdTestCase, self).__init__(test_type, 'image', 'apply_threshold', input_file, expected_file, **kwargs)

    def _initialize_lib(self):
        self.lib.apply_threshold.argtypes = (ct.POINTER(ct.c_float), ct.c_int, ct.c_int, ct.c_int)
        self.lib.apply_threshold.restype = None

    def _run_test(self, color):
        assert self.input_file is not None
        assert self.expected_file is not None
        input_matrix = matrix_from_file(self.input_file, False)
        expected_matrix = matrix_from_file(self.expected_file, False)
        input_array = input_matrix.get_as_c_array()
        self.lib.apply_threshold(ct.cast(input_array, ct.POINTER(ct.c_float)),
                                 input_matrix.w, input_matrix.h, self.threshold)

        if compare_array(input_array, expected_matrix.values, SMALL_EPSILON):
            return None
        
        if color:
            return (f"{colors.FAIL}Incorrect result after calling apply_threshold with:{colors.END}\n"
                    f"{colors.BOLD}T:{colors.END} {self.threshold}\n"
                    f"{colors.BOLD}img:{colors.END}\n{input_matrix}\n"
                    f"{colors.BOLD}result:{colors.END}\n{pretty_print(input_array, input_matrix.w, input_matrix.h)}\n"
                    f"{colors.BOLD}expected:{colors.END}\n{expected_matrix}"
                    if self.verbose else
                    f"{colors.FAIL}Incorrect result for apply_threshold.{colors.END}")
        else:
            return (f"Incorrect result after calling apply_threshold with:\n"
                    f"T: {self.threshold}\n"
                    f"img:\n{input_matrix}\n"
                    f"result:\n{pretty_print(input_array, input_matrix.w, input_matrix.h)}\n"
                    f"expected:\n{expected_matrix}"
                    if self.verbose else
                    f"Incorrect result for apply_threshold.")


class ScaleImageTestCase(TestCase):
    def __init__(self, test_type, input_file, expected_file, **kwargs):
        super(ScaleImageTestCase, self).__init__(test_type, 'image', 'scale_image', input_file, expected_file, **kwargs)

    def _initialize_lib(self):
        self.lib.scale_image.argtypes = (ct.POINTER(ct.c_float), ct.POINTER(ct.c_float), ct.c_int, ct.c_int)
        self.lib.scale_image.restype = None

    def _run_test(self, color):
        assert self.input_file is not None
        assert self.expected_file is not None
        input_matrix = matrix_from_file(self.input_file, False)
        expected_matrix = matrix_from_file(self.expected_file, False)
        input_array = input_matrix.get_as_c_array()

        float_array_type = ct.c_float * len(input_matrix.values)
        result = float_array_type()
        result[0:(input_matrix.w * input_matrix.h)]
        result_ptr = ct.cast(result, ct.POINTER(ct.c_float))

        self.lib.scale_image(result_ptr, ct.cast(input_array, ct.POINTER(ct.c_float)),
                             input_matrix.w, input_matrix.h)

        if compare_array(result, expected_matrix.values, LARGE_EPSILON):
            return None
        
        if color:
            return (f"{colors.FAIL}Incorrect result after calling scale_image with:{colors.END}\n"
                    f"{colors.BOLD}img:{colors.END}\n{input_matrix}\n"
                    f"{colors.BOLD}result:{colors.END}\n{pretty_print(result, input_matrix.w, input_matrix.h)}\n"
                    f"{colors.BOLD}expected:{colors.END}\n{expected_matrix}"
                    if self.verbose else
                    f"{colors.FAIL}Incorrect result for scale_image.{colors.END}")
        else:
            return (f"Incorrect result after calling scale_image with:\n"
                    f"img:\n{input_matrix}\n"
                    f"result:\n{pretty_print(result, input_matrix.w, input_matrix.h)}\n"
                    f"expected:\n{expected_matrix}"
                    if self.verbose else
                    f"Incorrect result for scale_image.")


class ReadImageTestCase(TestCase):
    def __init__(self, test_type, input_file, expected_file, **kwargs):
        super(ReadImageTestCase, self).__init__(test_type, 'image', 'read_image_from_file', input_file, expected_file, **kwargs)

    def _get_input_file_name(self, input_file):
        return os.path.join(INPUT_DATA_DIR, input_file + '.pgm')

    def _initialize_lib(self):
        self.lib.read_image_from_file.argtypes = (ct.POINTER(ct.c_char), ct.POINTER(ct.c_int), ct.POINTER(ct.c_int))
        self.lib.read_image_from_file.restype = ct.POINTER(ct.c_float)

    def _run_test(self, color):
        assert self.input_file is not None
        assert self.expected_file is not None
        expected_matrix = matrix_from_file(self.expected_file, False)

        w = ct.c_int(0)
        h = ct.c_int(0)
        
        input_file = self.input_file.encode('utf-8')
        filename_ptr = ct.c_char_p(input_file)

        img_ptr = self.lib.read_image_from_file(filename_ptr, ct.byref(w), ct.byref(h))

        w = w.value
        h = h.value

        if not bool(img_ptr):
            if color:
                return f"{colors.FAIL}Read image function returned NULL for a valid image file.{colors.END}"
            else:
                return "Read image function returned NULL for a valid image file."

        if w != expected_matrix.w:
            return f"Incorrect width (expected {expected_matrix.w} but was {w})."

        if h != expected_matrix.h:
            return f"Incorrect height (expected {expected_matrix.h} but was {h})."

        if compare_array(img_ptr, expected_matrix.values, SMALL_EPSILON):
            return None
        
        result = pretty_print(img_ptr, expected_matrix.w, expected_matrix.h)
        
        if self.verbose:
            return f"Incorrect result after reading image {self.input_file}:\nresult:\n{result}\nexpected\n{expected_matrix}"
        else:
            return "Incorrect result for read_image_from_file."


class ReadBrokenImageTestCase(TestCase):
    def __init__(self, test_type, input_file, **kwargs):
        super(ReadBrokenImageTestCase, self).__init__(test_type, 'image', 'read_image_from_file', input_file, None, **kwargs)

    def _get_input_file_name(self, input_file):
        return os.path.join(INPUT_DATA_DIR, input_file + '.pgm')

    def _initialize_lib(self):
        self.lib.read_image_from_file.argtypes = (ct.POINTER(ct.c_char), ct.POINTER(ct.c_int), ct.POINTER(ct.c_int))
        self.lib.read_image_from_file.restype = ct.POINTER(ct.c_float)

    def _run_test(self, color):
        assert self.input_file is not None

        w = ct.c_int(0)
        h = ct.c_int(0)
        
        input_file = self.input_file.encode('utf-8')
        filename_ptr = ct.c_char_p(input_file)

        img_ptr = self.lib.read_image_from_file(filename_ptr, ct.byref(w), ct.byref(h))

        if not bool(img_ptr):
            return None
        
        if color:
            return f"{colors.FAIL}Read image function did not return NULL for an invalid image file.{colors.END}"
        else:
            return "Read image function did not return NULL for an invalid image file."


class WriteImageTestCase(TestCase):
    def __init__(self, test_type, input_file, expected_file, filename, **kwargs):
        self.filename = filename + '.pgm'
        super(WriteImageTestCase, self).__init__(test_type, 'image', 'write_image_to_file', input_file, expected_file, **kwargs)

    def _get_expected_file_name(self, expected_file):
        return os.path.join(EXPECTED_DATA_DIR, expected_file + '.pgm')

    def _initialize_lib(self):
        self.lib.write_image_to_file.argtypes = (ct.POINTER(ct.c_float), ct.c_int, ct.c_int, ct.POINTER(ct.c_char))
        self.lib.write_image_to_file.restype = None

    def _run_test(self, color):
        assert self.input_file is not None
        assert self.expected_file is not None
        input_matrix = matrix_from_file(self.input_file, False)
        input_array = input_matrix.get_as_c_array()
        
        filename = self.filename.encode('utf-8')
        filename_ptr = ct.c_char_p(filename)

        self.lib.write_image_to_file(ct.cast(input_array, ct.POINTER(ct.c_float)),
                                     input_matrix.w, input_matrix.h, filename_ptr)

        if not os.path.exists(self.filename):
            if color:
                return f"{colors.FAIL}No output file written.{colors.END}"
            else:
                return "No output file written."

        with open(self.filename, 'r') as f:
            content = f.read()
        with open(self.expected_file, 'r') as f:
            expected = f.read()

        error = compare_image_files(content, expected, 1)
        os.remove(self.filename)
        return error


class ConvolveTestCase(TestCase):
    def __init__(self, test_type, input_file, expected_file, kernel, **kwargs):
        self.kernel = self._get_input_file_name(kernel)
        super(ConvolveTestCase, self).__init__(test_type, 'convolution', 'convolve', input_file, expected_file, **kwargs)

    def _initialize_lib(self):
        self.lib.convolve.argtypes = (ct.POINTER(ct.c_float),ct.POINTER(ct.c_float), ct.c_int, ct.c_int, ct.POINTER(ct.c_float), ct.c_int, ct.c_int)
        self.lib.convolve.restype = None

    def _run_test(self, color):
        assert self.input_file is not None
        assert self.expected_file is not None
        input_matrix = matrix_from_file(self.input_file, False)
        expected_matrix = matrix_from_file(self.expected_file, False)

        assert self.kernel is not None and os.path.exists(self.kernel)
        kernel_matrix = matrix_from_file(self.kernel, False)

        input_array = input_matrix.get_as_c_array()
        kernel_array = kernel_matrix.get_as_c_array()

        float_array_type = ct.c_float * len(input_matrix.values)
        result = float_array_type()
        result[0:len(input_matrix.values)]
        result_ptr = ct.cast(result, ct.POINTER(ct.c_float))

        self.lib.convolve(result_ptr, ct.cast(input_array, ct.POINTER(ct.c_float)),
                          input_matrix.w, input_matrix.h,
                          ct.cast(kernel_array, ct.POINTER(ct.c_float)),
                          kernel_matrix.w, kernel_matrix.h)

        if compare_array(result, expected_matrix.values, LARGE_EPSILON):
            return None

        if color:
            return (f"{colors.FAIL}Incorrect result after calling convolve with:{colors.END}\n"
                f"{colors.BOLD}img:{colors.END}\n{input_matrix}\n"
                f"{colors.BOLD}kernel:{colors.END}\n{kernel_matrix}\n"
                f"{colors.BOLD}result:{colors.END}\n{pretty_print(result, expected_matrix.w, expected_matrix.h)}\n"
                f"{colors.BOLD}expected:{colors.END}\n{expected_matrix}"
                if self.verbose else
                f"{colors.FAIL}Incorrect result for convolve.{colors.END}")
        else:
            return (f"Incorrect result after calling convolve with:\n"
                f"img:\n{input_matrix}\n"
                f"kernel:\n{kernel_matrix}\n"
                f"result:\n{pretty_print(result, expected_matrix.w, expected_matrix.h)}\n"
                f"expected:\n{expected_matrix}"
                if self.verbose else
                f"Incorrect result for convolve.")


class GradientMagnitudeTestCase(TestCase):
    def __init__(self, test_type, expected_file, dx_file, dy_file, name):
        self.dx_file = self._get_input_file_name(dx_file)
        self.dy_file = self._get_input_file_name(dy_file)
        super(GradientMagnitudeTestCase, self).__init__(test_type, 'derivation', 'gradient_magnitude', None, expected_file, name)

    def _initialize_lib(self):
        self.lib.gradient_magnitude.argtypes = (ct.POINTER(ct.c_float),ct.POINTER(ct.c_float), ct.POINTER(ct.c_float), ct.c_int, ct.c_int)
        self.lib.gradient_magnitude.restype = None

    def _run_test(self, color):
        assert self.expected_file is not None
        expected_matrix = matrix_from_file(self.expected_file, False)

        assert self.dx_file is not None and os.path.exists(self.dx_file)
        assert self.dy_file is not None and os.path.exists(self.dy_file)
        dx_matrix = matrix_from_file(self.dx_file, False)
        dy_matrix = matrix_from_file(self.dy_file, False)
        dx_array = dx_matrix.get_as_c_array()
        dy_array = dy_matrix.get_as_c_array()

        float_array_type = ct.c_float * len(expected_matrix.values)
        result = float_array_type()
        result[0:(expected_matrix.w * expected_matrix.h)]
        result_ptr = ct.cast(result, ct.POINTER(ct.c_float))

        self.lib.gradient_magnitude(result_ptr, ct.cast(dx_array, ct.POINTER(ct.c_float)),
                                    ct.cast(dy_array, ct.POINTER(ct.c_float)), expected_matrix.w, expected_matrix.h)

        if compare_array(result, expected_matrix.values, LARGE_EPSILON):
            return None
        
        
        if color:
            return (f"{colors.FAIL}Incorrect result after calling gradient_magnitude with:{colors.END}\n"
                    f"{colors.BOLD}d_x:{colors.END}\n{dx_matrix}\n"
                    f"{colors.BOLD}d_y:{colors.END}\n{dy_matrix}\n"
                    f"{colors.BOLD}result:{colors.END}\n{pretty_print(result, expected_matrix.w, expected_matrix.h)}\n"
                    f"{colors.BOLD}expected:{colors.END}\n{expected_matrix}"
                    if self.verbose else
                    f"{colors.FAIL}Incorrect result for gradient_magnitude.{colors.END}")
        else:
            return (f"Incorrect result after calling gradient_magnitude with:\n"
                    f"d_x:\n{dx_matrix}\n"
                    f"d_y:\n{dy_matrix}\n"
                    f"result:\n{pretty_print(result, expected_matrix.w, expected_matrix.h)}\n"
                    f"expected:\n{expected_matrix}"
                    if self.verbose else
                    f"Incorrect result for gradient_magnitude.")


class MainTestCase(TestCase):
    def __init__(self, test_type, input_file, threshold, **kwargs):
        self.expected_blur = self._get_expected_file_name('blur_' + input_file)
        self.expected_dx = self._get_expected_file_name('d_x_' + input_file)
        self.expected_dy = self._get_expected_file_name('d_y_' + input_file)
        self.expected_gm = self._get_expected_file_name('gm_' + input_file)
        self.expected_gm_min_max = os.path.join(EXPECTED_DATA_DIR, input_file + '.minmax')
        self.threshold = threshold
        super(MainTestCase, self).__init__(test_type, 'main', 'main', input_file, 'edges_' + input_file, **kwargs)

    def _get_input_file_name(self, input_file):
        return os.path.join(INPUT_DATA_DIR, input_file + '.pgm')

    def _get_expected_file_name(self, expected_file):
        return os.path.join(EXPECTED_DATA_DIR, expected_file + '.pgm')

    def _get_name(self):
        return '{}-{:d}'.format(os.path.basename(self.input_file).split('.')[0], self.threshold) if not self.name else self.name

    def _initialize_lib(self):
        self.lib.main.argtypes = (ct.c_int, ct.POINTER(ct.c_char_p))
        self.lib.main.restype = ct.c_int

    def _run_test(self, color):
        assert self.expected_file is not None
        assert self.expected_blur is not None and os.path.exists(self.expected_blur)
        assert self.expected_dx is not None and os.path.exists(self.expected_dx)
        assert self.expected_dy is not None and os.path.exists(self.expected_dy)
        assert self.expected_gm is not None and os.path.exists(self.expected_gm)
        assert self.expected_gm_min_max is not None and os.path.exists(self.expected_gm_min_max)

        args = ['main.so', '-T', str(self.threshold), self.input_file]
        arg_array_type = ct.c_char_p * len(args)
        c_args = arg_array_type()
        
        for i in range(0, len(args)):
            c_args[i] = args[i].encode('utf-8')
            
        self.lib.main(len(args), c_args)

        def test_file(name, expected_name, tolerance):
            if not os.path.exists(name):
                if color:
                    return f"{colors.FAIL}No {name} file written.{colors.END}"
                else:
                    return f"No {name} file written."
            
            with open(name, 'r') as f:
                content = f.read()
            with open(expected_name, 'r') as f:
                expected = f.read()
                
            error = compare_image_files(content, expected, tolerance)
            
            if error is not None:
                if color:
                    return f"{colors.FAIL}Error in {name}.{colors.END} {error}"
                else:
                    return f"Error in {name}. {error}"

            return None

        def test_final_file(name, expected_w, expected_h, expected_values, tolerance):
            if not os.path.exists(name):
                if color:
                    return f"{colors.FAIL}No {name} file written.{colors.END}"
                else:
                    return "No {} file written.".format(name)
            with open(name, 'r') as f:
                content = f.read()
                
            error = compare_image_file_with_matrix(content, expected_w, expected_h, expected_values, tolerance, True)
            
            if error is not None:
                if color:
                    return f"{colors.FAIL}Error in {name}.{colors.END} {error}"
                else:
                    return f"Error in {name}. {error}"

            return None

        def cleanup():
            for outfile in ['out_' + x + '.pgm' for x in ['blur', 'd_x', 'd_y', 'gm', 'edges']]:
                if os.path.exists(outfile):
                    os.remove(outfile)

        for name, expected_name in [('out_blur.pgm', self.expected_blur),
                                    ('out_d_x.pgm', self.expected_dx),
                                    ('out_d_y.pgm', self.expected_dy),
                                    ('out_gm.pgm', self.expected_gm)]:

            error = test_file(name, expected_name, 1)
            
            if error is not None:
                cleanup()
                return error

        actual_gm = read_pgm('out_gm.pgm')

        min_value, max_value = read_min_max(self.expected_gm_min_max)
        assert min_value <= max_value
        value_range = max_value - min_value

        def unscale(value):
            return value / 255. * value_range + min_value

        final_tolerance = max(unscale(1), 1.)

        def get_expected_value(value):
            value = unscale(value)
            if compare_values(value, self.threshold, final_tolerance):
                return None
            return 0 if value < self.threshold else 255

        expected_edges = matrix_from_values(actual_gm.w, actual_gm.h, [get_expected_value(value) for value in actual_gm.values])
        
        error = test_final_file('out_edges.pgm', expected_edges.w, expected_edges.h, expected_edges.values, 0)
            
        cleanup()
        
        if error is not None:
            return error
        
        return None
