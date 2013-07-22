# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment: interfaces.
'''

from zope.interface import Interface
from zope import schema
from zope.container.constraints import contains
from eke.knowledge import ProjectMessageFactory as _
from Products.ATContentTypes.interface import IATFolder

class IKnowledgeFolder(IATFolder):
    '''Knowledge folder.'''
    contains('eke.knowledge.interfaces.IKnowledgeObject')
    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'Descriptive name of this folder.'),
        required=True,
    )
    description = schema.Text(
        title=_(u'Description'),
        description=_(u'A short summary of this folder.'),
        required=False,
    )
    rdfDataSource = schema.TextLine(
        title=_(u'RDF Data Source'),
        description=_(u'URL to a source of Resource Description Format data that mandates the contents of this folder.'),
        required=False,
    )
    

class IKnowledgeObject(Interface):
    '''Knowledge object.'''
    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'Title of this resource.'),
        required=True,
    )
    description = schema.Text(
        title=_(u'Description'),
        description=_(u'A short summary of the resource.'),
        required=False,
    )
    identifier = schema.TextLine(
        title=_(u'Identifier'),
        description=_(u'The Uniform Resource Identifier identifying the resource.'),
        required=True,
    )

class IBodySystem(IKnowledgeObject):
    '''Body system.'''

class IDisease(IKnowledgeObject):
    '''Disease.'''
    affectedOrgans = schema.List(
        title=_(u'Affected Body Systems'),
        description=_(u'Body systems for which this disease is an ailment.'),
        required=False,
        value_type=schema.Object(title=_(u'Body System'), schema=IBodySystem),
        unique=True
    )
    icd9Code = schema.TextLine(
        title=_(u'ICD9 Code'),
        description=_(u'International Statistical Classifiction of Disease Code (version 9)'),
        required=False,
    )
    icd10Code = schema.TextLine(
        title=_(u'ICD10 Code'),
        description=_(u'International Statistical Classifiction of Disease Code (version 10)'),
        required=False,
    )
    
