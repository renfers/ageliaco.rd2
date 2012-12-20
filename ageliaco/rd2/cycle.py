# -*- coding: UTF-8 -*-
import os.path

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

from plone.directives import form, dexterity
from plone.app.textfield import RichText
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.indexer import indexer

from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.schema.fieldproperty import FieldProperty

from ageliaco.rd2 import _
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
from zope.interface import invariant, Invalid

from Acquisition import aq_inner, aq_parent
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot
from zope.security import checkPermission

from ageliaco.rd2 import _

#from projet import IProjet
from interface import ICycle, IAuteur



"""
<model xmlns="http://namespaces.plone.org/supermodel/schema">
  <schema>
    <field name="num_projet" type="zope.schema.TextLine">
      <description />
      <title>Numero Projet</title>
    </field>
    <field name="supervisor" type="zope.schema.TextLine">
      <description>Personne de RD qui supervise ce projet</description>
      <required>False</required>
      <title>Superviseur</title>
    </field>
    <field name="superviseur2" type="zope.schema.TextLine">
      <description>Personne qui epaule le superviseur</description>
      <required>False</required>
      <title>Superviseur2</title>
    </field>
    <field name="debut" type="zope.schema.TextLine">
      <description>L'annee a laquelle le projet a commence ou devrait commencer</description>
      <title>Annee de debut</title>
    </field>
    <field name="duration" type="zope.schema.Int">
      <description>Nombre d'annees que le projet devrait durer</description>
      <title>Duree</title>
    </field>
    <field name="presentation" type="plone.app.textfield.RichText">
      <default>Presentation</default>
      <description>Presentation des enjeux et objectifs du projet</description>
      <missing_value />
      <required>False</required>
      <title>Presentation</title>
    </field>
  </schema>
</model>
"""


class Single_view(dexterity.DisplayForm):
    grok.context(ICycle)
    grok.require('zope2.View')
    grok.name('single_view')
    
    def canRequestReview(self):
        return checkPermission('cmf.RequestReview', self.context)
        
    def canAddContent(self):
        return checkPermission('cmf.AddPortalContent', self.context)
        
    def canModifyContent(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)
                
    
    def parent_url(self):
        context = aq_inner(self.context)
        parent = context.aq_parent
        print parent.absolute_url()
        return parent.absolute_url()
    
    def setaddress(self):
        for c in self.w.keys():
            print "champ : %s => %s" % (c,self.w[c])
        
        context = aq_inner(self.context)

        print context.keys()

# class View(dexterity.DisplayForm):
#     grok.context(ICycle)
#     grok.require('zope2.View')
#     
#     def canRequestReview(self):
#         return checkPermission('cmf.RequestReview', self.context)
#         
#     def canAddContent(self):
#         return checkPermission('cmf.AddPortalContent', self.context)
#         
#     def canModifyContent(self):
#         return checkPermission('cmf.ModifyPortalContent', self.context)
#                 
#     
#     def parent_url(self):
#         context = aq_inner(self.context)
#         parent = context.aq_parent
#         print parent.absolute_url()
#         return parent.absolute_url()
#     
#     def setaddress(self):
#         for c in self.w.keys():
#             print "champ : %s => %s" % (c,self.w[c])
#         
#         context = aq_inner(self.context)
# 
#         print context.keys()



# @grok.subscribe(ICycle, IObjectAddedEvent)
# @grok.subscribe(ICycle, IObjectModifiedEvent)
# def setAuteurs(cycle, event):
#     portal_url = getToolByName(cycle, 'portal_url')
#     acl_users = getToolByName(cycle, 'acl_users')
#     
#     portal = portal_url.getPortalObject() 
#     #projet = cycle.aq_parent
#     
#     #set title
#     cycle.title = cycle.id
#     authors = cycle.auteurs
#     if authors:
#         print "authors ", len(authors)
#     auteurs = []
#     for auteur in cycle.objectValues():
#         if auteur.portal_type == 'ageliaco.rd2.auteur':
#             auteurs.append(auteur.id)
# 
#     print "Enter auteur setting !!! -> ", len(auteurs)
#     
#     for auteur in auteurs:
#         print auteur
#         try:
#             author = cycle[auteur]
#         except KeyError: 
#             print "creating auteur", auteur
#             cycle.invokeFactory("ageliaco.rd.auteur", id=auteur, 
#                                 lastname=author.lastname,
#                                 firstname=author.firstname,
#                                 school=author.school,
#                                 address=author.address,
#                                 email=author.email,
#                                 phone=author.phone)
#             author = cycle[auteur]
#     
#     #projet.setContributors(projet.contributor)
#     return #projet.request.response.redirect(cycles.absolute_url() + '++add++ageliaco.rd.cycle')

        
class View(dexterity.DisplayForm):
    grok.context(ICycle)
    grok.require('zope2.View')
    
    def canRequestReview(self):
        return checkPermission('cmf.RequestReview', self.context)
        
    def canAddContent(self):
        return checkPermission('cmf.AddPortalContent', self.context)
        
    def canModifyContent(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)
        
        
        
    def auteurs(self):
        context = aq_inner(self.context)
        
        catalog = getToolByName(self.context, 'portal_catalog')
        log( 'context path : ' + context.absolute_url())
        
        return catalog(object_provides=[IAuteur.__identifier__],
                       path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
                       sort_on='sortable_title')
        

    def delAuteur(self,auteur):
        context = aq_inner(self.context)
        if auteur in context.keys():
            del context[auteur]
        return context.absolute_url()
    
    def parent_url(self):
        context = aq_inner(self.context)
        parent = context.aq_parent
        print parent.absolute_url()
        return parent.absolute_url()

    def cycle_url(self):
        context = aq_inner(self.context)
        print context.absolute_url()
        return context.absolute_url()
    
    def setaddress(self):
        for c in self.w.keys():
            print "champ : %s => %s" % (c,self.w[c])
        
        context = aq_inner(self.context)

        print context.keys()

    def contributeur(self,auteur):
        context = aq_inner(self.context)
        
        if auteur in context.keys():
            return context[auteur]
        return None
    
@indexer(ICycle)
def searchableIndexer(context):
    keywords = " ".join(context.subject)
    return "%s %s %s %s %s" % (context.title, 
                            context.description, 
                            context.problematique, 
                            context.objectifs,
                            keywords)

grok.global_adapter(searchableIndexer, name="SearchableText")



# @indexer(ICycle)
# def authorsIndexer(obj):
#     return obj.contributor
# grok.global_adapter(authorsIndexer, name="authors")


# class Add(dexterity.AddForm):
#     grok.name('ageliaco.rd2.cycle')
# 
#     label = _(u"Dépôt de projet")
#     def updateWidgets(self):
#         super(Add, self).updateWidgets()
#         self.widgets['id'].mode = 'hidden'

# class AddForm(dexterity.AddForm):
#     grok.name('ageliaco.rd2.cycle')
# 
#     label = _(u"Dépôt de projet")
#     def updateWidgets(self):
#         super(Add, self).updateWidgets()
#         self.widgets['id'].mode = 'hidden'

    

# class DataGridEditView(DefaultEditForm):
#     """Edit form that uses the ContentTreeWidget for some fields in
#     the datagrids.
#     """
# 
#     def datagridInitialise(self, subform, widget):
#         if widget.name == 'form.widgets.auteurs':
#             subform.fields['auteurs'].widgetFactory = ContentTreeFieldWidget
#         datagrid.auto_append = True
# 
# class DataGridView(DefaultView):
#     """View that uses the ContentTreeWidget for some fields in the
#     datagrids.
#     """
# 
#     # Just point to the original template from plone.dexterity.
#     index = ViewPageTemplateFile(
#         'item.pt', os.path.dirname(plone.dexterity.browser.__file__))
# 
#     def datagridInitialise(self, subform, widget):
#         if widget.name == 'form.widgets.auteurs':
#             subform.fields['auteur'].widgetFactory = ContentTreeFieldWidget
#         datagrid.auto_append = True
# 
# 
# class DatagridAddForm(DefaultAddForm):
# 
#     def datagridInitialise(self, subform, widget):
#         if widget.name == 'form.widgets.auteurs':
#             subform.fields['auteur'].widgetFactory = ContentTreeFieldWidget
#         datagrid.auto_append = True
# 
# 
# class DatagridAddView(DefaultAddView):
#     """Add-view that uses the ContentTreeWidget for some fields in the
#     datagrids.
#     """
# 
#     form = DatagridAddForm    
