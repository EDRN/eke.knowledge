# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment: browser utilities.'''

from rdflib import URIRef
from Products.CMFCore.utils import getToolByName
import HTMLParser, htmlentitydefs

class EntityFilterer(HTMLParser.HTMLParser):
    '''A filter for HTML named and numeric entities that converts them to
    their equivalent Unicode characters.'''
    _result = []
    def getResult(self):
        return u''.join(self._result)
    def reset(self):
        HTMLParser.HTMLParser.reset(self)
        self._result = []
    def _formatAttrs(self, attrs):
        if len(attrs) == 0:
            return u''
        reformatted = []
        for name, value in attrs:
            reformatted.append(u'%s="%s"' % (name, value))
        return u' %s' % u' '.join(reformatted)
    def handle_starttag(self, tag, attrs):
        self._result.append(u'<%s%s>' % (tag, self._formatAttrs(attrs)))
    def handle_startendtag(self, tag, attrs):
        self._result.append(u'<%s%s/>' % (tag, self._formatAttrs(attrs)))
    def handle_endtag(self, tag):
        self._result.append(u'</%s>' % tag)
    def handle_data(self, data):
        self._result.append(data)
    def handle_charref(self, name):
        if name[0] in ('x', 'X'):
            self._result.append(unichr(int(name[1:], 16)))
        else:
            self._result.append(unichr(int(name)))
    def handle_entityref(self, name):
        try:
            self._result.append(unichr(htmlentitydefs.name2codepoint[name]))
        except KeyError:
            self._result.append(u'&%s;' % name)
    def handle_comment(self, data):
        self.result.append(u'<!--%s-->' % data)
    def handle_decl(self, decl):
        self.result.append(decl)
    def handle_pi(self, data):
        self.result.append(u'<?%s>' % data)

class MarkupFilterer(EntityFilterer):
    '''A filter for HTML named and numeric entities that converts them to
    their equivalent Unicode characters and strips out all HTML markup.'''
    def handle_starttag(self, tag, attrs):
        pass
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        pass
    def handle_comment(self, data):
        pass
    def handle_decl(self, decl):
        pass
    def handle_pi(self, data):
        pass

def updateObject(obj, uri, predicates, context=None):
    '''Update a generic object by matching up predicate URIs to predicate
    URIs listed in Archetypes field descriptions.
    '''
    obj.identifier = uri
    for f in obj.schema.fields():
        try:
            predicateURI = URIRef(f.predicateURI)
        except AttributeError:
            continue
        if predicateURI in predicates:
            mutator = f.getMutator(obj)
            if f.type == 'reference':
                uids = getUIDsFromURIs(context, predicates[predicateURI])
                if len(uids) == 0:
                    continue
                if f.multiValued:
                    mutator(uids)
                else:
                    mutator(uids[0])
            else:
                def convertEntities(s):
                    filterer = EntityFilterer()
                    filterer.feed(s)
                    return filterer.getResult()
                values = [unicode(v) for v in predicates[predicateURI]]
                if f.multiValued:
                    mutator([convertEntities(s) for s in values])
                else:
                    value = values[0]
                    # If a field specifically says its RDF literal value is not marked up, just use it directly.
                    if getattr(f, 'unmarkedUpRDFLiteral', False):
                        mutator(value)
                    else:
                        # Otherwise, if it's a title or description, strip it of any HTML markup and convert HMTL entities.
                        if f.getName() in ('title', 'description'):
                            filterer = MarkupFilterer()
                            filterer.feed(value)
                            mutator(filterer.getResult())
                        else:
                            # Otherwise, we consider it HTML, and all we have to do is convert any entities,
                            # leaving the markup in place.
                            value = convertEntities(value)
                            # Work around "fix" to http://dev.plone.org/plone/ticket/10141
                            if f.getType() == 'Products.Archetypes.Field.DateTimeField':
                                value = value.replace('T', ' ')
                            mutator(value)

def getUIDsFromURIs(context, uris):
    '''Return a list of object UIDs that correspond to the URI identifiers
    given in uris.  The context is required in order to look up the
    portal_catalog tool.  Note this uses the catalog to find uris listed in
    the identifier index.  UIDs are returned in no particular order, and there
    may be fewer UIDs than URIs passed in.
    '''
    catalog = getToolByName(context, 'portal_catalog')  # Get the catalog
    uris = [unicode(i) for i in uris]                   # Convert URIRefs into plain unicode strings
    results = catalog(identifier=uris)                  # Search for those strings
    return [i.UID for i in results]                     # Return the UID of each match
    
