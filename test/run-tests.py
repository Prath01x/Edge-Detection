#!/usr/bin/env python3
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import re
from config import get_argparser, run_tests
from test_suite import TEST_SUITE

if __name__ == '__main__':
    parser = get_argparser()
    args = parser.parse_args()

    test_filter = None
    if args.filter:
        test_filter = re.compile(args.filter)

    all_tests = []

    for test in TEST_SUITE:
        if not test_filter or test_filter.match(test.get_name()):
            all_tests.append(test)

    if args.list:
        for test in all_tests:
            print(test.get_name())
        exit(0)

    run_tests(args, all_tests)
