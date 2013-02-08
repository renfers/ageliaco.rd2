# -*- coding: UTF-8 -*-
from five import grok
from zope import schema

from plone.directives import form, dexterity
from z3c.form import field, button

#from cycle import Projet

from ageliaco.rd2 import _

# for debug purpose => log(...)
from Products.CMFPlone.utils import log

from interface import IProjet, ICycle, IAuteur, InterfaceView

from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName

from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget, AutocompleteFieldWidget
from zope.interface import invariant, Invalid

from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName

from plone.app.textfield import RichText

#from collective.gtags.field import Tags

from Products.CMFCore.interfaces import IFolderish
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView

#from zope.app.pagetemplate import ViewPageTemplateFile
from plone.app.layout.viewlets.interfaces import IAboveContent

import datetime

from zope.component import getMultiAdapter

from zope.app.component.hooks import setHooks, setSite, getSite


import yafowil.plone
import yafowil.loader
from yafowil.base import factory, UNSET, ExtractionError
from yafowil.controller import Controller
from yafowil.plone.form import Form
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from interface import ICycle, IAuteur, InterfaceView


# def getView(context, request, name):
#     # Remove acquisition wrapper which may cause false context assumptions
#     context = aq_inner(context)
#     # Will raise ComponentLookUpError
#     view = getMultiAdapter((context, request), name=name)
#     # Put view to acquisition chain
#     view.context = context
#     view.request = request
#     return view
    
class IProjets(form.Schema):
    """
    Projets de Projet RD
    """
    presentation = RichText(
            title=_(u"Projets R&D"),
            required=True,
        )    



    
        
class View(InterfaceView):
    grok.context(IProjets)
    grok.require('zope2.View')
    grok.name('view')
    
    def _form_action(self, widget, data):
        #import pdb; pdb.set_trace()
        return '%s/@@localsearch' % self.context.absolute_url()

    def _form_handler(self, widget, data):
        #import pdb; pdb.set_trace()
        self.searchterm = data['searchterm'].extracted
    def form(self):
        form = factory('form',
            name='search',
            props={
                'action': self._form_action,
            })

        form['searchterm'] = factory(
            'field:label:error:text',
            props={
                'label': _(u'Rechercher dans les projets:'),
                'field.class': 'myFieldClass',
                'text.class': 'myInputClass',
                'size': '20',
        })
        form['submit'] = factory(
            'field:submit',
            props={
                'label': _(u'Lancer la recherche'),
                'submit.class': '',
                'handler': self._form_handler,
                'action': 'search'
        })

        controller = Controller(form, self.request)
        return controller.rendered
        
    def results(self):
        if not hasattr(self,'searchterm') or not self.searchterm:
            return []
        context = aq_inner(self.context)
        cat = getToolByName(self.context, 'portal_catalog')
        query = {}
    
        qterm = self.searchterm
        if qterm:
            qterm = '%s' % (qterm)
            query['SearchableText'] = qterm.decode('utf-8')
            query['path']={'query': '/'.join(context.getPhysicalPath())}
        #print query
        return cat(**query)                

# 
#     def render_table(self, projets):
#         """ return a table of projets """
#         #self.summary_template = ViewPageTemplateFile("projets_templates/projectlisting.pt")
#         #return self.summary_template(projets)
# 
#         projectlisting = ProjectListing(self.context,self.request)
#         listingview = getView(self.context,self.request, name="projectlisting")
#         options = {}
#         options['projets'] = projets
#         return projectlisting.render_table(options=options)

class KeywordView(InterfaceView):
    grok.context(IProjets)
    grok.require('zope2.View')
    grok.name('keywordview')
    
    pass
        
class StateView(View):
    grok.context(IProjets)
    grok.require('zope2.View')
    grok.name('stateview')
    
    pass

class LocalSearch(View):
    grok.context(IProjets)
    grok.require('zope2.View')
    grok.name('localsearch')
    
    pass

class CyclesView(InterfaceView):
    grok.context(IProjets)
    grok.require('zope2.View')
    grok.name('cyclesview')
    pass
#     def _form_action(self, widget, data):
#         #import pdb; pdb.set_trace()
#         return '%s/@@cyclesview' % self.context.absolute_url()
