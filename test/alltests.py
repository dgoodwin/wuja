import unittest
import sys
import settestpath

import parsingTests

def suite():
    # Append all test suites here:
    return unittest.TestSuite((parsingTests.suite(),))

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
