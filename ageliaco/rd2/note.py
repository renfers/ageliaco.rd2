# -*- coding: UTF-8 -*-
from five import grok
from zope import schema
from plone.namedfile import field as namedfile
from z3c.relationfield.schema import RelationChoice, RelationList
from plone.formwidget.contenttree import ObjPathSourceBinder

from plone.directives import form, dexterity

from ageliaco.rd2 import MessageFactory

from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
from z3c.form.browser.checkbox import CheckBoxFieldWidget

import datetime

from Acquisition import aq_inner, aq_parent
from plone.app.textfield import RichText

from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName

from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget
from .interface import INote, InterfaceView, possibleAttendees

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

class View(InterfaceView):
    grok.context(INote)
    grok.require('zope2.View')
    grok.name('view')
    
    def presence(self):
        context = self.context
        note = context
        out = [[],[],[]]
        presents = [] #note.presence
        absents = [] #note.absence
        sansexcuse = []
        cycle = note.aq_parent
        attendees = possibleAttendees(cycle)
        #import pdb; pdb.set_trace()
        for item in attendees._terms:
            if item.token in note.presence:
                presents.append(item.title)
            elif item.token in note.absence:
                absents.append(item.title)
            else:
                sansexcuse.append(item.title)
        out = presents, absents, sansexcuse
        return out
    def rencontres(self):
        context = aq_inner(self.context)
        #import pdb; pdb.set_trace()
        projectPath = '/'.join(context.getPhysicalPath())
        catalog = getToolByName(self.context, 'portal_catalog')
        cat = catalog(portal_type='Event',
                       path={'query': projectPath, 'depth': 2},
                       sort_on="modified")
        
        #import pdb; pdb.set_trace()
        return cat
        