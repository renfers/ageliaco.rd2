# -*- coding: UTF-8 -*-
from five import grok
from zope import schema

from plone.directives import form, dexterity
from zope.app.container.interfaces import IObjectAddedEvent

from plone.z3cform.textlines import TextLinesFieldWidget

from zope.interface import invariant, Invalid

from interface import IProjet

from plone.app.textfield.value import RichTextValue
from DateTime import DateTime
from plone.indexer import indexer
import datetime

from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage

from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from zope.security import checkPermission
from zope.app.content import queryContentType
from zope.schema import getFieldsInOrder
from plone.dexterity.interfaces import IDexterityFTI 
from zope.component import queryUtility
 
from cycle import ICycle
from auteur import IAuteur

from ageliaco.rd2 import _

import pdb
    
@grok.subscribe(IProjet, IObjectAddedEvent)
def setRealisation(projet, event):
    admid = 'realisation'
    try:
        cycles = projet[admid]
    except KeyError: 
        rea = projet.invokeFactory("Folder", id=admid, title=u'Réalisation')
        #projet[admid] = rea
    
    #projet.setContributors(projet.contributor)
    #request.response.redirect(cycles.absolute_url() + '++add++ageliaco.rd2.cycle')
    return #request.response.redirect(cycles.absolute_url() + '++add++ageliaco.rd2.cycle')
    
@indexer(IProjet)
def searchableIndexer(context):
    keywords = " ".join(context.keywords)
    return "%s %s %s %s" % (context.title, context.description, context.presentation, keywords)

grok.global_adapter(searchableIndexer, name="SearchableText")

    


class View(grok.View):
    grok.context(IProjet)
    grok.require('zope2.View')
    
    def canRequestReview(self):
        return checkPermission('cmf.RequestReview', self.context)

    def logo_url(self):
        context = aq_inner(self.context)
        portal_url = getToolByName(context, 'portal_url')
        if 'logo.png' in context.keys():
            return context.absolute_url() + '/logo.png'
        return portal_url + '/++resource++ageliaco.rd/screens.png'      

    def noCycle(self):
        context = aq_inner(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        cat = catalog(object_provides= ICycle.__identifier__,
                   path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
                   sort_on="modified", sort_order="reverse")     
        if len(cat)>0:
            return False
        return True
        
    def new_cycle_url(self):
        context = aq_inner(self.context)
        admid = 'admin_' + context.id 
        url = context.absolute_url() + '/' + admid + '/++add++ageliaco.rd.cycle'
        return url 
        
    def cycles(self):
        """Return a catalog search result of issues to show
        """
        
        context = aq_inner(self.context)
        #catalog = getToolByName(self.context, 'portal_catalog')
        #object = context
        #return catalog(object_provides= ICycle.__identifier__,
        #               path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
        #               sort_on="modified", sort_order="reverse")        
        admin = 'admin_' + context.id
        if admin in context.objectIds():
            administration = context[admin]
            return administration.objectValues()
        return []

    def canAddContent(self):
        return checkPermission('cmf.AddPortalContent', self.context)
        
    def canModifyContent(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)
        
        
    def cycles_obj(self):
        #return a list of actual cycle objects
        context = aq_inner(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        cat = catalog(object_provides= ICycle.__identifier__,
                   path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
                   sort_on="modified", sort_order="reverse")     
        return cat
        
    def review_state(self):
        context = aq_inner(self.context)
        portal_workflow = getToolByName(context, 'portal_workflow')
        review_state = portal_workflow.getInfoFor(context, 'review_state')
        return review_state
        
    def isRepository(self):
        context = aq_inner(self.context)
        portal_workflow = getToolByName(context, 'portal_workflow')
        review_state = portal_workflow.getInfoFor(context, 'review_state')
        return review_state == u'repository'
        

    def contributeurs(self,cycle_id):
        context = aq_inner(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        if cycle_id in context.keys():
            cycle = context[cycle_id]  
            if cycle:
                cat = catalog(object_provides= IAuteur.__identifier__,
                           path={'query': '/'.join(cycle.getPhysicalPath()), 'depth': 1},
                           sort_on="modified", sort_order="reverse")     
                return cat
        return None
    
    def hasRealisation(self):
        context = aq_inner(self.context)
        if not context.has_key('realisation'):
            return ""
        if len(context['realisation'].keys()):
            return context['realisation'].absolute_url()
        return ""
    
    
    def hasLink(self):
        context = aq_inner(self.context)
        #pdb.set_trace()
        
        if getattr(context,'lien',0):
            print context.getAttribute('lien')
            return context.lien
        else:
            print "no Property 'link'"
        return ''
    

#     def cycles(self):
#         #return a list with all the cycles for this projet
#         context = aq_inner(self.context)
#         catalog = getToolByName(self.context, 'portal_catalog')
#         try:
#             objet = context['admin_' + context.id]
#             return catalog(object_provides= ICycle.__identifier__,
#                            path={'query': object.absolute_url(), 'depth': 1},
#                            sort_on="modified", sort_order="reverse")        
#             
#         except:
#             return []
#         #log( 'cycle : ' + object.getPath())
#         #log( wf_state + " state chosen")
