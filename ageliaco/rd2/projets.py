# -*- coding: UTF-8 -*-
from five import grok
from zope import schema

from plone.directives import form, dexterity
from z3c.form import field, button

#from cycle import Projet

from ageliaco.rd2 import _

# for debug purpose => log(...)
from Products.CMFPlone.utils import log

from projet import IProjet
from cycle import ICycle

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


        
# class View(grok.View):
#     grok.context(IProjets)
#     grok.require('zope2.View')
#     
#     def projets(self, wf_state='all'):
#         """Return a catalog search result of projects to show
#         """
#         
#         context = aq_inner(self.context)
#         catalog = getToolByName(context, 'portal_catalog')
#         log( "context's physical path : " + '/'.join(context.getPhysicalPath()))
#         log( "all projects")
#         if wf_state == 'all':
#             log( "all projets")
#             log('/'.join(context.getPhysicalPath()))
#             return catalog(object_provides= IProjet.__identifier__,
#                            path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
#                            sort_on="start", sort_order="reverse")        
#         return catalog(object_provides=[IProjet.__identifier__],
#                        review_state=wf_state,
#                        path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
#                        sort_on='sortable_title')
# 
#     def cycles(self, projectPath, wf_state='all'):
#         """Return a catalog search result of cycles from a project
#         """
#         
#         context = aq_inner(self.context)
#         catalog = getToolByName(self.context, 'portal_catalog')
#         log( 'cycle : ' + projectPath)
#         log( wf_state + " state chosen")
#         if wf_state == 'all':
#             log( "all cycles")
#             return catalog(object_provides= ICycle.__identifier__,
#                            path={'query': projectPath, 'depth': 1},
#                            sort_on="modified", sort_order="reverse")        
#         return catalog(object_provides=[ICycle.__identifier__],
#                        review_state=wf_state,
#                        path={'query': projectPath, 'depth': 2},
#                        sort_on='sortable_title')
# 
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

        
