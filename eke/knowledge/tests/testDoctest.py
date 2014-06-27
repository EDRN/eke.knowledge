# encoding: utf-8
# Copyright 2009-2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''
EDRN Knowledge Environment: functional and documentation tests.
'''

from eke.knowledge.testing import EKE_KNOWLEDGE_FUNCTIONAL_TESTING as LAYER
from plone.testing import layered
import doctest
import unittest2 as unittest

optionFlags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE)

def test_suite():
	return unittest.TestSuite([
		layered(doctest.DocFileSuite('README.rst', package='eke.knowledge', optionflags=optionFlags), LAYER),
	])
	

if __name__ == '__main__':
	unittest.main(defaultTest='test_suite')
	
