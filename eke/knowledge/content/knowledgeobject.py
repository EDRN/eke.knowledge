# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Knowledge object.'''

from eke.knowledge import dublincore
from eke.knowledge import ProjectMessageFactory as _
from eke.knowledge.config import PROJECTNAME
from eke.knowledge.interfaces import IKnowledgeObject
from Products.Archetypes import atapi
from Products.Archetypes.interfaces import IObjectPostValidation
from Products.ATContentTypes.content import schemata, base
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.utils import getToolByName
from zope.component import adapts
from zope.interface import implements, directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
import re
_uriSchemes = (
    'http', 'ftp', 'irc', 'news', 'imap', 'gopher', 'jabber', 'webdav', 'smb', 'fish',
    'ldap', 'pop3', 'smtp', 'sftp', 'ssh', 'feed', 'testscheme', 'urn'
)
_uriRegex = re.compile(r'(%s)s?:(//)?[^\s\r\n]+' % '|'.join(_uriSchemes))

KnowledgeObjectSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
    atapi.StringField(
        'identifier',
        required=True,
        default='http://',
        storage=atapi.AnnotationStorage(),
        predicateURI=dublincore.IDENTIFIER_URI,
        widget=atapi.StringWidget(
            label=_(u'Identifier'),
            description=_(u'The Uniform Resource Identifier identifying the resource.'),
        ),
    ),
))
KnowledgeObjectSchema['title'].storage            = atapi.AnnotationStorage()
# FIXME: Should be this:
# KnowledgeObjectSchema['title'].predicateURI       = dublincore.TITLE_URI
# But BMDB uses this:
KnowledgeObjectSchema['title'].predicateURI       = 'http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#Description'
KnowledgeObjectSchema['description'].storage      = atapi.AnnotationStorage()
KnowledgeObjectSchema['description'].predicateURI = dublincore.DESCRIPTION_URI

finalizeATCTSchema(KnowledgeObjectSchema, folderish=False, moveDiscussion=False)

class KnowledgeObject(base.ATCTContent):
    '''Knowledge object.'''
    implements(IKnowledgeObject)
    portal_type               = 'Knowledge Object'
    _at_rename_after_creation = True
    schema                    = KnowledgeObjectSchema
    title                     = atapi.ATFieldProperty('title')
    description               = atapi.ATFieldProperty('description')
    identifier                = atapi.ATFieldProperty('identifier')

atapi.registerType(KnowledgeObject, PROJECTNAME)

class URIValidator(object):
    implements(IObjectPostValidation)
    adapts(IKnowledgeObject)
    def __init__(self, context):
        self.context = context
    def __call__(self, request):
        value = request.form.get('identifier', request.get('identifier', None))
        if value and not _uriRegex.match(value):
            return {'identifier': _(u'Please enter a valid URI.')}
        return None

def ResourceVocabularyFactory(context):
    catalog = getToolByName(context, 'portal_catalog')
    # TODO: filter by review_state?
    results = catalog(portal_type='Knowledge Object', sort_on='sortable_title')
    items = [(i.Title, i.UID) for i in results]
    return SimpleVocabulary.fromItems(items)
directlyProvides(ResourceVocabularyFactory, IVocabularyFactory)
