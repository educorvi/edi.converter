# -*- coding: utf-8 -*-
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.navigation.navtree import NavtreeStrategyBase
from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy, DefaultNavtreeStrategy
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from base64 import encodestring
from plone import api as ploneapi
import sys
import re

def controlunicode(inputtxt):
    _illegal_unichrs = r'\x0b'
    return re.sub(_illegal_unichrs, '', inputtxt)


class RootFolder(BrowserView):
    """
       Objektliste der Ordner in der Ebene 0
       Eventuell muss die Behandlung des Members-Ordners noch implementiert werden.
    """

    def __call__(self):
        pcat = getToolByName(self.context, 'portal_catalog')
        path = '/'
        folder_path = '/'.join(self.context.getPhysicalPath())
        brains = pcat(path={'query': folder_path, 'depth': 1}, portal_type='Folder')
        objlist = []
        for i in brains:
            myobj = {}
            obj = i.getObject()
            try:
                txtfield = obj.getField('text')
                txt = txtfield.getRaw(obj).decode('utf-8')
                myobj['txt'] = txt
            except:
                myobj['txt'] = u''
            myobj['uid'] = obj.UID()
            myobj['id'] = obj.id
            myobj['parent'] = ""
            myobj['title'] = obj.title
            myobj['description'] = obj.description
            myobj['review_state'] = i.review_state
            myobj['localroles'] = obj.get_local_roles()
            try:
                if obj.__ac_local_roles_block__:
                    myobj['block_vererbung'] = True
                else:
                    myobj['block_vererbung'] = False
            except:
                myobj['block_vererbung'] = False
            defaultpage = obj.getDefaultPage()
            myobj['defaultpage'] = None
            if defaultpage:
               if hasattr(obj, defaultpage):
                   myobj['defaultpage'] = defaultpage
            myobj['creation_date'] = obj.created().strftime('%Y-%m-%dT%H:%M:%S')
            try:
                if obj.effective().strftime('%Y-%m-%dT%H:%M:%S') == '1969-12-30T23:00:00':
                    myobj['effective_date'] = None
                else:
                    myobj['effective_date'] = obj.effective().strftime('%Y-%m-%dT%H:%M:%S')
            except:
                print(obj.absolute_url())
            myobj['excludeFromNav'] = obj.exclude_from_nav
            myobj['creators'] = obj.creators
            myobj['contributors'] = obj.contributors
            myobj['rights'] = obj.rights
            objlist.append(myobj)
        return objlist


class DefaultPage(BrowserView):
    """
       Prueft ob im Original-Ordner eine Default-Page gesetzt war und liefert
       gegebenenfalls die ID der Default-Page zurueck
    """

    def __call__(self, objuid):
        ordner = self.context.reference_catalog.lookupObject(objuid)
        if ordner:
            if ordner.getDefaultPage():
                page = ordner.getDefaultPage()
                if hasattr(ordner, page):
                    return page
        return False


class FolderInfo(BrowserView):
    """
       Liefert die Informationen eines einzelnen Ordner Objekts.
    """

    def __call__(self):
        myobj = {}
        obj = self.context
        try:
	    txtfield = obj.getField('text')
	    txt = txtfield.getRaw(obj).decode('utf-8')
	    myobj['txt'] = txt
        except:
	    myobj['txt'] = u''
        myobj['uid'] = obj.UID()
        myobj['id'] = obj.id
        myobj['parent'] = obj.aq_inner.aq_parent.UID()
        myobj['title'] = obj.title
        myobj['description'] = obj.description
        # workflowTool = getToolByName(self.context, "portal_workflow")
        # status = workflowTool.getStatusOf("folder_workflow", obj)
        myobj['review_state'] = ploneapi.content.get_state(obj)#status.get('review_state')
        myobj['localroles'] = obj.get_local_roles()
        try:
            if obj.__ac_local_roles_block__:
                myobj['block_vererbung'] = True
            else:
                myobj['block_vererbung'] = False
        except:
	        myobj['block_vererbung'] = False
        defaultpage = obj.getDefaultPage()
        myobj['defaultpage'] = None
        if defaultpage:
            if hasattr(obj, defaultpage):
	            myobj['defaultpage'] = defaultpage
        myobj['creation_date'] = obj.created().strftime('%Y-%m-%dT%H:%M:%S')
        try:
            if obj.effective().strftime('%Y-%m-%dT%H:%M:%S') == '1969-12-30T23:00:00':
                myobj['effective_date'] = None
            else:
                myobj['effective_date'] = obj.effective().strftime('%Y-%m-%dT%H:%M:%S')
        except:
	        print(obj.absolute_url())
        myobj['excludeFromNav'] = obj.exclude_from_nav
        myobj['creators'] = obj.creators
        myobj['contributors'] = obj.contributors
        myobj['rights'] = obj.rights
        return myobj


class FileInfo(BrowserView):
    """
       Liefert die Informationen einer einzelnen Datei. Der Dateiinhalt wird mittels
       separatem Download-Request gelesen.
    """

    def __call__(self):
        myobj = {}
        obj = self.context
        myobj['uid'] = obj.UID()
        myobj['id'] = obj.id
        myobj['parent'] = obj.aq_inner.aq_parent.UID()
        myobj['title'] = obj.title
        myobj['description'] = obj.description
        workflowTool = getToolByName(self.context, "portal_workflow")
        status = workflowTool.getStatusOf("plone_workflow", obj)
        myobj['review_state'] = ploneapi.content.get_state(obj)#status.get('review_state')
        myobj['creation_date'] = obj.created().strftime('%Y-%m-%dT%H:%M:%S')
        try:
            if obj.effective().strftime('%Y-%m-%dT%H:%M:%S') == '1969-12-30T23:00:00':
                myobj['effective_date'] = None
            else:
                myobj['effective_date'] = obj.effective().strftime('%Y-%m-%dT%H:%M:%S')
        except:
	        print(obj.absolute_url())
        myobj['excludeFromNav'] = obj.exclude_from_nav
        myobj['creators'] = obj.creators
        myobj['contributors'] = obj.contributors
        myobj['rights'] = obj.rights
        myobj['filedata'] = obj.absolute_url()
        myobj['content_type'] = obj.content_type
        myobj['filename'] = obj.file.filename #obj.getFilename()
        return myobj

class ImageInfo(BrowserView):
    """
       Liefert die Informationen eines einzelnen Bildes. Der Bildinhalt wird mittels
       separatem Download-Request gelesen.
    """

    def __call__(self):
        myobj = {}
        obj = self.context
        myobj['uid'] = obj.UID()
        myobj['id'] = obj.id
        myobj['parent'] = obj.aq_inner.aq_parent.UID()
        myobj['title'] = obj.title
        myobj['description'] = obj.description
        workflowTool = getToolByName(self.context, "portal_workflow")
        status = workflowTool.getStatusOf("plone_workflow", obj)
        myobj['review_state'] = ploneapi.content.get_state(obj)#status.get('review_state')
        myobj['creation_date'] = obj.created().strftime('%Y-%m-%dT%H:%M:%S')
        try:
            if obj.effective().strftime('%Y-%m-%dT%H:%M:%S') == '1969-12-30T23:00:00':
                myobj['effective_date'] = None
            else:
                myobj['effective_date'] = obj.effective().strftime('%Y-%m-%dT%H:%M:%S')
        except:
	        print(obj.absolute_url())
        myobj['excludeFromNav'] = obj.exclude_from_nav
        myobj['creators'] = obj.creators
        myobj['contributors'] = obj.contributors
        myobj['rights'] = obj.rights
        myobj['filedata'] = obj.absolute_url()# + '/at_download/image'
        myobj['content_type'] = obj.content_type
        myobj['filename'] = obj.image.filename #obj.getFilename()
        return myobj

class DocumentInfo(BrowserView):
    """
       Liefert die Information eines einzelnen Dokuments
    """

    def __call__(self):
        myobj = {}
        obj = self.context
        myobj['uid'] = obj.UID()
        myobj['id'] = obj.id
        myobj['parent'] = obj.aq_inner.aq_parent.UID()
        myobj['title'] = controlunicode(obj.title)
        myobj['description'] = obj.description
        workflowTool = getToolByName(self.context, "portal_workflow")
        status = workflowTool.getStatusOf("plone_workflow", obj)
        myobj['review_state'] = ploneapi.content.get_state(obj)#status.get('review_state')
        try:
            myobj['creation_date'] = obj.created().strftime('%Y-%m-%dT%H:%M:%S')
        except:
            myobj['creation_date'] = '2020-01-31T12:00:00'
        try:
            if obj.effective().strftime('%Y-%m-%dT%H:%M:%S') == '1969-12-30T23:00:00':
                myobj['effective_date'] = None
            else:
                myobj['effective_date'] = obj.effective().strftime('%Y-%m-%dT%H:%M:%S')
        except:
	        print(obj.absolute_url())
        myobj['excludeFromNav'] = obj.exclude_from_nav
        myobj['creators'] = obj.creators
        myobj['contributors'] = obj.contributors
        myobj['rights'] = obj.rights
        try:
            rawtext = obj.text.raw #obj.getRawText()
            rawtext = rawtext.replace('/image_large', '/@@images/image/large')
            rawtext = rawtext.replace('/image_preview', '/@@images/image/preview')
            rawtext = rawtext.replace('/image_mini', '/@@images/image/mini')
            rawtext = rawtext.replace('/image_thumb', '/@@images/image/thumb')
            rawtext = rawtext.replace('/image_tile', '/@@images/image/tile')
            rawtext = rawtext.replace('/image_icon', '/@@images/image/icon')
            rawtext = rawtext.replace('/image_listing', '/@@images/image/listing')
            myobj['txt'] = rawtext
        except:
            myobj['txt'] = ""
        return myobj

class NewsInfo(BrowserView):
    """
       Liefert die Informationen einer einzelnen Nachricht. Das Bild zur Nachricht
       wird mit einem separaten Download-Request gelesen.
    """

    def __call__(self):
        myobj = {}
        obj = self.context
        myobj['uid'] = obj.UID()
        myobj['id'] = obj.id
        myobj['parent'] = obj.aq_inner.aq_parent.UID()
        myobj['title'] = obj.title
        myobj['description'] = obj.description
        workflowTool = getToolByName(self.context, "portal_workflow")
        status = workflowTool.getStatusOf("plone_workflow", obj)
        myobj['review_state'] = ploneapi.content.get_state(obj)#status.get('review_state')
        try:
            myobj['creation_date'] = obj.created().strftime('%Y-%m-%dT%H:%M:%S')
        except:
            myobj['creation_date'] = '2020-01-31T12:00:00'
        try:
            if obj.effective().strftime('%Y-%m-%dT%H:%M:%S') == '1969-12-30T23:00:00':
                myobj['effective_date'] = None
            else:
                myobj['effective_date'] = obj.effective().strftime('%Y-%m-%dT%H:%M:%S')
        except:
	        print(obj.absolute_url())
        myobj['excludeFromNav'] = obj.exclude_from_nav
        myobj['creators'] = obj.creators
        myobj['contributors'] = obj.contributors
        myobj['rights'] = obj.rights
        myobj['filedata'] = ''
        if obj.image:
            myobj['filedata'] = obj.absolute_url()# + '/at_download/image'
            myobj['filename'] = obj.image.filename #obj.getFilename()
        myobj['content_type'] = obj.content_type
        try:
            rawtext = obj.text.raw #obj.getRawText()
            rawtext = rawtext.replace('/image_large', '/@@images/image/large')
            rawtext = rawtext.replace('/image_preview', '/@@images/image/preview')
            rawtext = rawtext.replace('/image_mini', '/@@images/image/mini')
            rawtext = rawtext.replace('/image_thumb', '/@@images/image/thumb')
            rawtext = rawtext.replace('/image_tile', '/@@images/image/tile')
            rawtext = rawtext.replace('/image_icon', '/@@images/image/icon')
            rawtext = rawtext.replace('/image_listing', '/@@images/image/listing')
            myobj['txt'] = rawtext
        except:
            myobj['txt'] = ""
        return myobj


class LinkInfo(BrowserView):
    """
       Liefert die Informationen eines einzelnen Links.
    """

    def __call__(self):
        myobj = {}
        obj = self.context
        myobj['uid'] = obj.UID()
        myobj['id'] = obj.id
        myobj['parent'] = obj.aq_inner.aq_parent.UID()
        myobj['title'] = obj.title
        myobj['description'] = obj.description
        workflowTool = getToolByName(self.context, "portal_workflow")
        status = workflowTool.getStatusOf("plone_workflow", obj)
        myobj['review_state'] = ploneapi.content.get_state(obj)#status.get('review_state')
        try:
            myobj['creation_date'] = obj.created().strftime('%Y-%m-%dT%H:%M:%S')
        except:
            myobj['creation_date'] = u'2020-01-31T12:00:00'
        try:
            if obj.effective().strftime('%Y-%m-%dT%H:%M:%S') == '1969-12-30T23:00:00':
                myobj['effective_date'] = None
            else:
                myobj['effective_date'] = obj.effective().strftime('%Y-%m-%dT%H:%M:%S')
        except:
	        print(obj.absolute_url())
        myobj['excludeFromNav'] = obj.exclude_from_nav
        myobj['creators'] = obj.creators
        myobj['contributors'] = obj.contributors
        myobj['rights'] = obj.rights
        myobj['remoteUrl'] = obj.remoteUrl #obj.getRemoteUrl()
        return myobj

class StammblattInfo(BrowserView):
    """
       Liefert die Informationen einer einzelnen Stammblatts. Der Dateiinhalt wird mittels
       separatem Download-Request gelesen.
    """

    def __call__(self):
        myobj = {}
        obj = self.context
        myobj['uid'] = obj.UID()
        myobj['id'] = obj.id
        myobj['parent'] = obj.aq_inner.aq_parent.UID()
        myobj['title'] = obj.title
        myobj['description'] = obj.description
        workflowTool = getToolByName(self.context, "portal_workflow")
        status = workflowTool.getStatusOf("plone_workflow", obj)
        myobj['review_state'] = ploneapi.content.get_state(obj)#status.get('review_state')
        myobj['creation_date'] = obj.created().strftime('%Y-%m-%dT%H:%M:%S')
        try:
            if obj.effective().strftime('%Y-%m-%dT%H:%M:%S') == '1969-12-30T23:00:00':
                myobj['effective_date'] = None
            else:
                myobj['effective_date'] = obj.effective().strftime('%Y-%m-%dT%H:%M:%S')
        except:
	        print(obj.absolute_url())
        myobj['excludeFromNav'] = obj.exclude_from_nav
        myobj['creators'] = obj.creators
        myobj['contributors'] = obj.contributors
        myobj['rights'] = obj.rights
        myobj['filedata'] = obj.absolute_url()
        myobj['content_type'] = obj.content_type
        try:
            myobj['ziele'] = obj.ziele.raw
        except:
            myobj['ziele'] = " "
        try:
            myobj['verantwortung'] = obj.verantwortung
        except:
            myobj['verantwortung'] = " "
        try:
            myobj['steuerung'] = obj.steuerung
        except:
            myobj['steuerung'] = " "
        try:
            myobj['anstoss'] = obj.anstoss
        except:
            myobj['anstoss'] = " "
        try:
            myobj['eingaben'] = obj.eingaben
        except:
            myobj['eingaben'] = " "
        try:
            myobj['ergebnisse'] = obj.ergebnisse.raw
        except:
            myobj['ergebnisse'] = " "
        try:
            myobj['kennzahlen'] = obj.kennzahlen.raw
        except:
            myobj['kennzahlen'] = " "
        try:
            myobj['grundlagen'] = obj.grundlagen.raw
        except:
            myobj['grundlagen'] = " "
        try:
            myobj['dokumente'] = obj.dokumente.raw
        except:
            myobj['dokumente'] = " "
        try:
            myobj['formulare'] = obj.formulare.raw
        except:
            myobj['formulare'] = " "
        try:
            myobj['risikobewertung'] = obj.risikobewertung.raw
        except:
            myobj['risikobewertung'] = " "
        
        return myobj


class KollektionInfo(BrowserView):
    """
       Liefert die Informationen einer einzelnen Kollektion.
    """

    def __call__(self):
        myobj = {}
        obj = self.context
        myobj['uid'] = obj.UID()
        myobj['id'] = obj.id
        myobj['parent'] = obj.aq_inner.aq_parent.UID()
        myobj['title'] = obj.title
        myobj['description'] = obj.description
        myobj['review_state'] = ploneapi.content.get_state(obj)#status.get('review_state')
        try:
            myobj['creation_date'] = obj.created().strftime('%Y-%m-%dT%H:%M:%S')
        except:
            myobj['creation_date'] = u'2020-01-31T12:00:00'
        try:
            if obj.effective().strftime('%Y-%m-%dT%H:%M:%S') == '1969-12-30T23:00:00':
                myobj['effective_date'] = None
            else:
                myobj['effective_date'] = obj.effective().strftime('%Y-%m-%dT%H:%M:%S')
        except:
	        print(obj.absolute_url())
        myobj['excludeFromNav'] = obj.exclude_from_nav
        myobj['creators'] = obj.creators
        myobj['contributors'] = obj.contributors
        myobj['rights'] = obj.rights
        myobj['sort_on'] = obj.sort_on
        myobj['customViewFields'] = obj.customViewFields
        myobj['at_references'] = obj.at_references
        myobj['sort_reversed'] = obj.sort_reversed
        myobj['query'] = obj.query
        try:
            myobj['txt'] = obj.text.raw
        except:
            pass
        return myobj

class FunktionsgruppenInfo(BrowserView):
    """
       Liefert die Informationen einer einzelnen Funktionsgruppe.
    """

    def __call__(self):
        myobj = {}
        obj = self.context
        myobj['uid'] = obj.UID()
        myobj['id'] = obj.id
        myobj['parent'] = obj.aq_inner.aq_parent.UID()
        myobj['title'] = obj.title
        myobj['description'] = obj.description
        myobj['review_state'] = ploneapi.content.get_state(obj)#status.get('review_state')
        try:
            myobj['creation_date'] = obj.created().strftime('%Y-%m-%dT%H:%M:%S')
        except:
            myobj['creation_date'] = u'2020-01-31T12:00:00'
        try:
            if obj.effective().strftime('%Y-%m-%dT%H:%M:%S') == '1969-12-30T23:00:00':
                myobj['effective_date'] = None
            else:
                myobj['effective_date'] = obj.effective().strftime('%Y-%m-%dT%H:%M:%S')
        except:
	        print(obj.absolute_url())
        myobj['excludeFromNav'] = obj.exclude_from_nav
        myobj['creators'] = obj.creators
        myobj['contributors'] = obj.contributors
        myobj['rights'] = obj.rights
        myobj['groupmembers'] = obj.groupmembers
        try:
            myobj['txt'] = obj.text.raw
        except:
            pass
        return myobj


## Die folgenden Views liefern Objektlisten mit URLs an die Gegenseite ##

URL = '/bghwintranet/'

class Filebuilder(BrowserView):

    def __call__(self):
        pfad = URL + '%s' %self.context.id
        pcat = getToolByName(self.context, 'portal_catalog')
        brains = pcat(portal_type='File', path=pfad)
        print(len(brains))
        idlist = []
        for i in brains:
            idlist.append(i.getURL())
        return idlist

class Imagebuilder(BrowserView):

    def __call__(self):
        pfad = URL + '%s' %self.context.id
        pcat = getToolByName(self.context, 'portal_catalog')
        brains = pcat(portal_type='Image', path=pfad)
        print(len(brains))
        idlist = []
        for i in brains:
            idlist.append(i.getURL())
        return idlist

class Documentbuilder(BrowserView):

    def __call__(self):
        pfad = URL + '%s' %self.context.id
        pcat = getToolByName(self.context, 'portal_catalog')
        brains = pcat(portal_type='Document', path=pfad)
        print(len(brains))
        idlist = []
        for i in brains:
            idlist.append(i.getURL())
        return idlist

class Newsbuilder(BrowserView):

    def __call__(self):
        pfad = URL + '%s' %self.context.id
        pcat = getToolByName(self.context, 'portal_catalog')
        brains = pcat(portal_type='News Item', path=pfad)
        print(len(brains))
        idlist = []
        for i in brains:
            idlist.append(i.getURL())
        return idlist

class Linkbuilder(BrowserView):

    def __call__(self):
        pfad = URL + '%s' %self.context.id
        pcat = getToolByName(self.context, 'portal_catalog')
        brains = pcat(portal_type='Link', path=pfad)
        print(len(brains))
        idlist = []
        for i in brains:
            idlist.append(i.getURL())
        return idlist

class Stammblattbuilder(BrowserView):

    def __call__(self):
        pfad = URL + '%s' %self.context.id
        pcat = getToolByName(self.context, 'portal_catalog')
        brains = pcat(portal_type='Stammblatt', path=pfad)
        print(len(brains))
        idlist = []
        for i in brains:
            idlist.append(i.getURL())
        return idlist

class Kollektionsbuilder(BrowserView):

    def __call__(self):
        pfad = URL + '%s' %self.context.id
        pcat = getToolByName(self.context, 'portal_catalog')
        brains = pcat(portal_type='Collection', path=pfad)
        print(len(brains))
        idlist = []
        for i in brains:
            idlist.append(i.getURL())
        return idlist
    
class Funktionsgruppenbuilder(BrowserView):

    def __call__(self):
        pfad = URL + '%s' %self.context.id
        pcat = getToolByName(self.context, 'portal_catalog')
        brains = pcat(portal_type='Funktionsgruppe', path=pfad)
        print(len(brains))
        idlist = []
        for i in brains:
            idlist.append(i.getURL())
        return idlist


class Treebuilder(BrowserView):

    def __call__(self):
        query = {'portal_type':'Folder'}
        #portal_url = getToolByName(self.context, "portal_url")
        #rootobj = portal_url.getPortalObject()
        rootobj = self.context
        tree = query_items_in_natural_sort_order(rootobj, query)
        print(len(tree))
        idlist = []
        for i in tree:
            idlist.append(i.getURL())
        return idlist

def query_items_in_natural_sort_order(root, query):
    """
    Create a flattened out list of portal_catalog queried items in their natural depth first navigation order.

    @param root: Content item which acts as a navigation root

    @param query: Dictionary of portal_catalog query parameters

    @return: List of catalog brains
    """

    # Navigation tree base portal_catalog query parameters
    applied_query=  {
        'path' : '/'.join(root.getPhysicalPath()),
        'sort_on' : 'getObjPositionInParent'
    }

    # Apply caller's filters
    applied_query.update(query)

    # Set the navigation tree build strategy
    # - use navigation portlet strategy as base
    #strategy = DefaultNavtreeStrategy(root)
    strategy = NavtreeStrategyBase()
    strategy.rootPath = '/'.join(root.getPhysicalPath())
    strategy.showAllParents = False
    strategy.bottomLevel = 999
    # This will yield out tree of nested dicts of
    # item brains with retrofitted navigational data
    tree = buildFolderTree(root, root, query, strategy=strategy)

    items = []

    def flatten(children):
        """ Recursively flatten the tree """
        for c in children:
            # Copy catalog brain object into the result
            items.append(c["item"])
            children = c.get("children", None)
            if children:
                flatten(children)

    flatten(tree["children"])

    return items

