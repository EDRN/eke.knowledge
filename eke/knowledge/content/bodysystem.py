# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Body system.'''

from eke.knowledge.config import PROJECTNAME
from eke.knowledge.interfaces import IBodySystem
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements, directlyProvides
from eke.knowledge.content import knowledgeobject
from Products.CMFCore.utils import getToolByName
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory
from eke.knowledge import dublincore

BodySystemSchema = knowledgeobject.KnowledgeObjectSchema.copy() + atapi.Schema((
    # No other fields
))
# FIXME: KnowledgeObjectSchema has title's predicate set to something wrong.
# When that's finally fixed, remove this line:
BodySystemSchema['title'].predicateURI = dublincore.TITLE_URI

finalizeATCTSchema(BodySystemSchema, folderish=False, moveDiscussion=False)

class BodySystem(knowledgeobject.KnowledgeObject):
    '''Body system.'''
    implements(IBodySystem)
    schema      = BodySystemSchema
    portal_type = 'Body System'

atapi.registerType(BodySystem, PROJECTNAME)

def BodySystemVocabularyFactory(context):
    catalog = getToolByName(context, 'portal_catalog')
    # TODO: filter by review_state?
    results = catalog(object_provides=IBodySystem.__identifier__, sort_on='sortable_title')
    return SimpleVocabulary([SimpleVocabulary.createTerm(i.UID, i.UID, i.Title.decode('utf-8')) for i in results])
directlyProvides(BodySystemVocabularyFactory, IVocabularyFactory)
