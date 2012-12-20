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
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
import unicodedata

from ageliaco.rd2 import _
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow

import datetime

import z3c.form
# for debug purpose => log(...)
from Products.CMFPlone.utils import log


from zope.schema.interfaces import IContextSourceBinder
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.app.container.interfaces import IObjectAddedEvent
from Products.CMFCore.utils import getToolByName
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from plone.namedfile.field import NamedImage
from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget, AutocompleteFieldWidget

from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget
from zope.interface import invariant, Invalid

from Acquisition import aq_inner, aq_parent
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot
from zope.security import checkPermission

from AccessControl.interfaces import IRoleManager

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
        #terms.append(SimpleVocabulary.createTerm('', str(''), ''))
        if group is not None:
            for member_id in group.getMemberIds():
                user = acl_users.getUserById(member_id)
                if user is not None:
                    member_name = user.getProperty('fullname') or member_id
                    terms.append(SimpleVocabulary.createTerm(member_id, str(member_id), member_name))
            
        return SimpleVocabulary(terms)    


class ProjetsVoc(object):
    """Context source binder to provide a vocabulary of users in a given
    group.
    """
    
    grok.implements(IContextSourceBinder)
    
    def __init__(self, projet_name):
        self.projet_name = projet_name
    
    def __call__(self, context):
        acl_users = getToolByName(context, 'acl_users')
        group = acl_users.getGroupById(self.projet_name)
        terms = []
        terms.append(SimpleVocabulary.createTerm('', str(''), ''))
        if group is not None:
            for member_id in group.getMemberIds():
                user = acl_users.getUserById(member_id)
                if user is not None:
                    member_name = user.getProperty('fullname') or member_id
                    terms.append(SimpleVocabulary.createTerm(member_id, str(member_id), member_name))
            
        return SimpleVocabulary(terms)    


    
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



class IProjet(form.Schema):
    """
    Projet RD
    """
    start = schema.TextLine(
            title=_(u"Année"),
            description=_(u"L'année à laquelle le projet a commencé ou devrait commencer"),
            required=True,
        )

    duration = schema.Int(
            title=_(u"Durée"),
            description=_(u"Durée (en années) du projet, prévue ou effective"),
            required=True,
        )
    
    presentation = RichText(
            title=_(u"Présentation"),
            description=_(u"Présentation synthétique du projet (présentation publiée)"),
            required=True,
        )    

    picture = NamedImage(
            title=_(u"Chargez une image pour le projet"),
            required=False,
        )

    lien = schema.TextLine(
            title=_(u"Lien vers la réalisation"),
            description=_(u"Lien extérieur vers la réalisation"),
            required=False,
        )

    
@grok.subscribe(IProjet, IObjectAddedEvent)
def setRealisation(projet, event):
    admid = 'realisation'
    try:
        cycles = projet[admid]
    except KeyError: 
        rea = projet.invokeFactory("Folder", id=admid, title=u'Réalisation')
        #projet[admid] = rea
    
    #projet.setContributors(projet.contributor)
    #request.response.redirect(cycles.absolute_url() + '++add++ageliaco.rd2.cycle')
    return #request.response.redirect(cycles.absolute_url() + '++add++ageliaco.rd2.cycle')

@grok.provider(IContextSourceBinder)
def activeProjects(context):
    catalog = getToolByName(context, 'portal_catalog')
    cat = catalog(portal_type='ageliaco.rd2.projet',
                   review_state='encours',
                   sort_on='sortable_title')
    log('catalogue : %s items'%len(cat))

    terms = []
                
    for brain in cat:
        print dir(brain)
        print "getURL : %s => getPath : %s " % (brain.getURL(),brain.getPath())
        terms.append(SimpleVocabulary.createTerm(brain.getPath(), brain.id, brain.Title))
    return SimpleVocabulary(terms) #SimpleVocabulary([SimpleVocabulary.createTerm(x.id, x.getURL(), x.Title) for x in cat])

    
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
    description = schema.TextLine(
            title=_(u"Sous-titre"),
            description=_(u"Sous-titre du projet"),
            required=False,
        )
    presentation = RichText(
            title=_(u"Présentation succincte du projet"),
            description=_(u"Présentation succincte du projet (synopsis)"),
            required=True,
        )    

    #form.widget(projet=AutocompleteFieldWidget)
    projet = schema.Choice(
            title=_(u"Projet existant"),
            description=_(u"Lien vers un projet existant"),
            source=activeProjects,
            required=False,
        )
            
    dexterity.write_permission(supervisor='cmf.ReviewPortalContent')
    supervisor = schema.Choice(
            title=_(u"Superviseur"),
            description=_(u"Personne de R&D qui supervise ce projet"),
            source=GroupMembers('superviseur'),
            required=False,
        )
        
    problematique = RichText(
            title=_(u"Problématique"),
            description=_(u"Problématique et contexte du projet"),
            required=False,
        )    
        
    objectifs = RichText(
            title=_(u"Objectifs"),
            description=_(u"Objectifs, moyens nécessaires et résultats escomptés du projet pour l'année"),
            required=False,
        )    


@form.default_value(field=ICycle['id'])
def idDefaultValue(data):
    # To get hold of the folder, do: context = data.context
    return str(datetime.datetime.today().year)
    
@grok.subscribe(ICycle, IObjectModifiedEvent)
def setSupervisor(cycle, event):
    if not cycle.supervisor:
        return
    if IRoleManager.providedBy(cycle):
        cycle.manage_addLocalRoles(cycle.supervisor, ['Reader', 'Contributor', 'Editor'])
    log("Role added to %s for %s"%(cycle.id,cycle.supervisor))

@grok.subscribe(ICycle, IObjectAddedEvent)
def setAuteurs(cycle, event):
    print "Projet lié à %s ==> %s ==> %s" % (cycle.id,cycle.projet,cycle.supervisor)
    if not cycle.projet:
        return
    catalog = getToolByName(cycle, 'portal_catalog')
    cat = catalog(portal_type='ageliaco.rd2.cycle',
                   path={'query': cycle.projet, 'depth': 1},
                   sort_on="id",sort_order="reverse")
    log('catalogue des cycles : %s items'%len(cat))
    
    #if there cycles, take the last one (first in reverse) and copy the authors
    if len(cat):
        lastCyclePath = cat[0].getPath()
        lastCycle = cat[0].getObject()
        auteurBrains = catalog(portal_type='ageliaco.rd2.auteur',
                        path={'query': lastCyclePath, 'depth': 1})
        for brain in auteurBrains:
            auteur = brain.getObject()
            cb_copy_data = lastCycle.manage_copyObjects([auteur.id])
            cycle.manage_pasteObjects(cb_copy_data)    
    #projet.setContributors(projet.contributor)
    #request.response.redirect(cycles.absolute_url() + '++add++ageliaco.rd2.cycle')
    return #request.response.redirect(cycles.absolute_url() + '++add++ageliaco.rd2.cycle')

    
