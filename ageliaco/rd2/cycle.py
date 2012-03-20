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
from ageliaco.rd2.auteur import IAuteur
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

class GroupMembers(object):
    """Context source binder to provide a vocabulary of users in a given
    group.
    """
    
    grok.implements(IContextSourceBinder)
    
    def __init__(self, group_name):
        self.group_name = group_name
    
    def __call__(self, context):
        acl_users = getToolByName(context, 'acl_users')
        group = acl_users.getGroupById(self.group_name)
        terms = []
        terms.append(SimpleVocabulary.createTerm('', str(''), ''))
        if group is not None:
            for member_id in group.getMemberIds():
                user = acl_users.getUserById(member_id)
                if user is not None:
                    member_name = user.getProperty('fullname') or member_id
                    terms.append(SimpleVocabulary.createTerm(member_id, str(member_id), member_name))
            
        return SimpleVocabulary(terms)    



class ICycle(form.Schema):
    """
    Cycle de projet RD
    """
    
    # -*- Your Zope schema definitions here ... -*-
    id = schema.TextLine(
            title=_(u"Année"),
            description=_(u"L'année d'administration du projet"),
            required=True,
        )
    title = schema.TextLine(
            title=_(u"Titre"),
            description=_(u"Titre du projet"),
            required=True,
        )

    # Data grid
    #form.fieldset('Auteurs', label=_(u"Auteurs"), fields=['auteurs'])
    #if DataGridFieldFactory is not None:
    #    form.widget(auteurs=DataGridFieldFactory)
    #form.widget(auteurs=AutocompleteMultiFieldWidget)
    #auteurs = schema.List(
    #        title=_(u"Auteurs"),
    #        required=False,
    #        value_type=schema.Object(title=u'Auteurs',
    #                                     schema=IAuteur),
    #    )
            
    dexterity.write_permission(supervisor='cmf.ReviewPortalContent')
    supervisor = schema.Choice(
            title=_(u"Superviseur"),
            description=_(u"Personne de R&D qui supervise ce projet"),
            source=GroupMembers('superviseur'),
            required=False,
        )

    problematique = RichText(
            title=_(u"Problématique"),
            description=_(u"Problématique et contexte du projet pour l'année à venir"),
            required=False,
        )    
        
    objectifs = RichText(
            title=_(u"Objectifs"),
            description=_(u"Objectifs du projet pour l'année"),
            required=False,
        )    

    resultats = RichText(
            title=_(u"Résultats"),
            description=_(u"Retombées (profs et/ou élèves) du projet pour l'année"),
            required=False,
        )    

    moyens = RichText(
            title=_(u"Moyens"),
            description=_(u"Moyens nécessaires pour l'année"),
            required=False,
        )    

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



@form.default_value(field=ICycle['id'])
def idDefaultValue(data):
    # To get hold of the folder, do: context = data.context
    return str(datetime.datetime.today().year)

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
