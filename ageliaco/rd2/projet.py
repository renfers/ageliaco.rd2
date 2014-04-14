# -*- coding: UTF-8 -*-
from five import grok
from zope import schema

from Products.ATContentTypes.lib import constraintypes
from Products.Five import BrowserView
from plone.directives import form, dexterity
from zope.app.container.interfaces import IObjectAddedEvent

from plone.z3cform.textlines import TextLinesFieldWidget

from zope.interface import invariant, Invalid

from interface import IProjet,IAuteur,ICycle,idDefaultFromContext,InterfaceView
from note import INote

import yafowil.plone
import yafowil.loader
from yafowil.base import factory, UNSET, ExtractionError
from yafowil.controller import Controller
from yafowil.plone.form import Form
#from yafowil.widget.richtext import richtext
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.dexterity.utils import createContentInContainer
from zope.schema.vocabulary import SimpleVocabulary
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
from z3c.form import button, field
from interface import InterfaceView
from plone.memoize import view
 
from ageliaco.rd2 import MessageFactory
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
_ = MessageFactory

import ast

@grok.subscribe(IProjet, IObjectAddedEvent)
def setRealisation(projet, event):
    admid = 'realisation'
    try:
        cycles = projet[admid]
    except KeyError: 
        rea = projet.invokeFactory("Folder", id=admid, title=u'Réalisation')
        #projet[admid] = rea
        rea.setConstrainTypesMode(constraintypes.ENABLED)
        rea.setLocallyAllowedTypes(
            ["File","Folder","Image","Document","Link"]
            )
        rea.setImmediatelyAddableTypes(
            ["File","Folder","Image","Document","Link"]
            )
    
    return 
#request.response.redirect(cycles.absolute_url() + '++add++ageliaco.rd2.cycle')
    
@indexer(IProjet)
def searchableIndexer(context):
    keywords = " ".join(context.keywords)
    return "%s %s %s %s" % (context.title, 
                context.description, context.presentation, keywords)

grok.global_adapter(searchableIndexer, name="SearchableText")

    

def richtext():
    part = factory(u'fieldset', name='yafowilwidgetrichtext')
    part['richtext'] = factory('#field:richtext', props={
        'label': 'Richtext field',
        'required': 'Text is required'})
    return {'widget': part,
            'doc': "Doc",
            'title': 'Richtext'}

class EditForm(dexterity.EditForm):
    grok.context(IProjet)
    #grok.layer(ILayer)
    grok.name('edit')

    label = _(u"Editer la présentation du projet")
    description = _(u"Make your changes below.")

class View(InterfaceView):
    grok.context(IProjet)
    grok.require('zope2.View')
    grok.name('view')
    template = ViewPageTemplateFile('projet_templates/view.pt')

    #     def __call__(self):
    #         return self.view_template()
        
    def activeProjets(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        cat = catalog(portal_type='ageliaco.rd2.projet',
                       review_state='encours',
                       sort_on='sortable_title')
        #log('catalogue : %s items'%len(cat))
    
        terms = [('',''),]
                    
        for brain in cat:
            terms.append((brain.getPath(),brain.Title))
        return terms 
    
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
                   path={'query': '/'.join(context.getPhysicalPath()), 
                         'depth': 1
                        },
                   sort_on="modified", sort_order="reverse")     
        if len(cat)>0:
            return False
        return True
        

    #     def auteur_disciplines(self,auteur):
    #         if hasattr(auteur,'disciplines'):
    #             return auteur.disciplines
    #         return ""
    
    def isRepository(self):
        context = aq_inner(self.context)
        portal_workflow = getToolByName(context, 'portal_workflow')
        review_state = portal_workflow.getInfoFor(context, 'review_state')
        return review_state == u'repository'
        
    
    def hasRealisation(self):
        context = aq_inner(self.context)
        if not context.has_key('realisation'):
            return ""
        if len(context['realisation'].keys()) or \
                self.canAddContent(context['realisation']):
            return context['realisation'].absolute_url()
        return ""
    
    
    def hasLink(self):
        context = aq_inner(self.context)
        #pdb.set_trace()
        
        if getattr(context,'lien',0):
            #print context.getAttribute('lien')
            return context.lien
        #         else:
        #             print "no Property 'link'"
        return ''

    
class CyclesView(InterfaceView):
    grok.context(IProjet)
    grok.require('zope2.View')
    grok.name('cyclesview')
    pass

class CyclesAuteursTableView(InterfaceView):
    grok.context(IProjet)
    grok.require('zope2.View')
    grok.name('cycles_auteurs_tableview')
    #cycles_auteurs_table_template = ViewPageTemplateFile('projet_templates/cycles_auteurs_table.pt')

    pass
