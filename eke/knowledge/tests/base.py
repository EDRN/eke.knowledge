# encoding: utf-8
# Copyright 2008-2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Testing base code.
'''

import urllib2, cStringIO

_oneResource = '''<?xml version='1.0' encoding='utf-8'?><rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#' xmlns:bmdb='http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#'><bmdb:ExternalResource rdf:about='http://google.com/'><bmdb:URI>http://google.com/</bmdb:URI><bmdb:Description>A search engine</bmdb:Description></bmdb:ExternalResource></rdf:RDF>'''
_twoResources = '''<?xml version='1.0' encoding='utf-8'?><rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#' xmlns:bmdb='http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#'><bmdb:ExternalResource rdf:about='http://google.com/'><bmdb:URI>http://google.com/</bmdb:URI><bmdb:Description>A search engine</bmdb:Description></bmdb:ExternalResource><bmdb:ExternalResource rdf:about='http://yahoo.com/'><bmdb:URI>http://yahoo.com/</bmdb:URI><bmdb:Description>A web index</bmdb:Description></bmdb:ExternalResource></rdf:RDF>'''
_oneBodySystem = '''<?xml version='1.0' encoding='utf-8'?><rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#' xmlns:_3='http://purl.org/dc/terms/'><rdf:Description rdf:about='urn:edrn:organs:anus'><rdf:type rdf:resource='http://edrn.nci.nih.gov/rdf/types.rdf#BodySystem'/><_3:title>Anus</_3:title></rdf:Description></rdf:RDF>'''
_twoBodySystems = '''<?xml version='1.0' encoding='utf-8'?><rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#' xmlns:_3='http://purl.org/dc/terms/'><rdf:Description rdf:about='urn:edrn:organs:anus'><rdf:type rdf:resource='http://edrn.nci.nih.gov/rdf/types.rdf#BodySystem'/><_3:title>Anus</_3:title></rdf:Description><rdf:Description rdf:about='urn:edrn:organs:rectum'><rdf:type rdf:resource='http://edrn.nci.nih.gov/rdf/types.rdf#BodySystem'/><_3:title>Rectum</_3:title></rdf:Description></rdf:RDF>'''
_oneDisease = '''<?xml version='1.0' encoding='UTF-8'?><rdf:RDF xmlns:_3="http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#" xmlns:_4="http://purl.org/dc/terms/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about="http://edrn.nci.nih.gov/data/diseases/1"><_3:icd9>204.9</_3:icd9><_3:icd10>C81-Q96</_3:icd10><_3:bodySystemsAffected rdf:resource="urn:edrn:organs:anus"/><rdf:type rdf:resource="http://edrn.nci.nih.gov/rdf/types.rdf#Disease"/><_4:description>Seepage of pus or mucus from the anus</_4:description><_4:title>Anal seepage</_4:title></rdf:Description></rdf:RDF>'''
_twoDiseases = '''<?xml version='1.0' encoding='UTF-8'?><rdf:RDF xmlns:_3="http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#" xmlns:_4="http://purl.org/dc/terms/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about="http://edrn.nci.nih.gov/data/diseases/1"><_3:icd9>204.9</_3:icd9><_3:icd10>C81-Q96</_3:icd10><_3:bodySystemsAffected rdf:resource="urn:edrn:organs:anus"/><rdf:type rdf:resource="http://edrn.nci.nih.gov/rdf/types.rdf#Disease"/><_4:description>Seepage of pus or mucus from the anus</_4:description><_4:title>Anal seepage</_4:title></rdf:Description><rdf:Description rdf:about="http://edrn.nci.nih.gov/data/diseases/2"><_3:icd9>205.9</_3:icd9><_3:icd10>C82-Q96</_3:icd10><_3:bodySystemsAffected rdf:resource="urn:edrn:organs:anus"/><rdf:type rdf:resource="http://edrn.nci.nih.gov/rdf/types.rdf#Disease"/><_4:description>Protrusion of the rectum into the vagina</_4:description><_4:title>Rectocele</_4:title></rdf:Description></rdf:RDF>'''
_similarResources = '''<?xml version='1.0' encoding='UTF-8'?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
         xmlns:bmdb="http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#"
         xmlns:edrn="http://edrn.nci.nih.gov/rdf/schema.rdf#"
         xmlns:edrntype="http://edrn.nci.nih.gov/rdf/types.rdf#" 
         xmlns:dc="http://purl.org/dc/terms/">
  <bmdb:ExternalResource rdf:about="http://www.genenames.org/data/hgnc_data.php?hgnc_id=6367">
    <bmdb:URI>http://www.genenames.org/data/hgnc_data.php?hgnc_id=6367</bmdb:URI>
    <bmdb:Description>HGNC entry for kallikrein-related peptidase 6 (KLK6)</bmdb:Description>
  </bmdb:ExternalResource>
  <bmdb:ExternalResource rdf:about="http://www.genenames.org/data/hgnc_data.php?hgnc_id=28873">
    <bmdb:URI>http://www.genenames.org/data/hgnc_data.php?hgnc_id=28873</bmdb:URI>
    <bmdb:Description>HGNC entry 28873 forV-set domain containing T cell activation inhibitor 1 (VTCN1), also called B7-H4,FLJ22418, B7S1, B7X, B7H4</bmdb:Description>
  </bmdb:ExternalResource>
</rdf:RDF>'''
_markedUpDisease = '''<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:_3="http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#" xmlns:_4="http://purl.org/dc/terms/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about="http://edrn.nci.nih.gov/data/diseases/3">
        <_3:icd9>204.9</_3:icd9>
        <_3:icd10>C81-Q96</_3:icd10>
        <_3:bodySystemsAffected rdf:resource="urn:edrn:organs:anus"/>
        <rdf:type rdf:resource="http://edrn.nci.nih.gov/rdf/types.rdf#Disease"/>
        <_4:description>Look&#58; no &lt;sup&gt;superscripts&lt;/sup&gt;&#x002d;or&#x002d;&lt;sub&gt;subscripts&lt;/sub&gt; here.</_4:description>
        <_4:title>&lt;b&gt;Yummy Markup&lt;/b&gt;</_4:title>
    </rdf:Description>
</rdf:RDF>'''
_testData = {}

def registerLocalTestData():
    registerTestData('/resources/a', _oneResource)
    registerTestData('/resources/b', _twoResources)
    registerTestData('/bodysystems/a', _oneBodySystem)
    registerTestData('/bodysystems/b', _twoBodySystems)
    registerTestData('/diseases/a', _oneDisease)
    registerTestData('/diseases/b', _twoDiseases)
    registerTestData('/diseases/c', _markedUpDisease)
    registerTestData('/resources/similar', _similarResources)

class TestHandler(urllib2.BaseHandler):
    '''Fake web server that serves up test data for unit and functional tests.'''
    def testscheme_open(self, req):
        try:
            return cStringIO.StringIO(_testData[req.get_selector()])
        except KeyError:
            raise urllib2.URLError('Not found')

def registerTestData(urlSelector, rdfResponse):
    '''Add additional test data for a given base URL selector to respond with given RDF.'''
    _testData[urlSelector] = rdfResponse
