# -*- coding: UTF-8 -*-
from five import grok
from zope import schema
from plone.namedfile import field as namedfile
from z3c.relationfield.schema import RelationChoice, RelationList
from plone.formwidget.contenttree import ObjPathSourceBinder

from plone.directives import form, dexterity

from ageliaco.rd2 import _


import datetime

from Acquisition import aq_inner, aq_parent
from plone.app.textfield import RichText

from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName

from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget

@grok.provider(IContextSourceBinder)
def possibleAttendees(context):
    acl_users = getToolByName(context, 'acl_users')
    parent = context.__parent__
    #group = acl_users.getGroupById(projectID)
    terms = []
    group = parent.getContributor()
    group.append(parent.getSupervisor())
    group.append(parent.getSupervisor2())
    
    if group is not None:
        for member in group:
            terms.append(member)
            
    return SimpleVocabulary(terms)

"""
<model xmlns="http://namespaces.plone.org/supermodel/schema">
  <schema>
    <field name="presence" type="zope.schema.Text">
      <default>${owner}
${contributor}</default>
      <description>Personnes presentes au rendez-vous</description>
      <required>False</required>
      <title>Presents</title>
    </field>
    <field name="absence" type="zope.schema.Text">
      <description>Personnes absentes au rendez-vous</description>
      <required>False</required>
      <title>Absents</title>
    </field>
    <field name="objectifs" type="plone.app.textfield.RichText">
      <description>Objectifs et planification</description>
      <required>False</required>
      <title>Objectifs</title>
    </field>
    <field name="date_prochain_rdv" type="zope.schema.Datetime">
      <description>Date fixee pour le prochain rendez-vous</description>
      <required>False</required>
      <title>Date du prochain rdv</title>
    </field>
    <field name="lieu_prochain_rdv" type="zope.schema.TextLine">
      <description>Lieu du prochain rendez-vous</description>
      <required>False</required>
      <title>Lieu du prochain rdv</title>
    </field>
  </schema>
</model>
"""
class INote(form.Schema):
    """
    Note de suivi de rendez-vous
    """
    # -*- Your Zope schema definitions here ... -*-
    
    title = schema.TextLine(
            title=_(u"Titre"),
            required=False,
        )    

    #form.widget(presence=AutocompleteMultiFieldWidget)
    presence = schema.Text(
            title=_(u"Personnes présentes"),
            #default=[],
            #value_type=schema.Choice(source=possibleAttendees,),            
            required=False,
        )

    #form.widget(absence=AutocompleteMultiFieldWidget)
    absence = schema.Text(
            title=_(u"Personnes absentes"),
            #default=[],
            #value_type=schema.Choice(source=possibleAttendees,),            
            required=False,
        )

    presentation = RichText(
            title=_(u"Notes de séance"),
            description=_(u"Compte-rendu de l'avancement du projet"),
            required=False,
        )    

    dexterity.read_permission(reviewNotes='cmf.ReviewPortalContent')
    dexterity.write_permission(reviewNotes='cmf.ReviewPortalContent')
    reviewNotes = RichText(
            title=_(u"Notes internes"),
            description=_(u"Notes visibles que par R&D"),
            required=False,
        )    
    
    nextmeeting = schema.Datetime(
            title=_(u"Date du prochain rendez-vous"),
            required=False,
        )

    meetingplace = schema.TextLine(
            title=_(u"Lieu du prochain rendez-vous"),
            required=False,
        )    

@form.default_value(field=INote['title'])
def startDefaultValue(data):
    # To get hold of the folder, do: context = data.context
    day =  datetime.datetime.today()
    return "Note-" + day.strftime("%Y-%m-%d")
