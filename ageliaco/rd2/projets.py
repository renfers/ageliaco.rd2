# -*- coding: UTF-8 -*-
from five import grok
from zope import schema

from plone.directives import form, dexterity
from z3c.form import field, button

#from cycle import Projet

from ageliaco.rd2 import MessageFactory

# for debug purpose => log(...)
from Products.CMFPlone.utils import log

from interface import IProjet, ICycle, IAuteur, InterfaceView

from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName

from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget,\
    AutocompleteFieldWidget
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
_ = MessageFactory



class IProjets(form.Schema):
    """
    Projets de Projet RD
    """
    presentation = RichText(
            title=MessageFactory(u"Projets SEF"),
            required=False,
        )    

    # contexte Fieldset
    form.fieldset(
        'vocabulaires',
        label=_(u"Vocabulaires"),
        fields=['filieres', 'schools', 'domaines',
                'disciplines', 'sponsorships']
    )

    filieres = schema.Text(title=u"Filières",
                description=u"Tapez une ligne par filière",
                required=False,
            )
    schools = schema.Text(title=u"Ecoles",
                description=u"format => CIGLE,nom école,FILIERE,LOGIN_DIRECTEUR",
                )
    domaines = schema.Text(title=u"Domaines d'étude",
                description=u"Tapez une ligne par domaine",
                required=False,
            )
    disciplines = schema.Text(title=u"Disciplines",
                description=u"Tapez une ligne par discipline",
                required=False,
            )
    #     schools = schema.List(title=u"Ecoles",
    #             description=u"Ecoles, avec leur filière et leur directeur",
    #             value_type=schema.Object(ISchool, title=u"Ecole"),
    #             required=False,)
    sponsorships = schema.Text(title=u"Heures de dégrevement",
                description=u"Tapez une ligne par valeur",
                required=False,
            )
    

    
        
class View(InterfaceView):
    grok.context(IProjets)
    grok.require('zope2.View')
    grok.name('view')
    
    def results(self):
        return self.cat
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
                'label': MessageFactory(u'Rechercher dans les projets:'),
                'field.class': 'myFieldClass',
                'text.class': 'myInputClass',
                'size': '20',
        })
        form['submit'] = factory(
            'field:submit',
            props={
                'label':  MessageFactory(u'Lancer la recherche'),
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
