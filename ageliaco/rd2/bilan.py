# -*- coding: UTF-8 -*-
from five import grok
from zope import schema
from plone.namedfile import field as namedfile
from z3c.relationfield.schema import RelationChoice, RelationList
from plone.formwidget.contenttree import ObjPathSourceBinder

from plone.directives import form, dexterity

from ageliaco.rd2 import _

from plone.app.textfield import RichText
import datetime



"""
<model xmlns="http://namespaces.plone.org/supermodel/schema">
  <schema>
    <field name="annee_scolaire" type="zope.schema.TextLine">
      <description>Ann&#233;e scolaire concern&#233;e</description>
      <title>Ann&#233;e scolaire</title>
    </field>
    <field name="objectifs" type="plone.app.textfield.RichText">
      <default />
      <description>Objectifs realises ou a realiser</description>
      <missing_value />
      <title>Objectifs</title>
    </field>
    <field name="documents_produits" type="zope.schema.Text">
      <description />
      <required>False</required>
      <title>Documents produits</title>
    </field>
    <field name="lien_internet" type="zope.schema.TextLine">
      <description>Lien internet, si le projet a g&#233;n&#233;r&#233; une production internet</description>
      <required>False</required>
      <title>Lien internet</title>
    </field>
  </schema>
</model>
"""

class IBilan(form.Schema):
    """
    Bilan de projet
    """

    presentation = RichText(
            title=_(u"Présentation du bilan"),
            description=_(u"Objectifs réalisés ou à réaliser"),
            required=True,
        )    

    docs = schema.Text(
            title=_(u"Documents produits"),
            description=_(u"Type de document et référence"),
            required=True,
            default=u"Aucun"
        )

    weblink = schema.TextLine(
            title=_(u"Lien internet"),
            description=_(u"Version internet du projet (lien principal)"),
            required=False,
        )
        
