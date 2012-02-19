This package provides Plone 3 content objects for the EDRN Knowledge
Environment (EKE_).  In particular, it provides the basic classes for all EKE
objects and basic RDF_ ingest capabilities for EKE.


Installation
============

Add "eke.knowledge" to the buildout.


Content Types
=============

The content types introduced in this package include the following:

Knowledge Folder
    A folder that contains knowledge objects.  It can also repopulate its
    contents from and RDF data source.
Knowledge Object
    A knowledge object is a generic resource that can be identified by URI_.
Body System
    A kind of identified object that describes a single system of the human
    body, such as an organ.
Disease
    A kind of identified object that is an ailment upon a body system, such a
    lymphoma or another kind of cancer.

The remainder of this document demonstrates the content types and RDF ingest
using a series of functional tests.


Tests
=====

First we have to set up some things and login to the site::

    >>> app = layer['app']
    >>> from plone.testing.z2 import Browser
    >>> from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
    >>> browser = Browser(app)
    >>> browser.handleErrors = False
    >>> browser.addHeader('Authorization', 'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD))
    >>> portal = layer['portal']    
    >>> portalURL = portal.absolute_url()

We'll also have a second browser that's unprivileged for some later
demonstrations::

    >>> unprivilegedBrowser = Browser(app)

Now, let's check things out.


Addable Content
---------------

Here we'll exercise some of the content objects available in this project and
demonstrate their properties and constraints.


Knowledge Folder
~~~~~~~~~~~~~~~~

A knowledge folder contains identified objects.  They can be created anywhere
in the portal::

    >>> browser.open(portalURL)
    >>> l = browser.getLink(id='knowledge-folder')
    >>> l.url.endswith('createObject?type_name=Knowledge+Folder')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = u'My Knowledge Folder'
    >>> browser.getControl(name='description').value = u'This folder is just for functional tests.'
    >>> browser.getControl(name='rdfDataSource').value = u'testscheme://localhost/resources/a'
    >>> browser.getControl(name='form.button.save').click()
    >>> 'my-knowledge-folder' in portal.objectIds()
    True
    >>> f = portal['my-knowledge-folder']
    >>> f.title
    'My Knowledge Folder'
    >>> f.description
    'This folder is just for functional tests.'
    >>> f.rdfDataSource
    'testscheme://localhost/resources/a'

Knowledge folders hold knowledge objects (and objects of child classes) as
well as other knowledge folders.  We'll test adding various knowledge objects
below, but let's make sure there's a link to created nested knowledge
folders::

    >>> browser.open(portalURL + '/my-knowledge-folder')
    >>> l = browser.getLink(id='knowledge-folder')
    >>> l.url.endswith('createObject?type_name=Knowledge+Folder')
    True


Knowledge Object
~~~~~~~~~~~~~~~~

Generic resources are termed Knowledge Objects.  They're the most generic
object defined in EKE, and form the ultimate base class of all other knowledge
objects.  Such resources, like all other knowledge objects, may be created
only in Knowledge Folders::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='knowledge-object')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

So, let's create one in our above knowledge folder::

    >>> browser.open(portalURL + '/my-knowledge-folder')
    >>> l = browser.getLink(id='knowledge-object')
    >>> l.url.endswith('createObject?type_name=Knowledge+Object')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = u'Google'
    >>> browser.getControl(name='description').value = u'Google search is a Web search engine owned by Google, Inc.'
    >>> browser.getControl(name='identifier').value = u'http://google.com/'
    >>> browser.getControl(name='form.button.save').click()
    >>> 'google' in f.objectIds()
    True
    >>> google = f['google']
    >>> google.title
    'Google'
    >>> google.description
    'Google search is a Web search engine owned by Google, Inc.'
    >>> google.identifier
    'http://google.com/'
    
A knowledge object assumes its identifier is a valid URL—even if it's an
URN—and will render it as a hyperlink.  Let's verify that::

    >>> browser.contents
    '...<a href="http://google.com/">...'
    
Body System
~~~~~~~~~~~

A body system is what EDRN terms an organ (being more generic than an organ).
They are themselves knowledge objects (hence resources identified with a URI).
As such, they may be created only within knowledge folders::

    >> browser.open(portalURL)
    >> browser.getLink(id='body-system')
    Traceback (most recent call last).
    ...
    LinkNotFoundError
    
Creating one by hand is simple enough::

    >>> browser.open(portalURL + '/my-knowledge-folder')
    >>> l = browser.getLink(id='body-system')
    >>> l.url.endswith('createObject?type_name=Body+System')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = u'Anus'
    >>> browser.getControl(name='description').value = u"The anus is an opening at the waste end of a human's digestive tract."
    >>> browser.getControl(name='identifier').value = u'urn:edrn:organs:anus'
    >>> browser.getControl(name='form.button.save').click()
    >>> 'anus' in f.objectIds()
    True
    >>> anus = f['anus']
    >>> anus.title
    'Anus'
    >>> anus.description
    "The anus is an opening at the waste end of a human's digestive tract."
    >>> anus.identifier
    'urn:edrn:organs:anus'

Disease
~~~~~~~

Diseases are ailments (like cancer) that affect body systems.  They too are
knowledge objects (and have URIs), and may only exist within knowledge
folders::

    >> browser.open(portalURL)
    >> browser.getLink(id='disease')
    Traceback (most recent call last).
    ...
    LinkNotFoundError

We can create one by hand (though RDF ingest will be far more common, see
below)::

    >>> browser.open(portalURL + '/my-knowledge-folder')
    >>> l = browser.getLink(id='disease')
    >>> l.url.endswith('createObject?type_name=Disease')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = u'Squamous Cell Carcinoma'
    >>> browser.getControl(name='description').value = u'A malignant tumor of squamous cell epithelium.'
    >>> browser.getControl(name='identifier').value = u'urn:edrn:diseases:scc'
    >>> browser.getControl(name='icd9Code').value = '509.9'
    >>> browser.getControl(name='icd10Code').value = 'C91-Q12'
    >>> browser.getControl(name='affectedOrgans:list').value = [anus.UID()]
    >>> browser.getControl(name='form.button.save').click()
    >>> 'squamous-cell-carcinoma' in f.objectIds()
    True
    >>> ssc = f['squamous-cell-carcinoma']
    >>> ssc.title
    'Squamous Cell Carcinoma'
    >>> ssc.description
    'A malignant tumor of squamous cell epithelium.'
    >>> ssc.identifier
    'urn:edrn:diseases:scc'
    >>> ssc.icd9Code
    '509.9'
    >>> ssc.icd10Code
    'C91-Q12'
    >>> ssc.affectedOrgans[0].title
    'Anus'


Vocabularies
------------

This package provides two vocabulary factories, one for available body
systems, and one for diseases.  Let's see if they produce reasonable values::

    >>> from zope.schema.interfaces import IVocabularyFactory
    >>> from zope.component import getUtility
    >>> v = getUtility(IVocabularyFactory, name='eke.knowledge.BodySystems')
    >>> type(v(portal))
    <class 'zope.schema.vocabulary.SimpleVocabulary'>
    >>> v = getUtility(IVocabularyFactory, name='eke.knowledge.Diseases')
    >>> type(v(portal))
    <class 'zope.schema.vocabulary.SimpleVocabulary'>


RDF Ingestion
-------------

Knowledge folders (and their children) support a URL-callable method that
causes them to

* Purge their existing content.
* Open a URL connection to their set RDF data source.
* Construct new content objects as described in the RDF.

The order of these operations isn't defined; different ingest handlers can do
it any way they want.

The basic knowledge folder supports reading only the most basic of knowledge
objects—knowledge objects, in fact!  In EKE, the basic knowledge object is the
most humble of resources, used to describe a single electronic resource with
basic Dublin Core metadata.

First, let's create a new, empty folder with which to play::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='knowledge-folder').click()
    >>> browser.getControl(name='title').value = u'Serious Business'
    >>> browser.getControl(name='rdfDataSource').value = u'testscheme://localhost/resources/a'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.open(portalURL + '/serious-business/content_status_modify?workflow_action=publish')
    >>> f = portal['serious-business']

Ingesting from the RDF data source ``testscheme://localhost/resources/a``::

    >>> browser.open(portalURL + '/serious-business/ingest')
    >>> browser.contents
    '...The following items have been created...A search engine...'
    >>> f.objectIds()
    ['http-google-com-1']
    >>> google = f['http-google-com-1']
    >>> google.title
    'A search engine'
    >>> google.identifier
    'http://google.com/'

The source ``testscheme://localhost/resources/b`` contains both Google *and*
Yahoo.  Since ingestion purges existing objects, we shouldn't get duplicate
copies of Google in the folder::

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/resources/b'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink('Ingest').click()
    >>> 'A search engine' in browser.contents and 'A web index' in browser.contents
    True
    >>> objIDs = f.objectIds()
    >>> objIDs.sort()
    >>> objIDs
    ['http-google-com-...', 'http-yahoo-com-...']

CA-450 complains that some resources aren't showing up for some biomarkers.
That's apparently due to the fact that many knowledge objects URIs were used
to generate their object IDs, and URIs that were URLs with a query component
got the rest of their ID chopped off.  For example, if two resources each had
the following URIs:

* http://www.genenames.org/data/hgnc_data.php?hgnc_id=6367
* http://www.genenames.org/data/hgnc_data.php?hgnc_id=6368

Then the object ID generated for *both* would be::

    http-www-genenames-org-data-hgnc_data-php-hgnc_id

That would result in the second one destroying the first, and biomarkers
unable to find their resources during biomarker ingest.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/resources/similar'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink('Ingest').click()
    >>> objIDs = f.objectIds()
    >>> len(objIDs)
    4
    >>> objIDs.sort()
    >>> objIDs
    ['http-google-com-...', 'http-www-genenames-org-data-hgnc_data-php-hgnc_id-...', 'http-www-genenames-org-data-hgnc_data-php-hgnc_id-...', 'http-yahoo-com-...']

Works fine!


Body Systems
~~~~~~~~~~~~

The basic knowledge folder can also ingest body systems from RDF::

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/bodysystems/a'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink('Ingest').click()
    >>> browser.contents
    '...The following items have been created...Anus...'
    >>> 'anus' in f.objectIds()
    True
    >>> anus.title
    'Anus'

A second ingest which has both "Anus" and "Rectum" in it should result in just
a single "Anus" in the folder; no duplicate anuses just like no duplicate
Googles::

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/bodysystems/b'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink('Ingest').click()
    >>> anuses = 0
    >>> for i in f.objectIds():
    ...     if i.startswith('anus'):
    ...         anuses += 1
    >>> anuses
    1
    >>> 'rectum' in f.objectIds()
    True


Diseases
~~~~~~~~

Likewise, diseases are importable from RDF::

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/diseases/a'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink('Ingest').click()
    >>> browser.contents
    '...The following items have been created...Anal seepage...'
    >>> 'anal-seepage' in f.objectIds()
    True
    >>> anal = f['anal-seepage']
    >>> anal.title
    'Anal seepage'
    >>> anal.description
    'Seepage of pus or mucus from the anus'
    >>> anal.icd9Code
    '204.9'
    >>> anal.icd10Code
    'C81-Q96'
    >>> anal.affectedOrgans[0].title
    'Anus'

A second ingest possessing both "Anal seepage" and "Rectocele" should result
in a single "Anal seepage"; no duplicate diseases should occur::

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/diseases/b'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink('Ingest').click()
    >>> seepages = 0
    >>> for i in f.objectIds():
    ...     if i.startswith('anal-seepage'):
    ...         seepages += 1
    >>> seepages
    1
    >>> 'rectocele' in f.objectIds()
    True


Metadata with Markup
~~~~~~~~~~~~~~~~~~~~

http://oodt.jpl.nasa.gov/jira/browse/CA-472 reveals that all literal data
coming from the DMCC RDF Server is not actually Unicode text, but is rather
HTML markup fragments, including metadata fields like titles.  Now, metadata
should be mere text, so we need to ensure that any markup gets stripped before
being inserted into metadata fields.  To test this, let's set up another RDF
data source (for diseases in this case) which has markup and ingest::

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/diseases/c'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink('Ingest').click()

Now, the ingested items should not have any markup in their titles::

    >>> browser.open(portalURL + '/serious-business/yummy-markup')
    >>> 'Yummy Markup' in browser.contents
    True
    >>> '<b>Yummy Markup</b>' not in browser.contents
    True
    >>> 'Look: no superscripts-or-subscripts here.' in browser.contents
    True
    >>> 'No <sup>superscripts</sup>-or-<sub>subscripts</sub> here.' not in browser.contents
    True


RDF Data Sources
~~~~~~~~~~~~~~~~

The URL to an RDF data source is nominally displayed on a knowledge folder::

    >>> browser.open(portalURL + '/serious-business')
    >>> browser.contents
    '...RDF Data Source...testscheme://localhost/diseases/c...'

That shows up because we're logged in as an administrator.  Mere mortals
shouldn't see that.  For one, it could confuse their tiny minds.  Secondly,
even if they did understand it, they could care less.  Let's see if the RDF
data source disappears for mere mortals::

    >>> unprivilegedBrowser.open(portalURL + '/serious-business')
    >>> 'RDF Data Source' not in unprivilegedBrowser.contents
    True

That's it!


.. References:
.. _EKE: http://cancer.jpl.nasa.gov/documents/applications/knowledge-environment
.. _RDF: http://w3.org/RDF/
.. _URI: http://w3.org/Addressing/
