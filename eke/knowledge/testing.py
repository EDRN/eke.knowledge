# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from plone.app.testing import PloneSandboxLayer, PLONE_FIXTURE, IntegrationTesting, FunctionalTesting
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.testing import z2

class EKEKnowledge(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)
    def setUpZope(self, app, configurationContext):
        import eke.knowledge
        self.loadZCML(package=eke.knowledge)
        z2.installProduct(app, 'eke.knowledge')
        import eke.knowledge.tests.base
        eke.knowledge.tests.base.registerLocalTestData()
    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'eke.knowledge:default')
    def teatDownZope(self, app):
        z2.uninstallProduct(app, 'eke.knowledge')
    
EKE_KNOWLEDGE_FIXTURE = EKEKnowledge()
EKE_KNOWLEDGE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EKE_KNOWLEDGE_FIXTURE,),
    name='EKEKnowledge:Integration',
)
EKE_KNOWLEDGE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EKE_KNOWLEDGE_FIXTURE,),
    name='EKEKnowledge:Functional',
)
