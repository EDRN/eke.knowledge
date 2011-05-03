# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''
EKE: RDF ingest for knowledge objects into knowledge folders.
'''

from Acquisition import aq_inner, aq_parent
from eke.knowledge import dublincore
from eke.knowledge import ProjectMessageFactory as _
from eke.knowledge.interfaces import IKnowledgeObject
from eke.knowledge.browser.utils import updateObject, getUIDsFromURIs
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from rdflib import ConjunctiveGraph, URLInputSource, URIRef
from zope.component import queryUtility
from utils import MarkupFilterer
import threading

# Well-known URI refs
_bodySystemURI       = URIRef('http://edrn.nci.nih.gov/rdf/types.rdf#BodySystem')
_dcTitleURI          = URIRef(dublincore.TITLE_URI)
_diseaseURI          = URIRef('http://edrn.nci.nih.gov/rdf/types.rdf#Disease')
_externalResourceURI = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#ExternalResource')
_typeURI             = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')

# Predicate URIs
_bodySystemsAffectedPredURI = URIRef('http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#bodySystemsAffected')

# Handlers are registered here as a mapping from RDF type URI ref to a handler object:
_handlers = {}

class Results(object):
    '''All information relating to the results of an ingest.'''
    def __init__(self, createdObjects, warnings):
        self.createdObjects, self.warnings = createdObjects, warnings
    @property
    def numWarnings(self):
        return len(self.warnings)
    @property
    def numObjectsCreated(self):
        return len(self.createdObjects)

class CreatedObject(object):
    '''A holder for a newly created object whose genesis was via RDF.'''
    def __init__(self, obj):
        self.obj = obj
        self._title = obj.title
        self._url = obj.absolute_url()
        self._uri = obj.identifier
    @property
    def title(self):
        '''Get the title of the newly created object.'''
        return self._title
    @property
    def url(self):
        '''Get the URL of the newly created object.'''
        return self._url
    @property
    def identifier(self):
        '''Get the URI from the RDF that identifies this object.'''
        return self._uri
    def reindex(self):
        '''Ask the newly created object to reindex itself in the catalog.'''
        self.obj.reindexObject()

class IngestHandler(object):
    '''An ingest handler is responsible for ingesting one kind of described
    object in RDF.  Concrete subclasses are made for each RDF type.  These
    subclasses must implement the ``createObjects`` method.'''
    def createObjects(self, uri, predicates, statements, context):
    	'''Create an object identified by uri and with a given set of
    	descriptive predicates.  All of the statements from the current ingest
    	are also available, if the object being described refers to other
    	objects.  The object should be created in the given context.  A
    	sequence of ``CreatedObject`` objects should be returned; usually this
    	sequence has just one object in it, however there are cases where
    	what's described will refer to other child objects, and so they must
    	be returned as well.'''
        raise NotImplementedError('Subclasses must implement the IngestHandler.createObjects method')
    def generateTitle(self, uri, predicates):
    	'''Generate a title for the new object.  By default we use the Dublin
    	Core term for a title (via its predicate URI) in the statements.  May
    	raise a KeyError if there's no title URI.'''
        return unicode(predicates[_dcTitleURI][0])
    def generateID(self, uri, predicates, normalizerFunction):
    	'''Generate an ID for the new object.  By default, we look for a
    	predicate uri in the predicates that matches the Dublin Core term for
    	"title" and normalize it with the given normalizerFunction.
    	Subclasses may override this to provide custom behavior.'''
        filterer = MarkupFilterer()
        filterer.feed(predicates[_dcTitleURI][0])
        return normalizerFunction(filterer.getResult())
    def deleteExistingObject(self, objectID, context, uri, predicates, statements):
    	'''Delete any existing object in the context with the given objectID.
    	Subclasses may override this in order to nuke specialized nets of
    	objects.'''
        if objectID in context.objectIds():
            context.manage_delObjects(objectID)

def registerHandler(typeURI, handler):
    '''Register an ingest handler that can ingest an RDF object described by the given type URI.'''
    _handlers[typeURI] = handler

class RDFIngestException(Exception):
    '''Exception indicating an error during RDF ingest.'''

class KnowledgeFolderIngestor(BrowserView):
    '''Default RDF ingestion.'''
    template = ViewPageTemplateFile('templates/ingestresults.pt')
    objects, render, _results = [], True, None
    def __call__(self, rdfDataSource=None):
        '''Ingest and render a results page.'''
        context = aq_inner(self.context)
        if rdfDataSource is None:
            rdfDataSource = context.rdfDataSource
        if not rdfDataSource:
            raise RDFIngestException(_(u'This folder has no RDF data source URL.'))
        normalizerFunction = queryUtility(IIDNormalizer).normalize
        graph = ConjunctiveGraph()
        graph.parse(URLInputSource(rdfDataSource))
        statements = self._parseRDF(graph)
        createdObjects = []
        for uri, predicates in statements.items():
            typeURI = predicates[_typeURI][0]
            handler = _handlers[typeURI]
            objectID = handler.generateID(uri, predicates, normalizerFunction)
            handler.deleteExistingObject(objectID, context, uri, predicates, statements)
            title = handler.generateTitle(uri, predicates)
            created = handler.createObjects(objectID, title, uri, predicates, statements, context)
            for obj in created:
                obj.reindex()
            createdObjects.extend(created)
            self.objects = createdObjects
        return self.renderResults()
    def renderResults(self):
        '''Render a results page. Provided here in case subclasses override __call__ and need
        to render a results page without duplicating the logic here.'''
        return self.render and self.template() or len(self.objects)
    def results(self):
        rc = self._results is not None and self._results or Results(self.objects, [])
        return rc
    def _parseRDF(self, graph):
    	'''Parse the statements in graph into a mapping {u→{p→o}} where u is a
    	resource URI, p is a predicate URI, and o is a list of objects which
    	may be literals or URI references.'''
        statements = {}
        for s, p, o in graph:
            if s not in statements:
                statements[s] = {}
            predicates = statements[s]
            if p not in predicates:
                predicates[p] = []
            predicates[p].append(o)
        return statements

class ExternalResourceHandler(IngestHandler):
    '''Handler for external resources, ie, ``Knowledge Objects``.'''
    def __init__(self):
        self.counter = 0
        self.lock = threading.Lock()
    def generateID(self, uri, predicates, normalizerFunction):
        try:
            self.lock.acquire()
            self.counter += 1
            return '%s-%d' % (normalizerFunction(uri), self.counter)
        finally:
            self.lock.release()
    def generateTitle(self, uri, predicates):
        return unicode(predicates[URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#Description')][0])
    def createObjects(self, objectID, title, uri, predicates, statements, context):
        resource = context[context.invokeFactory('Knowledge Object', objectID)]
        updateObject(resource, uri, predicates)
        return [CreatedObject(resource)]
    def deleteExistingObject(self, objectID, context, uri, predicates, statements):
        '''Check catalog for identifier (uri) and if exists, delete the object by its object ID.'''
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(identifier=unicode(uri), object_provides=IKnowledgeObject.__identifier__)
        for i in results:
            obj = i.getObject()
            container = aq_parent(aq_inner(obj))
            if container == context:
                context.manage_delObjects(obj.id)

class BodySystemHandler(IngestHandler):
    '''Handler for ``Body System`` objects.'''
    def createObjects(self, objectID, title, uri, predicates, statements, context):
        bodySystem = context[context.invokeFactory('Body System', objectID)]
        updateObject(bodySystem, uri, predicates)
        return [CreatedObject(bodySystem)]

class DiseaseHandler(IngestHandler):
    '''Handler for ``Disease`` objects.'''
    def createObjects(self, objectID, title, uri, predicates, statements, context):
        disease = context[context.invokeFactory('Disease', objectID)]
        updateObject(disease, uri, predicates)
        if _bodySystemsAffectedPredURI in predicates:
            disease.setAffectedOrgans(getUIDsFromURIs(context, predicates[_bodySystemsAffectedPredURI]))
        return [CreatedObject(disease)]

registerHandler(_externalResourceURI, ExternalResourceHandler())
registerHandler(_bodySystemURI, BodySystemHandler())
registerHandler(_diseaseURI, DiseaseHandler())

