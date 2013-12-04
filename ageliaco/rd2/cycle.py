# -*- coding: UTF-8 -*-
import os.path
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserRequest
from five import grok
from zope import schema
from plone.namedfile import field as namedfile
from z3c.relationfield.schema import RelationChoice, RelationList
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.dexterity.browser.add import DefaultAddView, DefaultAddForm
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.browser.view import DefaultView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import plone.dexterity.browser

import yafowil.plone
import yafowil.loader
from yafowil.base import factory, UNSET, ExtractionError
from yafowil.controller import Controller
from yafowil.plone.form import Form


from plone.directives import form, dexterity
from plone.app.textfield import RichText
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.indexer import indexer

from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.schema.fieldproperty import FieldProperty

from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow

import datetime

import z3c.form
# for debug purpose => log(...)
from Products.CMFPlone.utils import log


from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.app.container.interfaces import IObjectAddedEvent
from Products.CMFCore.utils import getToolByName
from plone.z3cform.textlines.textlines import TextLinesFieldWidget

from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget
from zope.interface import invariant, Invalid, Interface

from Acquisition import aq_inner, aq_parent
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot
from zope.security import checkPermission

from ageliaco.rd2 import MessageFactory

#from projet import IProjet
from interface import ICycle, IAuteur, InterfaceView

_ = MessageFactory

        
class View(InterfaceView, dexterity.DisplayForm):
    grok.context(ICycle)
    grok.require('zope2.View')
    grok.name('view')

    def isDraft(self):
        context = aq_inner(self.context)
        portal_workflow = getToolByName(context, 'portal_workflow')
        review_state = portal_workflow.getInfoFor(context, 'review_state')
        return review_state == 'draft'
        
    def isList(self,fieldname):
        context = aq_inner(self.context)
        data = None
        try:
            data = getattr(context,fieldname,None)
        except:
            return False
        if data:
            return type(data)== list
        return False
    
        return year < 2014 and month < 9
    def isOldCycle(self):
        context = aq_inner(self.context)
        date = context.CreationDate()
        year = date.split('-')[0]
        month = date.split('-')[1]
        date = year+month
        return int(date) < 201310
        
    def auteurs(self):
        context = aq_inner(self.context)
        
        catalog = getToolByName(self.context, 'portal_catalog')
        log( 'context path : ' + context.absolute_url())
        
        return catalog(object_provides=[IAuteur.__identifier__],
                path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
                sort_on='sortable_title'
                )                

    def delAuteur(self,auteur):
        context = aq_inner(self.context)
        if auteur in context.keys():
            del context[auteur]
        return context.absolute_url()
    
    def parent_url(self):
        context = aq_inner(self.context)
        parent = context.aq_parent
        #print parent.absolute_url()
        return parent.absolute_url()


    def cycle_url(self):
        context = aq_inner(self.context)
        #print context.absolute_url()
        return context.absolute_url()
    

    def contributeur(self,auteur):
        context = aq_inner(self.context)
        
        if auteur in context.keys():
            return context[auteur]
        return None
    
    def projet(self,url):
        context = aq_inner(self.context)
        
        catalog = getToolByName(self.context, 'portal_catalog')
        
        cat = catalog(portal_type='ageliaco.rd2.projet',
                    review_state='encours',
                    path={'query': '/'.join(url.split('/')[:-1]), 'depth': 1},
                    id=url.split('/')[-1])    
        if len(cat)==0:
            return ""
        obj = cat[0].getObject()
        return obj.title            
        
    
@indexer(ICycle)
def searchableIndexer(context):
    try:
        retour = u""
        all = (
                context.id,
                context.title, 
                context.description, 
                context.projet,
                context.domaine,
                context.discipline,
                context.problematique, 
                context.presentation,
                context.experiences,
                context.besoin,
                context.cible,
                context.pro,
                context.forme,
                context.planification,
                context.plan,
                context.repartition,
                context.modalites,
                context.participants,
                context.porteparole,
                )
        for elem in all:
            retour += u" %s" % elem
        return retour
            
    except:
        log( 'tOO BAD an INDEX (bad cycle) : ' + context.absolute_url())
        return u""        
grok.global_adapter(searchableIndexer, name="SearchableText")


@indexer(ICycle)
def authorsIndexer(obj):
    return obj.contributor
grok.global_adapter(authorsIndexer, name="authors")

@indexer(ICycle)
def supervisorIndexer(obj):
    return obj.supervisor
grok.global_adapter(supervisorIndexer, name="supervisor")

class ILayer(IDefaultBrowserLayer):
    pass

class EditForm(dexterity.EditForm):
    grok.context(ICycle)
    grok.layer(ILayer)
    grok.name('edit')

    label = _(u"Proposer un projet")
    description = _(u"Make your changes below.")

