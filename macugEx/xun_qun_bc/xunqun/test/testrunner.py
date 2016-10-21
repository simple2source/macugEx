from gevent import monkey

monkey.patch_all()
import unittest
import sys
import os

sys.path.append('..')

main = unittest.main

if __name__ == '__main__':
    if len(sys.argv) > 2:
        print('unsupport multi argument')
        exit()
    elif len(sys.argv) > 1:
        if os.path.isdir(sys.argv[1]):
            discover_dir = sys.argv[1]
            pattern = 'test*.py'
        else:
            discover_dir, pattern = os.path.split(sys.argv[1])
    else:
        discover_dir = '.'
        pattern = 'test*.py'
    loader = unittest.TestLoader()
    tests = loader.discover(discover_dir, pattern=pattern)
    testRunner = unittest.runner.TextTestRunner(verbosity=2)
    testRunner.run(tests)
