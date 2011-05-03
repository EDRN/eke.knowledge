# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Knowledge folder.'''

from eke.knowledge.config import PROJECTNAME
from eke.knowledge.interfaces import IKnowledgeFolder
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements
from Products.ATContentTypes.content import folder
from eke.knowledge import ProjectMessageFactory as _
from Products.Archetypes.interfaces import IObjectPostValidation
from zope.component import adapts
import re
_protocols = (
    'http', 'ftp', 'irc', 'news', 'imap', 'gopher', 'jabber', 'webdav', 'smb', 'fish',
    'ldap', 'pop3', 'smtp', 'sftp', 'ssh', 'feed', 'testscheme', 'file'
)
_protocolsRegex = re.compile(r'(%s)s?:(//)?[^\s\r\n]+' % '|'.join(_protocols))

KnowledgeFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((
    atapi.StringField(
        'rdfDataSource',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'RDF Data Source'),
            description=_(u'URL to a source of Resource Description Format data that mandates the contents of this folder.'),
            size=60,
        ),
    ),
))
KnowledgeFolderSchema['title'].storage = atapi.AnnotationStorage()
KnowledgeFolderSchema['description'].storage = atapi.AnnotationStorage()

finalizeATCTSchema(KnowledgeFolderSchema, folderish=True, moveDiscussion=False)

class KnowledgeFolder(folder.ATFolder):
    '''Knowledge folder which contains knowledge objects.'''
    implements(IKnowledgeFolder)
    portal_type               = 'Knowledge Folder'
    _at_rename_after_creation = True
    schema                    = KnowledgeFolderSchema
    title                     = atapi.ATFieldProperty('title')
    description               = atapi.ATFieldProperty('description')
    rdfDataSource             = atapi.ATFieldProperty('rdfDataSource')

atapi.registerType(KnowledgeFolder, PROJECTNAME)

class URLValidator(object):
    implements(IObjectPostValidation)
    adapts(IKnowledgeFolder)
    def __init__(self, context):
        self.context = context
    def __call__(self, request):
        value = request.form.get('rdfDataSource', request.get('rdfDataSource', None))
        if value and not _protocolsRegex.match(value):
            return {'rdfDataSource': _(u'Please enter a valid URL to an RDF data source.')}
        return None
