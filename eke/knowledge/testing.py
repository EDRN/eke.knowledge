# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from plone.app.testing import PloneSandboxLayer, PLONE_FIXTURE, IntegrationTesting, FunctionalTesting
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.testing import z2
from eke.knowledge.tests.base import _TestHandler
import urllib2

class EKEKnowledge(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)
    def setUpZope(self, app, configurationContext):
        import eke.knowledge
        self.loadZCML(package=eke.knowledge)
        z2.installProduct(app, 'eke.knowledge')
        urllib2.install_opener(urllib2.build_opener(_TestHandler))
        import eke.knowledge.tests.base
        eke.knowledge.tests.base.registerLocalTestData()
    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'eke.knowledge:default')
    def teatDownZope(self, app):
        z2.uninstallProduct(app, 'eke.knowledge')
        urllib2.install_opener(urllib2.build_opener())
    
EKE_KNOWLEDGE_FIXTURE = EKEKnowledge()
EKE_KNOWLEDGE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EKE_KNOWLEDGE_FIXTURE,),
    name='EKEKnowledge:Integration',
)
EKE_KNOWLEDGE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EKE_KNOWLEDGE_FIXTURE,),
    name='EKEKnowledge:Functional',
)
