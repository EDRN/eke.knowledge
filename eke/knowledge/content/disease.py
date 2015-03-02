# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Disease.'''

from eke.knowledge import dublincore
from eke.knowledge import ProjectMessageFactory as _
from eke.knowledge.config import PROJECTNAME
from eke.knowledge.content import knowledgeobject
from eke.knowledge.interfaces import IDisease
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.utils import getToolByName
from zope.interface import implements, directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

DiseaseSchema = knowledgeobject.KnowledgeObjectSchema.copy() + atapi.Schema((
    atapi.ReferenceField(
        'affectedOrgans',
        enforceVocabulary=True,
        multiValued=True,
        relationship='affectsOrgan',
        required=False,
        storage=atapi.AnnotationStorage(),
        vocabulary_factory=u'eke.knowledge.BodySystems',
        vocabulary_display_path_bound=-1,
        widget=atapi.ReferenceWidget(
            label=_(u'Affected Body Systems'),
            description=_(u'Body systems for which this disease is an ailment.'),
        ),
    ),
    atapi.StringField(
        'icd9Code',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'ICD9 Code'),
            description=_(u'International Statistical Classifiction of Disease Code (version 9)'),
            size=10,
        ),
        predicateURI=u'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#icd9',
    ),
    atapi.StringField(
        'icd10Code',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'ICD10 Code'),
            description=_(u'International Statistical Classifiction of Disease Code (version 10)'),
            size=10,
        ),
        predicateURI=u'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#icd10',
    ),
))
# FIXME: KnowledgeObjectSchema has title's predicate set to something wrong.
# When that's finally fixed, remove this line:
DiseaseSchema['title'].predicateURI = dublincore.TITLE_URI

finalizeATCTSchema(DiseaseSchema, folderish=False, moveDiscussion=False)

class Disease(knowledgeobject.KnowledgeObject):
    '''Disease.'''
    implements(IDisease)
    schema          = DiseaseSchema
    portal_type     = 'Disease'
    affectedOrgans = atapi.ATReferenceFieldProperty('affectedOrgans')
    icd9Code        = atapi.ATFieldProperty('icd9Code')
    icd10Code       = atapi.ATFieldProperty('icd10Code')

atapi.registerType(Disease, PROJECTNAME)

def DiseaseVocabularyFactory(context):
    catalog = getToolByName(context, 'portal_catalog')
    # TODO: filter by review_state?
    results = catalog(object_provides=IDisease.__identifier__, sort_on='sortable_title')
    return SimpleVocabulary([SimpleVocabulary.createTerm(i.UID, i.UID, i.Title.decode('utf-8')) for i in results])
directlyProvides(DiseaseVocabularyFactory, IVocabularyFactory)
