# -*- coding: UTF-8 -*-
from five import grok
from zope import schema

from Products.ATContentTypes.lib import constraintypes

from plone.directives import form, dexterity
from zope.app.container.interfaces import IObjectAddedEvent

from plone.z3cform.textlines import TextLinesFieldWidget

from zope.interface import invariant, Invalid

from interface import IProjet


import yafowil.plone
import yafowil.loader
from yafowil.base import factory, UNSET, ExtractionError
from yafowil.controller import Controller
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
        rea.setConstrainTypesMode(constraintypes.ENABLED)
        rea.setLocallyAllowedTypes(["File","Folder","Image","Document","Link"])
        rea.setImmediatelyAddableTypes(["File","Folder","Image","Document","Link"])
    
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
    next = ''
    nextId = ''
    def formnext(self, request):
        print "next : ", self.next
        #import pdb; pdb.set_trace()
        if not self.next:
            if self.nextId:
                cycle =  aq_inner(self.context)[self.nextId]
                return cycle.absolute_url() + '/edit'
        return self.next
    def _form_action(self, widget, data):
        context = aq_inner(self.context)
        
        print '%s/%s/edit' % (context.absolute_url(),self.nextId)
        self.next = '%s/%s/edit' % (context.absolute_url(),self.nextId)
        #import pdb; pdb.set_trace()

        return '%s/%s/edit' % (context.absolute_url(),self.nextId)
        
        
    def _form_action2(self, widget, data):
        if not hasattr(self,'projet') or not self.projet:
            error = ExtractionError(
                'Choisissez un projet dans la liste!')
            return self.context.absolute_url()
        context = aq_inner(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        cat = catalog(object_provides= ICycle.__identifier__,
                   path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
                   sort_on="modified", sort_order="reverse")  
        print "cat len = ", len(cat), cat
        cycleId = "%s-%i" % (context.start,(len(cat)+1))
        item = createContentInContainer(context, "ageliaco.rd2.cycle", id=cycleId, title=self.projet)
        
        print '%s/%s/edit' % (context.absolute_url(),cycleId)
        self.next = '%s/%s/edit' % (context.absolute_url(),cycleId)
        return '%s/%s/edit' % (context.absolute_url(),cycleId)

    def _form_handler(self, widget, data):
        #import pdb; pdb.set_trace()
        self.newprojet = data['newprojet'].extracted
        if not hasattr(self,'newprojet') or not self.newprojet:
            error = ExtractionError(
                'Complétez le titre du projet!')
            return self.context.absolute_url()
        context = aq_inner(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        cat = catalog(object_provides= ICycle.__identifier__,
                   path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
                   sort_on="modified", sort_order="reverse")  
        print "cat len = ", len(cat), cat
        cycleId = "%s-%i" % (context.start,(len(cat)+1))
        item = createContentInContainer(context, "ageliaco.rd2.cycle", id=cycleId, title=self.newprojet)
        self.nextId = cycleId
        self.next = item.absolute_url() + '/edit'
        self.form['submit'].props['next'] = self.next

        return self.newprojet
        
    def _form_handler2(self, widget, data):
        self.projet = data['projet'].extracted

    def form(self):
        form = factory('form',
            name='newproject',
            props={
                'action': self._form_action,
                'structural': True,
            })

        form['newprojet'] = factory(
            'field:label:error:text',
            props={
                'label': _(u'Titre du nouveau projet : '),
                'field.class': 'field',
                'text.class': 'text',
                'size': '80',
        })
        form['submit'] = factory(
            'field:submit',
            props={
                'label': _(u'Déposer un nouveau projet'),
                'submit.class': '',
                'handler': self._form_handler,
                'action': 'newproject',
        })

        controller = Controller(form, self.request)
        return controller.rendered
    def form2(self):
        form2 = factory('form',
            name='depot1form2',
            props={
                'action': self._form_action2,
            })

        form2['projet'] = factory(
            'field:label:error:select',
            props={
                'label': _(u'Reconduire le projet suivant : '),
                'field.class': 'field',
                'select.class': 'select',
                'vocabulary': self.activeProjets,
        })
        form2['submit'] = factory(
            'field:submit',
            props={
                'label': _(u'Reconduire le projet existant'),
                'submit.class': '',
                'handler': self._form_handler2,
                'action': 'newCycle',
                'next': self.formnext,
        })

        controller = Controller(form2, self.request)
        return controller.rendered
        
    def formResult(self):
        if not hasattr(self,'newprojet') or not self.newprojet:
            return ''
        return self.newprojet
        
    def form2Result(self):
        if not hasattr(self,'projet') or not self.projet:
            return ''
        return self.projet
        
        
    def activeProjets(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        cat = catalog(portal_type='ageliaco.rd2.projet',
                       review_state='encours',
                       sort_on='sortable_title')
        #log('catalogue : %s items'%len(cat))
    
        terms = [('',''),]
                    
        for brain in cat:
            print dir(brain)
            print "getURL : %s => getPath : %s " % (brain.getURL(),brain.getPath())
            terms.append((brain.getPath(),brain.Title))
        return terms #SimpleVocabulary([SimpleVocabulary.createTerm(x.id, x.getURL(), x.Title) for x in cat])
    
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
    
