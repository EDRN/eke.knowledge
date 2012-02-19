# encoding: utf-8
# Copyright 2010-2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment: Filter Tests
'''

import unittest2 as unittest
from eke.knowledge.testing import EKE_KNOWLEDGE_INTEGRATION_TESTING
from eke.knowledge.browser.utils import EntityFilterer, MarkupFilterer

class FiltererTestCase(unittest.TestCase):
    '''Common base for tests of filterers'''
    layer = EKE_KNOWLEDGE_INTEGRATION_TESTING
    def setUp(self):
        super(FiltererTestCase, self).setUp()
        self.filterer = self._constructFilterer()
        self.portal = self.layer['portal']
    def _constructFilterer(self):
        raise NotImplementedError('Subclasses must implement')
    def testEmptyInput(self):
        self.filterer.reset()
        self.filterer.feed(u'')
        self.assertEquals(u'', self.filterer.getResult())
    def testPlainInput(self):
        self.filterer.reset()
        self.filterer.feed(u'Hello')
        self.assertEquals(u'Hello', self.filterer.getResult())
    def testDecimalEntities(self):
        self.filterer.reset()
        self.filterer.feed(u'&#72;e&#108;l&#111;')
        self.assertEquals(u'Hello', self.filterer.getResult())
    def testHexadecimalEntities(self):
        self.filterer.reset()
        self.filterer.feed(u'&#x0048;&#x00E9;&#x006c;l&#x006f;')
        self.assertEquals(u'Héllo', self.filterer.getResult())
    def testNamedEntities(self):
        self.filterer.reset()
        self.filterer.feed(u'&amp;&eacute;&mdash;&copy;')
        self.assertEquals(u'&é—©', self.filterer.getResult())

class EntityFiltererTest(FiltererTestCase):
    '''Unit tests for the EntityFilterer'''
    def _constructFilterer(self):
        return EntityFilterer()

class MarkupFiltererTest(FiltererTestCase):
    '''Unit tests for the MarkupFilterer'''
    def _constructFilterer(self):
        return MarkupFilterer()
    def testUnmarkedupInput(self):
        self.filterer.reset()
        self.filterer.feed(u'H&eacute;llo')
        self.assertEquals(u'Héllo', self.filterer.getResult())
    def testMarkup(self):
        self.filterer.reset()
        self.filterer.feed(u'<sup>S&uuml;perscripts</sup>&#x2014;and&#x2014;<em><sub>emphasized subscripts</sub></em>')
        self.assertEquals(u'Süperscripts—and—emphasized subscripts', self.filterer.getResult())

def test_suite():
    return unittest.TestSuite([
        unittest.makeSuite(EntityFiltererTest),
        unittest.makeSuite(MarkupFiltererTest)
    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

    
