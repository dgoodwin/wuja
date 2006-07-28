import unittest
import sys
import settestpath
import configureLogging

import feedTests
import modelTests
import notifierTests
import configTests

from unittest import TestSuite

def suite():
    # Append all test suites here:
    return TestSuite((
        feedTests.suite(),
        modelTests.suite(),
        notifierTests.suite(),
        configTests.suite(), # not pure unit tests, candidate for future removal
    ))

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
