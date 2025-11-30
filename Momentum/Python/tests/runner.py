import os
import sys

# Ensure Momentum/Python is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import os


def run():
    # Run only the MVP tests to avoid executing the large legacy test-suite
    mvp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mvp_tests'))
    return pytest.main([mvp_dir, '-q'])


if __name__ == '__main__':
    raise SystemExit(run())
