from test_case import *


TEST_SUITE = [
    # Ex 1
    ApplyThresholdTestCase('public', 'threshold1', 'threshold1', 1),
    


    # Ex 2
    GradientMagnitudeTestCase('public', 'gm1', 'gm1_dx', 'gm1_dy', 'gm1'),
    


    # Ex 3
    ScaleImageTestCase('public', 'scale_image_1', 'scale_image_1'),
    

    
    # Ex 4
    GetPixelValueTestCase('public', 'small1', [(0, 0, 1), (2, 2, 9)], name='small1-pv1'),


    ConvolveTestCase('public', 'convolve1', 'convolve1', 'kernel1'),


    
    # Ex 5
    ReadBrokenImageTestCase('public', 'imgbroken1'),
    ReadBrokenImageTestCase('public', 'imgbroken2'),
    


    ReadImageTestCase('public', 'small1', 'small1', name='small1-read'),
    


    WriteImageTestCase('public', 'small1', 'small1', 'small1', name='small1-write'),


    
    # Ex 6
    MainTestCase('public', 'img_P', 100),
    

]
