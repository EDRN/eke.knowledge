# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''
EDRN Knowledge Environment: test the setup of this package.
'''

import unittest2 as unittest
from eke.knowledge.testing import EKE_KNOWLEDGE_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName

class SetupTest(unittest.TestCase):
    '''Unit tests the setup of this package.'''
    layer = EKE_KNOWLEDGE_INTEGRATION_TESTING
    def setUp(self):
        super(SetupTest, self).setUp()
        self.portal = self.layer['portal']
    def testCatalogIndexes(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        indexes = catalog.indexes()
        for i in ('identifier',):
            self.failUnless(i in indexes, '%s not found in catalog indexes' % i)
    def testCatalogMetadata(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        metadata = catalog.schema()
        for i in ('identifier',):
            self.failUnless(i in metadata, '%s not found in catalog metadata' % i)
    def testForWideURLField(self):
        '''Ensure fields for URLs are extra wide.'''
        from eke.knowledge.content.knowledgefolder import KnowledgeFolderSchema
        self.failUnless(KnowledgeFolderSchema['rdfDataSource'].widget.size >= 60)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

    
