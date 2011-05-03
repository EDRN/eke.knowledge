# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''
EKE: views for content types.
'''

from Acquisition import aq_inner
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class KnowledgeFolderView(BrowserView):
    '''Default view of a knowledge folder.'''
    __call__ = ViewPageTemplateFile('templates/knowledgefolder.pt')
    def getContents(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        return catalog(path=dict(query='/'.join(context.getPhysicalPath()), depth=1), sort_on='sortable_title')
    
class KnowledgeObjectView(BrowserView):
    '''Default view of a knowledge object.'''
    __call__ = ViewPageTemplateFile('templates/knowledgeobject.pt')

class BodySystemView(KnowledgeObjectView):
    '''Default view of a body system.'''
    __call__ = ViewPageTemplateFile('templates/bodysystem.pt')

class DiseaseView(KnowledgeObjectView):
    '''Defaul view of a body system.'''
    __call__ = ViewPageTemplateFile('templates/disease.pt')
    @memoize
    def affectedOrgans(self):
        context = aq_inner(self.context)
        organs = context.affectedOrgans
        return [dict(title=i.title, description=i.description, url=i.absolute_url()) for i in organs]
    
