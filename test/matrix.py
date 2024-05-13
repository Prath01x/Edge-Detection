import ctypes as ct
import numbers
import os.path


def pretty_print(values, w, h):
    integral = all(isinstance(x, numbers.Integral) for x in values)
    MAX_WIDTH = 10
    if integral:
        base_format = '{:d}'
        actual_format = '{:{:d}}'
    else:
        base_format = '{:.2f}'
        actual_format = '{:{:d}.2f}'
    max_width = max(len(base_format.format(x)) for x in values)
    max_width = min(max_width, MAX_WIDTH)
    if integral:
        cutoff_value = 10 ** (MAX_WIDTH - 1)
        max_value = cutoff_value - 1
    else:
        cutoff_value = 10 ** (MAX_WIDTH - 4)
        max_value = cutoff_value - 0.01
    return '\n'.join(' '.join(actual_format.format(x, max_width + 1) if abs(x) < cutoff_value else ('<-' if x < 0 else ' >') + ('{:d}' if integral else '{:.2f}').format(max_value)
                              for x in values[line_no * w:(line_no + 1) * w])
                     for line_no in range(0, h))

class Matrix(object):
    def __init__(self, w, h, values):
        assert len(values) == w * h
        self.w = w
        self.h = h
        self.values = values

    def get(self, x, y):
        return self.values[x + w * y]

    def get(self, i):
        return self.values[i]

    def get_as_c_array(self):
        float_array_type = ct.c_float * len(self.values)
        array = float_array_type()
        array[0:self.w * self.h] = self.values
        return array

    def __str__(self):
        return pretty_print(self.values, self.w, self.h)

def matrix_from_file(filename, integer=False):
    with open(filename, 'r') as matrix_file:
        lines = matrix_file.readlines()
    w = len(lines[0].split())
    h = len(lines)
    values = [int(number) if integer else float(number) for line in lines for number in line.split()]
    return Matrix(w, h, values)

def matrix_from_values(w, h, values):
    values = [int(number) for number in values] if isinstance(values[0], str) else values
    return Matrix(w, h, values)
