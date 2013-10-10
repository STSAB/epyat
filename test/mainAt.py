import sys

sys.path.append("../src")
sys.path.append("./include")

import unittest
import logger
#logger.log.setloglevel(logger.WARNING)


if __name__ == '__main__':
    pattern = "test_EH*.py"
    if len(sys.argv) > 1:
        pattern = sys.argv[1]

    runner = unittest.TextTestRunner(verbosity=2)
    tests = unittest.TestLoader().discover(".", pattern=pattern)
    runner.run(tests)



