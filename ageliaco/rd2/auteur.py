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

from plone.indexer import indexer

from plone.formwidget.autocomplete import AutocompleteFieldWidget
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
import unicodedata

from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.app.container.interfaces import IObjectAddedEvent
from Products.CMFCore.utils import getToolByName


schools = {u"ECGGR":[u"EC Bougeries",u"CEC"],
    u"CEBOU":[u"Nicolas-Bouvier",u"CEC"],
    u"CECHA":[u"André-Chavanne",u"CEC"],
    u"CEGOU":[u"Emilie-Gourd",u"CEC"],
    u"ECASE":[u"Madame-de-Stael",u"CEC"],
    u"ECSTI":[u"EC Aimée-Stitelmann",u"CEC"],
    u"CALV":[u"Calvin",u"COLLEGES"],
    u"CAND":[u"Candolle",u"COLLEGES"],
    u"CLAP":[u"Claparède",u"COLLEGES"],
    u"COPAD":[u"Alice-Rivaz",u"COLLEGES"],
    u"ROUS":[u"Rousseau",u"COLLEGES"],
    u"SAUS":[u"Saussure",u"COLLEGES"],
    u"SISM":[u"Sismondi",u"COLLEGES"],
    u"VOLT":[u"Voltaire",u"COLLEGES"],
    u"ECBGR":[u"ECG RHONE",u"ECG"],
    u"DUNAN":[u"Henry-Dunand",u"ECG"],
    u"MAILL":[u"Ella-Maillart",u"ECG"],
    u"ECGJP":[u"Jean-Piaget",u"ECG"],
    u"CFPC":[u"CFPC",u"ECOLES PROFESSIONNELLES"],
    u"CFPS":[u"CFPS",u"ECOLES PROFESSIONNELLES"],
    u"CFPT":[u"CFPT",u"ECOLES PROFESSIONNELLES"],
    u"CFPSH":[u"CFPSHR-EGEI",u"ECOLES PROFESSIONNELLES"],
    u"BOUV":[u"CFPCOM-Bouvier",u"ECOLES PROFESSIONNELLES"],
    u"CFPNE":[u"CFPNE",u"ECOLES PROFESSIONNELLES"],
    u"CFPAA":[u"CFPAA",u"ECOLES PROFESSIONNELLES"],
    u"SCAI":[u"SCAI",u"INSERTION"],
    u"COUDR":[u"CO Coudriers",u"CYCLES"]}

class SchoolsVocabulary(object):
    grok.implements(IVocabularyFactory)
    def __call__(self, context):
        terms = []
        for school in schools.keys():
            terms.append(SimpleVocabulary.createTerm(unicodedata.normalize('NFKC',school).encode('ascii','ignore'), 
                            unicodedata.normalize('NFKC',schools[school][0]).encode('ascii','ignore'), 
                            unicodedata.normalize('NFKC',schools[school][0]).encode('ascii','ignore')))
        return SimpleVocabulary(terms)
grok.global_utility(SchoolsVocabulary, name=u"ageliaco.rd2.schools")

class IAuteur(form.Schema):
    """
    Auteur de projet
    """
    # removed because if user is removed from ldap it generates an error
    #
    #     form.widget(id=AutocompleteFieldWidget)
    #     id = schema.Choice(
    #             title=_(u"Pseudo"),
    #             description=_(u"Login p10"),
    #             vocabulary=u"plone.principalsource.Users",
    #             required=True,
    #         )
    id = schema.TextLine(
            title=_(u"id"),
            description=_(u"Identifiant (login)"),
            required=True,
        )



    lastname = schema.TextLine(
            title=_(u"Nom"),
            description=_(u"Nom de famille"),
            required=True,
        )

    firstname = schema.TextLine(
            title=_(u"Prénom"),
            description=_(u"Prénom"),
            required=True,
        )

    school = schema.Choice(
            title=_(u"Ecole"),
            description=_(u"Etablissement scolaire de référence"),
            vocabulary=u"ageliaco.rd2.schools",
            default='',
            required=False,
        )

    address = schema.Text(
            title=_(u"Adresse"),
            description=_(u"Adresse postale"),
            required=False,
        )
        
    email = schema.TextLine(
            title=_(u"Email"),
            description=_(u"Adresse courrielle"),
            required=True,
        )

    phone = schema.TextLine(
            title=_(u"Téléphone"),
            description=_(u"Téléphone"),
            required=False,
        )


    
@grok.subscribe(IAuteur, IObjectAddedEvent)
def setAuteur(auteur, event):
    portal_url = getToolByName(auteur, 'portal_url')
    acl_users = getToolByName(auteur, 'acl_users')
    
    print "Nous y voici ::::>>>> ", auteur.id
    portal = portal_url.getPortalObject() 
    cycles = auteur.aq_parent
    print 'auteur id : ' + auteur.id
    user = acl_users.getUserById(auteur.id)
#     if user is not None:
#         member_name = user.getProperty('fullname') or auteur.id
#         auteur.email = user.getProperty('email') or ''
#         auteur.firstname = user.getProperty('firstname') or ''
#         auteur.lastname = user.getProperty('lastname') or ''
#         auteur.school = user.getProperty('school')
#         schools = auteur.school
#         print "Ecoles : " + schools
#         if schools in [list,tuple] and len(schools) > 0 : auteur.school = schools[0]
#         print "auteur : %s %s, %s, %s" % (auteur.firstname, auteur.lastname, auteur.email, auteur.school)
#         
#     return #projet.request.response.redirect(cycles.absolute_url() + '++add++ageliaco.rd2.cycle')
        
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
    if obj.firstname is None:
        return None
    return obj.email
grok.global_adapter(emailIndexer, name="email")

        
@indexer(IAuteur)
def schoolIndexer(obj):
    if obj.school is None:
        return None
    return obj.school
grok.global_adapter(schoolIndexer, name="school")

