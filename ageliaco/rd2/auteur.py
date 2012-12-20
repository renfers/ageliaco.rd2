# -*- coding: UTF-8 -*-
from five import grok
from zope import schema
from plone.namedfile import field as namedfile
from z3c.relationfield.schema import RelationChoice, RelationList
from plone.formwidget.contenttree import ObjPathSourceBinder

from plone.directives import form, dexterity

from ageliaco.rd2 import _

from interface import IAuteur

from plone.app.textfield import RichText
import datetime

from plone.indexer import indexer

from plone.formwidget.autocomplete import AutocompleteFieldWidget
import unicodedata

from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.app.container.interfaces import IObjectAddedEvent
from Products.CMFCore.utils import getToolByName


@indexer(IAuteur)
def searchableIndexer(context):
    return "%s %s %s %s %s %s" % (context.firstname, 
                            context.lastname, 
                            context.address, 
                            context.email,
                            context.school,
                            context.phone)

grok.global_adapter(searchableIndexer, name="SearchableText")


@indexer(IAuteur)
def firstnameIndexer(obj):
    if obj.firstname is None:
        return None
    return obj.firstname
grok.global_adapter(firstnameIndexer, name="firstname")

        
@indexer(IAuteur)
def lastnameIndexer(obj):
    if obj.lastname is None:
        return None
    return obj.lastname
grok.global_adapter(lastnameIndexer, name="lastname")

        
@indexer(IAuteur)
def addressIndexer(obj):
    if obj.address is None:
        return None
    return obj.address
grok.global_adapter(addressIndexer, name="address")

        
@indexer(IAuteur)
def emailIndexer(obj):
    if obj.email is None:
        return None
    return obj.email
grok.global_adapter(emailIndexer, name="email")

        
@indexer(IAuteur)
def schoolIndexer(obj):
    if obj.school is None:
        return None
    return obj.school
grok.global_adapter(schoolIndexer, name="school")

