# -*- coding: UTF-8 -*-

"""
ldap filter for R&D :
(|(memberof=cn=SITE-RD,ou=SECRETAIRES,ou=ESPACES-SCOLAIRES,ou=UO0872,ou=PO,ou=EEL,o=GRP,dc=EEL)
 (memberof=CN=TOUS,ou=DEGRES,ou=ENSEIGNANTS,ou=PO,ou=PO,ou=EEL,o=GRP,dc=EEL)  
 (memberof=CN=ETAT,ou=GLOBAL,ou=PO,ou=PO,ou=EEL,o=GRP,dc=EEL)  
 (memberof=CN=INVITES-ENSEIGNANTS,ou=GLOBAL,ou=PO,ou=PO,ou=EEL,o=GRP,dc=EEL)  
 (memberof=CN=INVITES-EXTERNES,ou=GLOBAL,ou=PO,ou=PO,ou=EEL,o=GRP,dc=EEL))
"""
import os.path
from Products.CMFPlone.utils import safe_unicode

from Products.Five import BrowserView
from five import grok
from zope import schema
from plone.namedfile import field as namedfile
from z3c.relationfield.schema import RelationChoice, RelationList
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.dexterity.browser.add import DefaultAddView, DefaultAddForm
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.browser.view import DefaultView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.textfield.value import RichTextValue
import plone.dexterity.browser
from plone.dexterity.utils import createContentInContainer
from plone.dexterity.utils import createContent
from plone.dexterity.interfaces import IDexterityFTI
from zope.interface import implements

from plone.directives import form, dexterity
from plone.app.textfield import RichText
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.indexer import indexer

from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.schema.fieldproperty import FieldProperty
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
import unicodedata
from zope.interface import invariant, Invalid, Interface
from plone.z3cform.interfaces import IWrappedForm

from ageliaco.rd2 import MessageFactory
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
import datetime

import zope.interface

import z3c.form
from z3c.form import validator
from z3c.form import button
from z3c.form.interfaces import ActionExecutionError, WidgetActionExecutionError
from zope.app.pagetemplate import ViewPageTemplateFile as Zope3PageTemplateFile
from plone.z3cform.z2 import processInputs
from plone.z3cform.crud import crud
# for debug purpose => log(...)
from Products.CMFPlone.utils import log
from plone.z3cform import layout
from plone.memoize import view

from AccessControl import getSecurityManager
from AccessControl import Unauthorized

# Import permission names as pseudo-constant strings from somewhere...
# see security doc for more info
from Products.CMFCore.permissions import ManagePortal


from zope.schema.interfaces import IVocabularyFactory
from zope.schema.interfaces import IContextSourceBinder
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.app.container.interfaces import IObjectAddedEvent
from Products.CMFCore.utils import getToolByName
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from plone.namedfile.field import NamedImage
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form import field
from plone.app.widgets.dx import SelectWidget

from zope.interface import invariant, Invalid

from Acquisition import aq_inner, aq_parent
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot
from zope.security import checkPermission

from AccessControl.interfaces import IRoleManager

import yafowil.plone
import yafowil.loader
from yafowil.base import factory, UNSET, ExtractionError
from yafowil.controller import Controller
from yafowil.plone.form import Form

from AccessControl.interfaces import IRoleManager
from Products.statusmessages.interfaces import IStatusMessage

from collective import dexteritytextindexer


from zope.component import getUtility
from plone.registry.interfaces import IRegistry

import unicodedata

def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
    
def utf_8(input_str):
    return unicode(input_str,"utf-8")
    
_ = MessageFactory

"""
Collèges =>
CALV : collège Calvin
CAND : collège de Candolle
CLAP : collège Claparède
ROUS : collège Rousseau
SAUS : collège de Saussure
SISM : collège Sismondi
VOLT : collège Voltaire
STAEL : collège de Staël
COPAD : collège pour adultes Alice-Rivaz

CFPPC centre de formation à la pratique professionnelle commerciale =>
CEBOU : EC Nicolas-Bouvier
CECHA : CEC André-Chavanne
CEGOU : CEC Emilie-Gourd
STITE : EC Aimée-Stitelmann
BGRIE : EC Bougeries

Insertion =>
ACPO : service de l'accueil du postobligatoire
CTP : centre de la transition professionnelle
ECG =>
DUNAN : ECG Henry-Dunant
PIAGE : ECG Jean-Piaget
MAILL : ECG Ella-Maillart

CFP Ecoles professionnelles =>
CFPAA : centre de formation professionnelle arts appliqués
CFPC : centre de formation professionnelle construction
CFPSHR : centre de formation professionnelle service hôtellerie restauration
CFPT : centre de formation professionnelle technique
CFPne : centre de formation professionnelle nature et environnement
CFPS : centre de formation professionnelle santé social
ESPOD : école supérieure des podologues
ESHYD : école supérieure des hygiénistes dentaires
ESAME : école supérieure des assistant-e-s de médecin
ECLAB : école des métiers du laboratoire
ESEDE : école supérieure d'éducatrices et d'éducateurs de l'enfance
ESAMB : école supérieure des ambulancier-ère-s
CUISI : filière romande de cuisinier-ère-s en diététique
FORAD : formation d'assistant-e-s dentaires
ECGEI : école des gestionnaires en intendance
ECASE : école d'assistant-e-s socio-éducativ-ve-s
ECASO : école d'assistant-e-s en soins et santé communautaire
 
"""
# ordres = {
#     "COLLEGES" : u"COLLEGES",
#     "COPAD" : u"COPAD",
#     "ECG" : u"ECG",
#     "INSERTION" : u"INSERTION",
#     "CFPCom" : u"CFPCom",
#     "CFPC": u"CFPC",
#     "CFPS":u"CFPS",
#     "CFPS-ECASE":u"CFPS-ECASE",
#     "CFPS-ECASO":u"CFPS-ECASO",
#     "CFPS-ESHYD":u"CFPS-ESHYD",
#     "CFPS-FORAD":u"CFPS-FORAD",
#     "CFPS-ECLAB":u"CFPS-ECLAB",
#     "CFPS-CUISI":u"CFPS-CUISI",
#     "CFPS-ECAME":u"CFPS-ECAME",
#     "CFPS-ESPOD":u"CFPS-ESPOD",
#     "CFPS-ESEDE":u"CFPS-ESEDE",
#     "CFPS-ESAMB":u"CFPS-ESAMB",
#     "CFPT":u"CFPT",
#     "CFPT-MECATRONIQUE":u"CFPT-MECATRONIQUE",
#     "CFPT-ELECTRONIQUE":u"CFPT-ELECTRONIQUE",
#     "CFPT-AUTOMOBILE":u"CFPT-AUTOMOBILE",
#     "CFPT-HORLOGERIE":u"CFPT-HORLOGERIE",
#     "CFPT-INFORMATIQUE":u"CFPT-INFORMATIQUE",
#     "CFPSHR":u"CFPSHR",
#     "CFPSHR-ECGEI":u"CFPSHR-ECGEI",
#     "CFPNE":u"CFPNE",
#     "CFPAA":u"CFPAA",
#     }
# 
# professionnelles = {
#     "CFPPC": u"CFPPC",
#     "CFPS":u"CFPS",
#     "CFPS-ECASE":u"CFPS-ECASE",
#     "CFPS-ECASO":u"CFPS-ECASO",
#     "CFPS-ESHYD":u"CFPS-ESHYD",
#     "CFPS-FORAD":u"CFPS-FORAD",
#     "CFPS-ECLAB":u"CFPS-ECLAB",
#     "CFPS-CUISI":u"CFPS-CUISI",
#     "CFPS-ECAME":u"CFPS-ECAME",
#     "CFPS-ESPOD":u"CFPS-ESPOD",
#     "CFPS-ESEDE":u"CFPS-ESEDE",
#     "CFPS-ESAMB":u"CFPS-ESAMB",
#     "CFPT":u"CFPT",
#     "CFPT-MECATRONIQUE":u"CFPT-MECATRONIQUE",
#     "CFPT-ELECTRONIQUE":u"CFPT-ELECTRONIQUE",
#     "CFPT-AUTOMOBILE":u"CFPT-AUTOMOBILE",
#     "CFPT-HORLOGERIE":u"CFPT-HORLOGERIE",
#     "CFPT-INFORMATIQUE":u"CFPT-INFORMATIQUE",
#     "CFPSH":u"CFPSHR",
#     "CFPSHR-ECGEI":u"CFPSHR-ECGEI",
#     "CFPNE":u"CFPNE",
#     "CFPAA":u"CFPAA",
#     }
    
# schools = {
#     'CALV' : ['CALV',u"collège Calvin",u"COLLEGES"],
#     'CAND' : ['CAND',u"collège de Candolle",u"COLLEGES"],
#     'CLAP' : ['CLAP',u"collège Claparède",u"COLLEGES"],
#     'ROUS' : ['ROUS',u"collège Rousseau",u"COLLEGES"],
#     'SAUS' : ['SAUS',u"collège de Saussure",u"COLLEGES"],
#     'SISM' : ['SISM',u"collège Sismondi",u"COLLEGES"],
#     'VOLT' : ['VOLT',u"collège Voltaire",u"COLLEGES"],
#     'STAEL' : ['STAEL',u"collège de Staël",u"COLLEGES"],
#     'COPAD' : ['COPAD',u"collège pour adultes Alice-Rivaz",u"COLLEGES"],
#     'CEBOU' : ['CEBOU',u"EC Nicolas-Bouvier",u"CFPPC"],
#     'CECHA' : ['CECHA',u"CEC André-Chavanne",u"CFPPC"],
#     'CEGOU' : ['CEGOU',u"CEC Emilie-Gourd",u"CFPPC"],
#     'STITE' : ['STITE',u"EC Aimée-Stitelmann",u"CFPPC"],
#     'BGRIE' : ['BGRIE',u"EC Bougeries",u"CFPPC"],
#     'CFPAA' : ['CFPAA',u"centre de formation professionnelle arts appliqués",u"CFP"],
#     'CFPC' : ['CFPC',u"centre de formation professionnelle construction",u"CFP"],
#     'CFPSHR' : ['CFPSHR',u"centre de formation professionnelle service hôtellerie restauration",u"CFP"],
#     'CFPT' : ['CFPT',u"centre de formation professionnelle technique",u"CFP"],
#     'CFPne' : ['CFPne',u"centre de formation professionnelle nature et environnement",u"CFP"],
#     'CFPS' : ['CFPS',u"centre de formation professionnelle santé social",u"CFP"],
#     'ESPOD' : ['ESPOD',u"école supérieure des podologues",u"CFP"],
#     'ESHYD' : ['ESHYD',u"école supérieure des hygiénistes dentaires",u"CFP"],
#     'ESAME' : ['ESAME',u"école supérieure des assistant-e-s de médecin",u"CFP"],
#     'ECLAB' : ['ECLAB',u"école des métiers du laboratoire",u"CFP"],
#     'ESEDE' : ['ESEDE',u"école supérieure d'éducatrices et d'éducateurs de l'enfance",u"CFP"],
#     'ESAMB' : ['ESAMB',u"école supérieure des ambulancier-ère-s",u"CFP"],
#     'CUISI' : ['CUISI',u"filière romande de cuisinier-ère-s en diététique",u"CFP"],
#     'FORAD' : ['FORAD',u"formation d'assistant-e-s dentaires",u"CFP"],
#     'ECGEI' : ['ECGEI',u"école des gestionnaires en intendance",u"CFP"],
#     'ECASE' : ['ECASE',u"école d'assistant-e-s socio-éducativ-ve-s",u"CFP"],
#     'ECASO' : ['ECASO',u"école d'assistant-e-s en soins et santé communautaire",u"CFP"],
#     'DUNAN' : ['DUNAN',u"ECG Henry-Dunant",u"ECG"],
#     'PIAGE' : ['PIAGE',u"ECG Jean-Piaget",u"ECG"],
#     'MAILL' : ['MAILL',u"ECG Ella-Maillart",u"ECG"],
#     'ACPO' : ['ACPO',u"service de l'accueil du postobligatoire",u"INSERTION"],
#     'CTP' : ['CTP',u"centre de la transition professionnelle",u"INSERTION"],
#     }
# 
# sponsorships = {"0":[u"0",0],
#     0.25:[u"0.25",0.25],
#     0.5:[u"0.5",0.5],
#     0.75:[u"0.75",0.75],
#     1.0:[u"1.0",1.0],
#     1.25:[u"1.25",1.25],
#     1.5:[u"1.5",1.5],
#     1.75:[u"1.75",1.75],
#     2.0:[u"2.0",2.0],
#     2.25:[u"2.25",2.25],
#     2.5:[u"2.5",2.5],
#     2.75:[u"2.75",2.75],
#     3.0:[u"3.0",3.0]}


def getProjetsParent(context):
    if not context:
        return None
    if context.portal_type == 'ageliaco.rd2.projets':
        return context
    urltool = getToolByName(context, 'portal_url')
    portal = urltool.getPortalObject()
    if context == portal:
        return None
    parent = context.aq_parent
    return getProjetsParent(parent)

class SchoolsVocabulary(object):
    grok.implements(IVocabularyFactory)
    def __call__(self, context):
        terms = []
        projets = getProjetsParent(context)
        #import pdb; pdb.set_trace()
        if projets == None:
            return None
        ecoles = projets.schools
        if ecoles:
            maListe = [x.strip() for x in ecoles.split(u'\n')]
            for ordre in sorted(maListe):
                school = ordre.split(',')
                if len(school)>0:
                    terms.append(SimpleVocabulary.createTerm(school[0], 
                                         str(remove_accents(school[0])),
                                         u"%s : %s"%(school[0],school[1])))
        #         ecoles = [(value[1],key) for key,value in schools.iteritems()]
        #         ecoles.sort()
        #         for school,school_id in ecoles:
        #             terms.append(SimpleVocabulary.createTerm(school_id, 
        #                             str(school_id),
        #                             u"%s : %s" % (school_id,school)))
        return SimpleVocabulary(terms)
grok.global_utility(SchoolsVocabulary, name=u"ageliaco.rd2.schools")
    
class SchoolOrdreVocabulary(object):
    grok.implements(IVocabularyFactory)
    def __call__(self, context):
        terms = []
        projets = getProjetsParent(context)
        #import pdb; pdb.set_trace()
        if projets == None:
            return None
        ecoles = projets.schools
        if ecoles:
            maListe = [x.strip() for x in ecoles.split(u'\n')]
            for ordre in sorted(maListe):
                school = ordre.split(',')
                if len(school)>0:
                    terms.append(SimpleVocabulary.createTerm(school[0], 
                                         str(remove_accents(school[0])),
                                         school[2]))
        #         ecoles = [(value[1],key) for key,value in schools.iteritems()]
        #         ecoles.sort()
        #         for school,school_id in ecoles:
        #             terms.append(SimpleVocabulary.createTerm(school_id, 
        #                             str(school_id),
        #                             u"%s : %s" % (school_id,school)))
        return SimpleVocabulary(terms)
grok.global_utility(SchoolOrdreVocabulary, name=u"ageliaco.rd2.schoolOrdre")

class OrdresEnseignementVocabulary(object):
    grok.implements(IVocabularyFactory)
    def __call__(self, context):
        terms = []
        #import pdb; pdb.set_trace()
        urltool = getToolByName(context, 'portal_url')
        portal = urltool.getPortalObject()
        projets = getProjetsParent(context)
        if projets == None:
            return None
        filieres = projets.filieres
        if filieres:
            maListe = [x.strip() for x in filieres.split(u'\n')]
            for ordre in sorted(maListe):
                terms.append(SimpleVocabulary.createTerm(ordre, 
                                         str(remove_accents(ordre)),
                                         ordre))
        #         for ordre in sorted(ordres.keys()):
        #             terms.append(SimpleVocabulary.createTerm(ordre, 
        #                             str(ordre),
        #                             ordres[ordre]))
        #import pdb; pdb.set_trace()

        return SimpleVocabulary(terms)
grok.global_utility(OrdresEnseignementVocabulary, name=u"ageliaco.rd2.ordres")

class DomainesEnseignementVocabulary(object):
    grok.implements(IVocabularyFactory)
    def __call__(self, context):
        terms = []
        #import pdb; pdb.set_trace()
        urltool = getToolByName(context, 'portal_url')
        portal = urltool.getPortalObject()
        projets = getProjetsParent(context)
        if projets == None:
            return None
        domaines = projets.domaines
        if domaines:
            maListe = [x.strip() for x in domaines.split(u'\n')]
            for ordre in sorted(maListe):
                terms.append(SimpleVocabulary.createTerm(ordre, 
                                         str(remove_accents(ordre)),
                                         ordre))
        return SimpleVocabulary(terms)
grok.global_utility(DomainesEnseignementVocabulary, name=u"ageliaco.rd2.domaines")

class DisciplinesVocabulary(object):
    grok.implements(IVocabularyFactory)
    def __call__(self, context):
        terms = []
        #import pdb; pdb.set_trace()
        urltool = getToolByName(context, 'portal_url')
        portal = urltool.getPortalObject()
        projets = getProjetsParent(context)
        if projets == None:
            return None
        disciplines = projets.disciplines
        if disciplines:
            maListe = [x.strip() for x in disciplines.split(u'\n')]
            #import pdb; pdb.set_trace()
            for ordre in sorted(maListe):
                terms.append(SimpleVocabulary.createTerm(ordre, 
                                         str(remove_accents(ordre)),
                                         ordre))
        return SimpleVocabulary(terms)
grok.global_utility(DisciplinesVocabulary, name=u"ageliaco.rd2.disciplines")

class SponsorshipVocabulary(object):
    grok.implements(IVocabularyFactory)
    def __call__(self, context):
        terms = []
        urltool = getToolByName(context, 'portal_url')
        portal = urltool.getPortalObject()
        projets = getProjetsParent(context)
        if projets == None:
            return None
        sponsorships = projets.sponsorships
        if sponsorships:
            maListe = [x.strip() for x in sponsorships.split(u'\n')]
            for ordre in sorted(maListe):
                terms.append(SimpleVocabulary.createTerm(ordre, 
                                         str(remove_accents(ordre)),
                                         ordre))
        #         for sponsorship in sorted(sponsorships.keys()):
        #             terms.append(SimpleVocabulary.createTerm(sponsorship, 
        #                             str(sponsorship), 
        #                             sponsorships[sponsorship][0]))
        return SimpleVocabulary(terms)
grok.global_utility(SponsorshipVocabulary, name=u"ageliaco.rd2.sponsorship")


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
                    terms.append(
                        SimpleVocabulary.createTerm(member_id, 
                            str(member_id), member_name
                            )
                        )
            
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
                    terms.append(
                        SimpleVocabulary.createTerm(member_id, 
                            str(member_id), member_name
                            )
                        )
            
        return SimpleVocabulary(terms)    


@grok.provider(IContextSourceBinder)
def possibleAttendees(context):
    # auteurs + supervisors
    cycle = None
    terms = []
    parent = context.aq_parent 
    #import pdb; pdb.set_trace()
    if context.portal_type == 'ageliaco.rd2.cycle':
        cycle = context
    elif context.portal_type == 'ageliaco.rd2.note':
        cycle = context.aq_parent
    else:
        return  SimpleVocabulary(terms) 
    mt = getToolByName(context, 'portal_membership')
    for supervisor in cycle.supervisor:
        member =  mt.getMemberById(supervisor)
        if member:
            name = member.getProperty('fullname')
            terms.append(SimpleVocabulary.createTerm(supervisor, 
                                str(supervisor), 
                                name))
    catalog = getToolByName(context, 'portal_catalog')
    auteurBrains = catalog(portal_type='ageliaco.rd2.auteur',
                        path={'query': '/'.join(cycle.getPhysicalPath()), 'depth': 1})
    for brain in auteurBrains:
        member = brain.id
        if brain.has_key('firstname') and brain.has_key('lastname'):
            name = "%s %s" % (brain.lastname,brain.firstname)
        else:
            name = brain.id
        terms.append(SimpleVocabulary.createTerm(brain.id, 
                            str(brain.id), 
                            name))
        terms = sorted(terms, key=lambda name: name.title)
    return SimpleVocabulary(terms)            


class INote(form.Schema):
    """
    Note de suivi de rendez-vous
    """
    title = schema.TextLine(
            title=MessageFactory(u"Titre"),
            required=False,
        )    

    form.widget(presence=CheckBoxFieldWidget)
    presence = schema.List(
        title=MessageFactory(u"Personnes présentes"),
        value_type=schema.Choice(source=possibleAttendees),
        required=False,
    )
    form.widget(absence=CheckBoxFieldWidget)
    absence = schema.List(
            title=MessageFactory(u"Personnes absentes excusées"),
            #default=[],
            value_type=schema.Choice(source=possibleAttendees),
            required=False,
        )
    
    #form.mode(sansexcuse='hidden')
    dexteritytextindexer.searchable('presentation')
    presentation = RichText(
            title=MessageFactory(u"Notes de séance"),
            description=MessageFactory(
                u"Compte-rendu de l'avancement du projet"),
            required=False,
            )    

@form.default_value(field=INote['title'])
def startDefaultValue(data):
    # To get hold of the folder, do: context = data.context
    context = data.context
    day =  datetime.datetime.today()
    return context.id + "_Note-" + day.strftime("%Y-%m-%d")

@grok.subscribe(INote, IObjectAddedEvent)
def setPresence(note, event):
    sansexcuse = []
    cycle = note.aq_parent
    attendees = possibleAttendees(cycle)
    #import pdb; pdb.set_trace()
    for item in attendees._terms:
        if item.token not in note.presence and item.token not in note.absence:
            sansexcuse.append(item.token)
    setattr(note,'sansexcuse',sansexcuse)  
    
    return 
    
class IAuteur(form.Schema):
    """
    Auteur de projet
    """
    # removed because if user is removed from ldap it generates an error
    #
    #form.widget(id=AutocompleteFieldWidget)
    #     id = schema.Choice(
    #             title=MessageFactory(u"Pseudo"),
    #             description=MessageFactory(u"Login EDU"),
    #             vocabulary=u"plone.principalsource.Users",
    #             required=True,
    #         )
    id = schema.TextLine(
            title=MessageFactory(u"id"),
            description=MessageFactory(u"Identifiant (login EDU)"),
            required=True,
        )


    dexteritytextindexer.searchable('lastname')
    lastname = schema.TextLine(
            title=MessageFactory(u"Nom"),
            description=MessageFactory(u"Nom de famille"),
            required=True,
        )

    dexteritytextindexer.searchable('firstname')
    firstname = schema.TextLine(
            title=MessageFactory(u"Prénom"),
            description=MessageFactory(u"Prénom"),
            required=True,
        )

    dexteritytextindexer.searchable('school')
    school = schema.Choice(
            title=MessageFactory(u"Ecole"),
            description=MessageFactory(u"Etablissement scolaire de référence"),
            vocabulary=u"ageliaco.rd2.schools",
            default='',
            required=True,
        )


    dexteritytextindexer.searchable('disciplines')
    form.widget('disciplines', SelectWidget, multiple='multiple', size=10) 
    disciplines = schema.List(
        title=MessageFactory(u"discipline(s) enseignée(s)"),
        description=MessageFactory(u"Sélectionnez la(s) discipline(s) enseignée(s)"),
        value_type=schema.Choice(vocabulary=u"ageliaco.rd2.disciplines"),
        required=False,
        )

    email = schema.TextLine(
            title=MessageFactory(u"Email"),
            description=MessageFactory(u"Adresse courrielle"),
            required=True,
        )

    phone = schema.TextLine(
            title=MessageFactory(u"Téléphone"),
            description=MessageFactory(u"Téléphone"),
            required=False,
        )

            
    sponsorasked = schema.Choice(
            title=MessageFactory(u"Dégrèvement demandé"),
            description=MessageFactory(
                u"Dégrèvement total demandé pour cet auteur " + 
                u"(1 heure ~= 2 x 1/2 journées/mois sur le projet)"
                ),
            vocabulary=u"ageliaco.rd2.sponsorship",
            required=True,
            default='',
        )
    
    #dexterity.read_permission(sponsorRD='cmf.ReviewPortalContent')
    dexterity.write_permission(sponsorRD='cmf.ManagePortal')
    sponsorRD = schema.Choice(
            title=MessageFactory(u"Dégrèvement R&D"),
            description=MessageFactory(
                u"Dégrèvement R&D attribué pour cet auteur"),
            vocabulary=u"ageliaco.rd2.sponsorship",
            required=False,
        )
    
    #dexterity.read_permission(sponsorSchool='cmf.ReviewPortalContent')
    dexterity.write_permission(sponsorSchool='cmf.ManagePortal')
    sponsorSchool= schema.Choice(
            title=MessageFactory(u"Dégrèvement Ecole"),
            description=MessageFactory(
                u"Dégrèvement école attribué pour cet auteur"),
            vocabulary=u"ageliaco.rd2.sponsorship",
            required=False,
        )

class Auteur(object):
    grok.implements(IAuteur)
    def __init__(self,id,lastname,firstname,email,phone='',
            school='',sponsorasked='',sponsorRD='',sponsorSchool=''): 
        self.id = id
        self.lastname = lastname
        self.firstname = self.firstname
        self.email = email
        self.sponsorasked = sponsorasked
        self.sponsorRD = sponsorRD
        self.sponsorSchool = sponsorSchool
        self.school = school
        
    def __repr__(self):
        return "<Auteur : login = %s>" % self.id
        
        
        
@grok.subscribe(IAuteur, IObjectAddedEvent)
def setAuteur(auteur, event):
    portal_url = getToolByName(auteur, 'portal_url')
    acl_users = getToolByName(auteur, 'acl_users')
    portal = portal_url.getPortalObject() 
#     cycle = auteur.aq_parent
#     cycle.manage_addLocalRoles(auteur.id, ['Reader',])


class IProjet(form.Schema):
    """
    Projet RD
    """
    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
            title=MessageFactory(u"Titre"),
            description=MessageFactory(
                u"Titre succinct"
                ),
            required=True,
            max_length=80,
        )
    dexteritytextindexer.searchable('description')
    description = schema.Text(
            title=MessageFactory(u"Sous-titre"),
            description=MessageFactory(
                u"Sous-titre ou titre détaillé"
                ),
            required=True,
        )
    start = schema.TextLine(
            title=MessageFactory(u"Année"),
            description=MessageFactory(
                u"L'année à laquelle le projet a commencé ou devrait commencer"
                ),
            required=True,
        )

    dexterity.read_permission(duration='cmf.ReviewPortalContent')
    dexterity.write_permission(duration='cmf.ReviewPortalContent')
    duration = schema.Int(
            title=MessageFactory(u"Durée"),
            description=MessageFactory(
                u"Durée (en années) du projet, prévue ou effective"),
            required=True,
        )
    
    dexteritytextindexer.searchable('presentation')
    presentation = RichText(
            title=MessageFactory(u"Présentation"),
            description=MessageFactory(
                u"Présentation synthétique du projet (présentation publiée)"),
            required=True,
        )    

    #     picture = NamedImage(
    #             title=MessageFactory(u"Chargez une image pour le projet"),
    #             required=False,
    #         )

    lien = schema.TextLine(
            title=MessageFactory(u"Lien vers la réalisation"),
            description=MessageFactory(u"Lien extérieur vers la réalisation"),
            required=False,
        )

@indexer(IProjet)
def projet_description(object):
    return object.text[:]
grok.global_adapter(projet_description, name="Description")
    
@indexer(IProjet)
def projet_title(object):
    return object.title
grok.global_adapter(projet_title, name="Title")
    
@grok.subscribe(IProjet, IObjectAddedEvent)
def setRealisation(projet, event):
    admid = 'realisation'
    if admid not in projet.keys():
        rea = projet.invokeFactory("Folder", id=admid, title=u'Réalisation')
        #projet[admid] = rea
    
    return 
#request.response.redirect(cycles.absolute_url() + '++add++ageliaco.rd2.cycle')

@grok.provider(IContextSourceBinder)
def activeProjects(context):
    catalog = getToolByName(context, 'portal_catalog')
    cat = catalog(portal_type='ageliaco.rd2.projet',
                   review_state='encours',
                   sort_on='sortable_title')
    terms = []
                
    for brain in cat:
        terms.append(SimpleVocabulary.createTerm(brain.getPath(), 
            brain.id, brain.Title))
    return SimpleVocabulary(terms) 
#SimpleVocabulary(
#   [SimpleVocabulary.createTerm(x.id, x.getURL(), x.Title) for x in cat])


class PorteparoleNotInParticipants(Invalid):
    __doc__ = _(u"Le porte-parole n'est pas dans les participants")

    
class ICycle(form.Schema):
    """
    Cycle de projet RD
    """
    
    # -*- Your Zope schema definitions here ... -*-
    form.mode(id='hidden')
    id = schema.TextLine(
            title=MessageFactory(u"Identifiant"),
            description=MessageFactory(
                u"Ne pas changer celui donné par défaut! Merci!"),
            required=True,
        )
        
    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
            title=MessageFactory(u"Titre"),
            description=MessageFactory(u"Titre bref du projet"),
            required=True,
            default=u'',
            max_length=80,
        )
        
    dexteritytextindexer.searchable('description')
    description = schema.Text(
            title=MessageFactory(u"Synopsis"),
            description=MessageFactory(
                u"Présentation du projet en un paragraphe"),
            required=False,
            default=u'',
        )
        
    #form.widget(projet=AutocompleteFieldWidget)
    projet = schema.Choice(
            title=MessageFactory(u"Projet existant"),
            description=MessageFactory(
                u"Lien vers un projet existant (en cas de reconduction)"),
            source=activeProjects,
            required=False,
            default=u'',
        )
            
    dexterity.write_permission(supervisor='cmf.ReviewPortalContent')
    form.widget(supervisor=CheckBoxFieldWidget)
    supervisor = schema.List(
            title=MessageFactory(u"Superviseur(s) R&D"),
            description=MessageFactory(
                u"Personne(s) de R&D qui supervise(nt) ce projet"),
            value_type=schema.Choice(source=GroupMembers('Supervisor')),
            required=False,
            missing_value=(),
            default=[],
        )
        
    dexteritytextindexer.searchable('domaines')
    form.widget('domaines', SelectWidget, multiple='multiple', size=10) 
    domaines = schema.List(
        title=MessageFactory(u"Domaine d'étude"),
        description=MessageFactory(u"Sélectionnez le(s) domaine(s) concerné(s)"),
        value_type=schema.Choice(vocabulary=u"ageliaco.rd2.domaines"),
        required=False,
        )

    dexteritytextindexer.searchable('disciplines')
    form.widget('disciplines', SelectWidget, multiple='multiple', size=10) 
    disciplines = schema.List(
        title=MessageFactory(u"Discipline visée"),
        description=MessageFactory(u"Sélectionnez la(s) discipline(s) concernée(s)"),
        value_type=schema.Choice(vocabulary=u"ageliaco.rd2.disciplines"),
        required=False,
        )

    #     dexteritytextindexer.searchable('discipline')
    #     discipline = schema.Text(
    #             title=MessageFactory(u"Discipline(s)"),
    #             description=MessageFactory(
    #                 u"Discipline(s) concernée(s) par le projet (une par ligne)"),
    #             required=False,
    #             default=u'',
    #         )
        
    dexteritytextindexer.searchable('presentation')
    presentation = RichText(
            title=MessageFactory(u"Objectifs généraux du projet"),
            description=MessageFactory(
                u"Changements et actions concrets auxquels " +
                u"on peut s'attendre à court et à long terme"
                ),
            required=False,
            default=u'',
        )    
        
    # contexte Fieldset
    form.fieldset(
        'contexte',
        label=_(u"Contexte"),
        fields=['problematique', 'experiences', 'besoin']
    )

    dexteritytextindexer.searchable('problematique')
    problematique = RichText(
            title=MessageFactory(u"Problématique"),
            description=MessageFactory(
                u"Quel postulat et/ou quelles hypothèses " +
                u"sont à l'origine du projet?"
                ),
            required=False,
            default=u'',
        )    

    dexteritytextindexer.searchable('experiences')
    experiences = RichText(
            title=MessageFactory(u"Expériences préalables"),
            description=MessageFactory(
                u"Sur quelles expériences ou connaissances préalables " +
                u"repose le projet? Quels sont le travail et la réflexion " +
                u"déjà entamés dans le domaine de la recherche proposée " +
                u"(bibliographie, inventaire d'expériences, etc.)"
                ),
            required=False,
            default=u'',
        )    

    dexteritytextindexer.searchable('besoin')
    besoin = RichText(
            title=MessageFactory(u"Origine du besoin"),
            description=MessageFactory(
                u"Quels éléments de la situation présente sont à l'origine " +
                u"du besoin exprimé ? Justification et preuves du besoin : " +
                u"plan cadre, directives, etc."
                ),
            required=False,
            default=u'',
        )    

    # Objectifs Fieldset
    form.fieldset(
        'objectifs',
        label=_(u"Objectifs"),
        fields=['cible', 'forme']
    )
    
    #dexteritytextindexer.searchable('cible')
    #form.widget(cible=CheckBoxFieldWidget)
    form.widget('cible', SelectWidget, multiple='multiple', size=10) 
    cible = schema.List(
        title=MessageFactory(u"Filière visée"),
        description=MessageFactory(u"Sélectionnez la filière concernée"),
        value_type=schema.Choice(vocabulary=u"ageliaco.rd2.ordres"),
        required=False,
        )
    
    
    dexteritytextindexer.searchable('forme')
    forme = RichText(
            title=MessageFactory(u"Forme du produit fini au terme du projet"),
            description=MessageFactory(
                u"Quels types de documents seront déposés sur le site de R&D?"+
                u" (documents maître, documents élève, documents de référence)"
                ),
            required=False,
            default=u'',
        )    

    # Organisation Fieldset
    form.fieldset(
        'organisation',
        label=_(u"Organisation"),
        fields=['duree','planification', 'production', 'plan', 
            'repartition', 'modalites', 'participants','porteparole']
    )

    duree = schema.Int(
            title=MessageFactory(u"Durée du projet (en années scolaires)"),
            description=MessageFactory(
                u"Durée estimée du projet en années scolaires"),
            default = 1,
            required=False,
        )

    dexteritytextindexer.searchable('planification')
    planification = RichText(
            title=MessageFactory(u"Planification des objectifs par année"),
            description=MessageFactory(
                u"Organisation des objectifs sur toute la durée du projet"),
            required=False,
            default=u'',
        )    

    dexteritytextindexer.searchable('production')
    production = RichText(
            title=MessageFactory(u"Production pour l'année à venir"),
            description=MessageFactory(
                u"Matériel produit pour les élèves et pour les maîtres"),
            required=False,
            default=u'',
        )    
    
    dexteritytextindexer.searchable('plan')
    plan = RichText(
            title=MessageFactory(u"Echéancier pour l'année à venir"),
            description=MessageFactory(
                u"Planification mensuelle détaillée : phases d'élaboration," +
                u" phases de test, phase de finalisation"
                ),
            required=False,
            default=u'',
        )    
    
    dexteritytextindexer.searchable('repartition')
    repartition = RichText(
            title=MessageFactory(u"Répartition et rôles"),
            description=MessageFactory(
                u"Répartition prévue des tâches entre participants"),
            required=False,
            default=u'',
        )    

    dexteritytextindexer.searchable('modalites')
    modalites = RichText(
            title=MessageFactory(u"Modalités de travail"),
            description=MessageFactory(
                u"Plage horaire commune : demande du groupe de travail " +
                u"auprès des établissements concernés"
                ),
            required=False,
            default=u'',
        )    

    dexteritytextindexer.searchable('participants')
    participants = schema.Text(
            title=MessageFactory(u"Participants pour l'année à venir"),
            description=MessageFactory(
    u"""Mettre le login EDU de chaque participant, un par ligne (ex: 'edu-dupontm').
        La liste des auteurs sera générée automatiquement.
        En cas d'erreur (si l'identifiant n'est pas dans l'annuaire), cf. la doc
        pour voir comment tester un identifiant, mais surtout il faut supprimer
        l'identifiant posant un problème pour pouvoir sauvegarder la session !!!
        """
                ),
            required=False,
            default=u'',
        )    

    porteparole = schema.TextLine(
            title=MessageFactory(u"Personne de contact"),
            description=MessageFactory(
                u"Personne de contact du projet pour R&D (mettre le login EDU)"),
            required=False,
            default=u'',
        )

    @invariant
    def validatePorteparole(data):
        if data.porteparole and not data.participants and \
                data.porteparole not in data.participants.split():
            raise PorteparoleNotInParticipants(_(
                u"La personne de contact doit faire partie des participants"))
                
        

def idDefaultFromContext(context):
    """context must be a ageliaco.rd2.projet object"""
    newId = ''
    indice = 1
    start = ''
    
    
    catalog = getToolByName(context, 'portal_catalog')
    cat = catalog.unrestrictedSearchResults(
        object_provides= ICycle.__identifier__,
        path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
        sort_on="modified", sort_order="reverse"
        )  

    if hasattr(context,'start'):
        start = context.start
    else:
        start = str(datetime.datetime.today().year)

    if len(cat): #first is last generated,if it is not a copy from an old cycle
        for cycle in cat:
            lastId = cycle.id
            #try:
            index = lastId.split('-')[1]
            newId =  "%s-%s" % (start,index)
            if (newId not in context.objectIds()):
                return newId
            #except:
            #    print "oups not good"
    index = len(cat)
            
    newId =  "%s-%s" % (start,index)
    while newId in context.objectIds():
        index += 1
        newId =  "%s-%s" % (start,index)
        
    return newId
    
@form.default_value(field=ICycle['id'])
def idDefaultValue(data):
    # To get hold of the folder, do: context = data.aq_parent
    #import pdb; pdb.set_trace()
    context = data.context

    newId = idDefaultFromContext(context)
    
    return newId

    
@grok.subscribe(ICycle, IObjectModifiedEvent)
def setSupervisor(cycle, event):
    if not cycle.supervisor:
        return
    if IRoleManager.providedBy(cycle):
        for supervisor in cycle.supervisor:
            cycle.manage_addLocalRoles(supervisor, 
                ['Reader', 'Contributor', 'Editor','Reviewer']
                )
        log("Role added to %s for %s"%(cycle.id,cycle.supervisor))


def checkAuteurs(cycle, value=u""):
    if value:
        newauteurs = value.split('\n')
    else:
        newauteurs = []
    newparticipants = {}
    #import pdb; pdb.set_trace()
    for ligne in newauteurs:
        ligne = ligne.strip()
        #import pdb; pdb.set_trace()
        try:
            login = ligne
            if login :
                newparticipants[login] = login
        except:
            raise ActionExecutionError(
                Invalid(_(u"""Il y a un problème avec l'identifiant : %s,
corrigez l'erreur ou supprimez la ligne pour pouvoir sauvegarder les changements et
prenez contact avec R&D pour les identifiants qui ne passent pas!""" %
                     ligne
                     )
                )
            )
    return newparticipants
    
def aboutAuteurs(cycle, value=u""):
    newparticipants = checkAuteurs(cycle,value)
    #import pdb; pdb.set_trace()
    catalog = getToolByName(cycle, 'portal_catalog')
    cyclepath = '/'.join(cycle.getPhysicalPath())
    auteurBrains = catalog(portal_type='ageliaco.rd2.auteur',
                    path={'query': cyclepath, 'depth': 1})
    mt = getToolByName(cycle, 'portal_membership')
    mdata = getToolByName(cycle, 'portal_memberdata')
    mdataIds = mdata.propertyIds()
    
    for brain in auteurBrains:
        if brain.id.upper() in [id.upper() for id in newparticipants.keys()]:
            if brain.id in newparticipants.keys():
                del newparticipants[brain.id]
            elif brain.id.upper() in newparticipants.keys():
                del newparticipants[brain.id.upper()]
            elif brain.id.lower() in newparticipants.keys():
                del newparticipants[brain.id.lower()]
            continue
        
        else: #auteur removed
            cycle.manage_delLocalRoles([brain.id])
            #import pdb; pdb.set_trace()
            if brain.id in cycle.keys():
                del cycle[brain.id]
                cycle.reindexObject()
    
        #try:
    acl_users = getToolByName(cycle, 'acl_users')
    ldap_active = False
    if 'ldap-plugin' in acl_users:
        acl = acl_users['ldap-plugin'].acl_users
        ldap_active = True
    else:
        acl = acl_users.source_users
    #import pdb; pdb.set_trace()
    for login in newparticipants.keys():
        ok = False
        member = mt.getMemberById(str(login))
        if not member: # ldap EEL keeps login in upper !!!
            member = mt.getMemberById(str(login).upper())
        if member:
            id = member.getProperty('id')
            if 'lastname' in mdataIds:
                lastname = utf_8(member.getProperty('lastname'))
            else:
                lastname = ''
            #import pdb;pdb.set_trace()
            if 'firstname' in mdataIds:
                firstname = utf_8(member.getProperty('firstname'))
            else:
                firstname = ''
            if 'email' in mdataIds:
                email = member.getProperty('email')
            else:
                email = ''
            auteur = createContent("ageliaco.rd2.auteur", 
                id = id,
                title = u"%s %s" % (lastname,firstname),
                firstname = firstname,
                lastname = lastname,
                email = email,)
            cycle[auteur.id]=auteur
            cycle.manage_setLocalRoles(auteur.id, ['Reader','Owner','Reviewer'])
            cycle.reindexObjectSecurity()
            #print "OK => id %s is in !!!" % auteur.id
            ok = True

                
        if not ok:
            print "no member found for %s" % login
            return u"""Il y a un problème avec l'identifiant : %s,
corrigez l'erreur ou supprimez la ligne pour pouvoir sauvegarder les changements et
prenez contact avec R&D pour les identifiants qui ne passent pas!""" % login
        return ""

 
@grok.subscribe(ICycle, IObjectAddedEvent)
def setAuteurs(cycle,event):
    aboutAuteurs(cycle, cycle.participants)
    #return cycle.absolute_url()+'/Auteurs'

def okToSubmit(form):
    #import pdb; pdb.set_trace()
    workflowTool = getToolByName(form.context, "portal_workflow")
    status = workflowTool.getStatusOf("rd2.cycle-workflow",form.context)['review_state']
    return status == 'draft'
 
class EditForm(dexterity.EditForm):
    grok.context(ICycle)

        
    @button.buttonAndHandler(_(u'Sauvegarder'))
    def handleApply(self, action):
        data, errors = self.extractData()
        #import pdb; pdb.set_trace()
        # Some additional validation
        if 'participants' in data:
            cycle = self.context 
            if 'porteparole' in data and data['porteparole'] and data['porteparole'] not in data['participants'].split():
                raise ActionExecutionError(Invalid(_(u"Le porte-parole (%s) ne se trouve pas parmi les participants!" % data['porteparole'])))
            executionErrors = aboutAuteurs(cycle, data['participants'])
            if executionErrors:
                raise ActionExecutionError(Invalid(_(executionErrors)))

        if errors:
            self.status = self.formErrorsMessage
            return
        else:
            processInputs(self.request)
            extrapath = ''
            if not cycle.participants and not data['participants']:
                extrapath = ''
            elif data['participants'] != cycle.participants:
                # changes were made
                extrapath = '/'+'Auteurs'
            #save changes
            self.applyChanges(data)
            cycle.reindexObject()
            return self.request.response.redirect(cycle.absolute_url()+extrapath)

    def updateActions(self):
        super(EditForm, self).updateActions()
        if 'soumettre' in self.actions.keys():
            self.actions['soumettre'].addClass("soumissionprojet")
            self.actions['soumettre'].title = u'Soumettre le projet (ne sera plus modifiable après soumission!)'

class AddForm(dexterity.AddForm):
    grok.name('ageliaco.rd2.cycle')
    label = u"Proposition de projet"

    @button.buttonAndHandler(_(u'Sauvegarder'))
    def handleApply(self, action):
        data, errors = self.extractData()
        extrapath = ''
        #import pdb; pdb.set_trace()
        # Some additional validation

        if errors:
            self.status = self.formErrorsMessage
            return
        else:
            processInputs(self.request)
            #save changes
            cycle = self.createAndAdd(data)
            extrapath = '/' + cycle.id + '/'+'Auteurs'
            #cycle.index()
            cycle = self.context[cycle.id]    
            if 'participants' in data:
                if not checkAuteurs(cycle, data['participants']):
                    extrapath = ''
            #import pdb; pdb.set_trace()
        return self.request.response.redirect(cycle.absolute_url()+extrapath)


class AuteursEditForm(crud.EditForm):
    """ Pigeonhole edit form.  
        Just a normal CRUD form without the form title or edit button.
    """
    
    label = u"""Complétez les informations

    école : attachement administratif, 
    dégrèvement demandé : une heure de dégrèvement correspond 
                          à 2 demi-journées de travail par mois.
    Numéro de téléphone (facultatif)
    """

    
    buttons = crud.EditForm.buttons.copy().omit('delete')
    handlers = crud.EditForm.handlers.copy()

    @button.buttonAndHandler(_(u"Retour à la proposition de projet"),
        name= "Cancel"
        )
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """
        #print self.request['URL1']
        cycleurl = self.request['URL1']
        return self.request.response.redirect(cycleurl)

def adapt_schema2security(field):
    sm = getSecurityManager()
    reviewField = field.Fields(IAuteur).select('sponsorRD')
    if not sm.checkPermission(ManagePortal, reviewField):
        #print "NO MANAGE ROLE FOR USER"
        return field.Fields(IAuteur).select('phone','email','school',
            'sponsorasked')
    #print "MANAGE ROLE FOR USER"
    return field.Fields(IAuteur).select('phone','email','school',
            'sponsorasked', 'sponsorRD', 'sponsorSchool')


class AuteursForm(crud.CrudForm,grok.View):
    #update_schema = IAuteur
    #view_schema = field.Fields(IAuteur).select('id')
    update_schema = field.Fields(IAuteur).select('id','firstname','lastname',
            'phone','email','school',
            'sponsorasked', 'sponsorRD', 'sponsorSchool')
    
    #field.Fields(IAuteur).select('phone','email','school','sponsorasked')
    addform_factory = crud.NullForm
    editform_factory = AuteursEditForm
    grok.context(ICycle)
    grok.require('zope2.View')
    grok.name('Auteurs')

    def updateWidgets(self):
        sm = getSecurityManager()
        workflowTool = getToolByName(self.context, "portal_workflow")
        status = workflowTool.getStatusOf("rd2.cycle-workflow", self.context)
        state = status["review_state"]
        #import pdb; pdb.set_trace()
        self.update_schema["id"].mode = z3c.form.interfaces.DISPLAY_MODE
        self.update_schema["firstname"].mode = z3c.form.interfaces.DISPLAY_MODE
        self.update_schema["lastname"].mode = z3c.form.interfaces.DISPLAY_MODE
        if not sm.checkPermission(ManagePortal, self.context):
            self.update_schema["sponsorRD"].mode = z3c.form.interfaces.DISPLAY_MODE
            self.update_schema["sponsorSchool"].mode = z3c.form.interfaces.DISPLAY_MODE
        else:
            self.update_schema["sponsorRD"].mode = z3c.form.interfaces.INPUT_MODE
            self.update_schema["sponsorSchool"].mode = z3c.form.interfaces.INPUT_MODE
        if state != "draft":
            self.update_schema["sponsorasked"].mode = z3c.form.interfaces.DISPLAY_MODE
        else:
            self.update_schema["sponsorasked"].mode = z3c.form.interfaces.INPUT_MODE
            
    def get_items(self):
        retour = sorted([(id,obj) for id, obj in self.context.objectItems() \
                        if obj.portal_type=='ageliaco.rd2.auteur'],
                    key=lambda x: x[1].lastname
                )
        return retour


class EditAuteurs(layout.FormWrapper):
    form = AuteursForm
    grok.context(ICycle)
    grok.require('zope2.View')
    grok.name('EditAuteurs')
    

# class CSSHeadSlotView(BrowserView):
#     implements(Interface)
#     # Nested templates which render different parts of template
#     head_slot_template = ViewPageTemplateFile("interface_templates/css_head_slot.pt")
#          
#     def render_css_head_slot(self):
#         return self.css_head_slot_template()
# 
# class JSHeadSlotView(BrowserView):
#     implements(Interface)
#     # Nested templates which render different parts of template
#     js_head_slot_template = ViewPageTemplateFile("interface_templates/js_head_slot.pt")
#          
#     def render_js_head_slot(self):
#         return self.js_head_slot_template()
# 
# class ProjetMenuView(BrowserView):
#     implements(Interface)
#     # Nested templates which render different parts of template
#     projet_menu_template = ViewPageTemplateFile("interface_templates/projet_menu.pt")
#     
#     def render_projet_menu(self):
#         return self.projet_menu_template()
    
       
class InterfaceView(grok.View,Form):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('interface')
    objectPath = ''
    degrevements = {}
    withTotal = False
    multikey = '@@keywordview'
    indx = 'Subject'
    searchType = IProjet.__identifier__
    pathDepth = 0
    allauthors = "cycle,author.id,author.lastname,author.firstname," + \
        "author.school,ordre,author.sponsorasked,author.sponsorRD," + \
        "author.sponsorSchool"
    keyword_dict = {}

    projets_menu_template = ViewPageTemplateFile("interface_templates/projets_menu.pt")
    cycle_list_template = ViewPageTemplateFile("interface_templates/cycle_list.pt")
    cycles_by_states_template = ViewPageTemplateFile("interface_templates/cycles_by_states.pt")
    list_auteurs_template = ViewPageTemplateFile("interface_templates/list_auteurs.pt")    
    css_head_slot_template = ViewPageTemplateFile("interface_templates/css_head_slot.pt")
    js_head_slot_template = ViewPageTemplateFile("interface_templates/js_head_slot.pt")
    projet_menu_template = ViewPageTemplateFile("interface_templates/projet_menu.pt")
    projets_table_template = ViewPageTemplateFile("projets_templates/projets-table.pt")
    cycleauteurs_template = ViewPageTemplateFile("interface_templates/cycleauteurs.pt")
    localauteurs_template = ViewPageTemplateFile("cycle_templates/localauteurs.pt")
    notes_template = ViewPageTemplateFile("interface_templates/notes.pt")
    auteurs_template = ViewPageTemplateFile("interface_templates/auteurs.pt")
    cycles_auteurs_table_template = \
        ViewPageTemplateFile("projet_templates/cycles_auteurs_table.pt")
        
    def render_cycles_auteurs_table(self):
        return self.cycles_auteurs_table_template()
        
    def render_auteurs(self):
        return self.auteurs_template()
        
    def render_notes(self):
        return self.notes_template()
        
    def render_localauteurs(self):
        return self.localauteurs_template()
                
    def render_cycleauteurs(self):
        return self.cycleauteurs_template()
                    
    def render_projets_table(self):
        return self.projets_table_template()
    
    def render_projet_menu(self):
        return self.projet_menu_template()
         
    def render_js_head_slot(self):
        return self.js_head_slot_template()
         
    def render_css_head_slot(self):
        return self.css_head_slot_template()
         
    def render_cycle_list(self):
        return self.cycle_list_template()
    
    def render_cycles_by_states(self):
        return self.cycles_by_states_template()
    
    def render_list_auteurs(self):
        return self.list_auteurs_template()
    
    def set2float(self,value):
        if not value:
            return 0.0
        else:
            return float(value)
    
    def auteur_disciplines(self,auteur):
        if hasattr(auteur,'disciplines') and type(auteur.disciplines)==list:
            return auteur.disciplines
        return []

    def auteur_disciplines_str(self,auteur):
        if hasattr(auteur,'disciplines') and type(auteur.disciplines)==list:
            ret = u""
            for disc in auteur.disciplines:
                ret += disc + u"\n"
            return ret
        return u""
    
            
    def whichState(self):
        if self.canReviewContent():
            return 'all'
        elif self.isAnonymous():
            return ['published']
        return  ['encours','published']

    def tags(self,brain):
        ret = ""
        subjects = sorted(brain.Subject)
        for sub in subjects:
            ret += sub
            ret += '\n'
        return ret

    #@view.memoize
    def disciplines(self,projectPath=""):
        #print projectPath
        context = aq_inner(self.context)
        #import pdb; pdb.set_trace()
        if not projectPath:
            projectPath = '/'.join(context.getPhysicalPath())
        catalog = getToolByName(self.context, 'portal_catalog')
        cat = catalog(object_provides=[ICycle.__identifier__],
                       path={'query': projectPath, 'depth': 2},
                       sort_on="modified", sort_order="reverse")
        disc = set()
        if len(cat):
            try:
                for cycle in cat:
                    obj = cycle.getObject()
                    if hasattr(obj,'disciplines') and obj.disciplines:
                        dom = set(obj.disciplines)
                        disc = disc | dom #union of sets
            except Unauthorized:
                print projectPath
                return ""
        #import pdb; pdb.set_trace()
        ret = ""
        for d in sorted(disc):
            ret += d
            ret += "\n"            
        return ret

    #@view.memoize
    def domaines(self,projectPath=''):
        context = aq_inner(self.context)
        #import pdb; pdb.set_trace()
        if not projectPath:
            projectPath = '/'.join(context.getPhysicalPath())
        catalog = getToolByName(self.context, 'portal_catalog')
        cat = catalog(object_provides=[ICycle.__identifier__],
                       path={'query': projectPath, 'depth': 2},
                       sort_on="modified", sort_order="reverse")
        disc = set()
        if len(cat):
            try:
                for cycle in cat:
                    obj = cycle.getObject()
                    if hasattr(obj,'domaines') and obj.domaines:
                        dom = set(obj.domaines)
                        disc = disc | dom #union of sets
            except Unauthorized:
                print projectPath
                return ""
        #import pdb; pdb.set_trace()
        ret = ""
        for d in sorted(disc):
            ret += d
            ret += "\n"            
        return ret
        
    def isAnonymous(self):
        mt = getToolByName(self.context, 'portal_membership')
        return mt.isAnonymousUser()
        
    def isOwner(self):
        mt = getToolByName(self.context, 'portal_membership')
        if mt.isAnonymousUser(): # the user has not logged in
            return False
        member = mt.getAuthenticatedMember()
        owner = self.context.getOwner()
        #print member, owner
        try:
            return member.getName() == owner.getName()
        except AttributeError: # getName: does it function with dexterity?
            return False
        
    # canReviewContent        
    def canReviewContent(self):
        return checkPermission('cmf.ReviewPortalContent', self.context)

    def canAddContent(self, context=None):
        if not context:
            context = self.context            
        return checkPermission('cmf.AddPortalContent', context)
        
    def canModifyContent(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)
                
    def setObjectPath(self, objectPath, withTotal = False):
        self.objectPath = objectPath
        self.withTotal = withTotal
        if withTotal:
            self.degrevements[objectPath] = [0.0,
                                             0.0,
                                             0.0,
                                             0.0]            
            
        return self.objectPath
        
    def getObjectPath(self):
        return self.objectPath
        
    @view.memoize    
    def notes(self, projectPath=''):
        """Return a catalog search result of authors from a project
        problem : same author appears several times 
        """
        context = aq_inner(self.context)
        #import pdb; pdb.set_trace()
        if not projectPath:
            projectPath = '/'.join(context.getPhysicalPath())
        catalog = getToolByName(self.context, 'portal_catalog')
        cat = catalog(object_provides=[INote.__identifier__],
                       path={'query': projectPath, 'depth': 3},
                       sort_on="modified", sort_order="reverse")
        
        #import pdb; pdb.set_trace()
        return cat
        
    @view.memoize    
    def authors(self, projectPath=''):
        """Return a catalog search result of authors from a project
        problem : same author appears several times 
        """
        auteurs = []
        auteurIDs = []
        context = aq_inner(self.context)
        #import pdb; pdb.set_trace()
        if not projectPath:
            projectPath = '/'.join(context.getPhysicalPath())
        catalog = getToolByName(self.context, 'portal_catalog')
        cat = catalog(object_provides=[IAuteur.__identifier__],
                       path={'query': projectPath, 'depth': 2},
                       sort_on="modified", sort_order="reverse")
        for auteur in cat:            
            if auteur.id not in auteurIDs:
                auteurs.append(auteur)
                auteurIDs.append(auteur.id)
        auteurs = sorted(auteurs, key=lambda author: author.lastname)
        #import pdb; pdb.set_trace()
        return auteurs
        
    def getSponsoring(self):
        if self.withTotal:
            return self.degrevements[self.objectPath]
        else:
            return {}

    @view.memoize    
    def ordre(self,school):
        factory = getUtility(IVocabularyFactory, 'ageliaco.rd2.schoolOrdre')
        vocabulary = factory(self.context)
        try:
            return vocabulary.getTerm(school).title
            
        except LookupError:
            return u''
        
    def sponsorasked(self,auteur):
        context = aq_inner(self.context)
        author = auteur.getObject()
        ordre = self.ordre(author.school)
        oneauthor = "\n%s,%s,%s,%s,%s,%s,%d,%d"% \
            (auteur.getPath().split('/')[-2],
            author.id,author.lastname,
            author.firstname,author.school,ordre,
            self.set2float(author.sponsorRD),
            self.set2float(author.sponsorSchool))
        self.allauthors += oneauthor
        if self.withTotal:
            self.degrevements[self.objectPath][0] += \
                self.set2float(author.sponsorasked)
            self.degrevements[self.objectPath][1] += \
                self.set2float(author.sponsorRD)
            self.degrevements[self.objectPath][2] += \
                self.set2float(author.sponsorSchool)
            self.degrevements[self.objectPath][3] += \
                self.set2float(author.sponsorSchool) + \
                            self.set2float(author.sponsorRD)
        return (author.sponsorasked,author.sponsorRD,author.sponsorSchool)
        
    @view.memoize
    def review_state(self):
        context = aq_inner(self.context)
        portal_workflow = getToolByName(context, 'portal_workflow')
        review_state = portal_workflow.getInfoFor(context, 'review_state')
        return review_state
        
    @view.memoize_contextless
    def cycle_state(self,review_state):
        wtool = getToolByName(self.context, 'portal_workflow', None)
        cycles = dict([(w.id,w.title) 
            for w in wtool['rd2.cycle-workflow'].states.values()])
        return cycles[review_state]
    
    @view.memoize_contextless
    def projet_state(self,review_state):
        wtool = getToolByName(self.context, 'portal_workflow', None)
        projets = dict([(w.id,w.title) 
            for w in wtool['rd2.projet-workflow'].states.values()])
        return projets[review_state]

    def __call__(self):
        if 'search.csvexport' in self.request.keys() and \
                self.request['search.csvexport'] == ' export csv':
            self.multiselect('review_state',pathDepth=2) 
            cat = self.results()
            for cycle in cat:
                for auteur in self.authors(cycle.getPath()):
                    self.sponsorasked(auteur)
            # Add header
            CSV = self.allauthors
            dataLen = len(CSV)
            R = self.request.RESPONSE
            R.setHeader('Content-Length', dataLen)
            R.setHeader('Content-Type', 'text/csv')
            R.setHeader('Content-Disposition', 
                'attachment; filename=%s.csv' % self.context.getId())
        
            #return thefields
            return CSV
        return super(InterfaceView, self).__call__()   
        
    def multiselect(self,indx='Subject',pathDepth=0):
        self.indx = indx
        self.pathDepth = pathDepth # 0 means everywhere
        catalog = getToolByName(self.context, 'portal_catalog')
        wtool = getToolByName(self.context, 'portal_workflow', None)
        #import pdb; pdb.set_trace()
        if indx == 'Subject':
            keywords = catalog.uniqueValuesFor('Subject')
            self.multikey = '@@keywordview'
            label = u'Selectionner un ou plusieurs mots-clé'
            self.searchType = IProjet.__identifier__

        else:
            self.keyword_dict = dict([(w.title,w.id) 
                for w in wtool['rd2.cycle-workflow'].states.values()])
            keywords = self.keyword_dict.keys()
            self.multikey = '@@cyclesview'
            label = u'Selectionner un ou plusieurs états'
            self.searchType = ICycle.__identifier__
            
        form = factory('form',
            name='search',
            props={
                'action': self._form_action,
            })

        form['searchterm'] = factory('#field:multiselect', props={
            'label': label,
            'vocabulary': keywords,
            'format': 'block',
            'multivalued': True})
        form['csvexport'] = factory('#field:select', props={
            'label': 'Export CSV',
            'vocabulary': [' export csv'," pas d'export csv"],
            'default':" pas d'export csv",
            'format': 'radio'})
        form['submit'] = factory(
            'field:submit',
            props={
                'label': MessageFactory(u'Lancer la recherche'),
                'submit.class': '',
                'handler': self._form_handler,
                'action': 'search'
        })

        controller = Controller(form, self.request)
        return controller.rendered

    def results(self):
        #import pdb; pdb.set_trace()
        if not hasattr(self,'searchterm') or not self.searchterm:
            return []
        #import pdb; pdb.set_trace()
        context = aq_inner(self.context)
        cat = getToolByName(self.context, 'portal_catalog')
        query = {}
        if self.indx == 'Subject':
            if 'search.csvexport' in self.request.keys() and \
                    self.request['search.csvexport']:
                self.searchType = 'ageliaco.rd2.interface.IProjet'
                self.pathDepth = 3
            query[self.indx] = self.searchterm
            query['object_provides'] = self.searchType
            if self.pathDepth:
                localpath = {'query': '/'.join(context.getPhysicalPath()), 
                    'depth': self.pathDepth}
                query['path'] = localpath
            #print query
            return cat(**query)                
        
        if 'search.csvexport' in self.request.keys() and \
                self.request['search.csvexport']:
            self.searchType = 'ageliaco.rd2.interface.ICycle'
            self.pathDepth = 2
        wtool = getToolByName(self.context, 'portal_workflow', None)

        #keywords1 = wtool.listWFStatesByTitle(filter_similar=1)
        self.keyword_dict = dict([(w.title,w.id) for w in 
                wtool['rd2.cycle-workflow'].states.values()])

        query[self.indx] = [self.keyword_dict[term] for term in self.searchterm]
        query['object_provides'] = self.searchType
        if self.pathDepth:
            localpath = {'query': '/'.join(context.getPhysicalPath()), 
                'depth': self.pathDepth}
            query['path'] = localpath
        return cat(**query)                

    def _form_action(self, widget, data):
        #import pdb; pdb.set_trace()

        return '%s/%s' % (self.context.absolute_url(),self.multikey)

    def _form_handler(self, widget, data):
        self.searchterm = data['searchterm'].extracted

    def projets(self, wf_state='all'):
        """Return a catalog search result of projects to show
        """
        
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        if wf_state == 'all':
            return catalog(portal_type='ageliaco.rd2.projet',
                           path={'query': '/'.join(context.getPhysicalPath()), 
                            'depth': 1},
                           sort_on="start", sort_order="reverse")        
        cat = catalog(portal_type='ageliaco.rd2.projet',
                       review_state=wf_state,
                       path={'query': '/'.join(context.getPhysicalPath()), 
                        'depth': 1},
                       sort_on='sortable_title')
        return cat


    def contributeurs(self,cycle_id):
        context = aq_inner(self.context)
        if context.portal_type == 'ageliaco.rd2.cycle':
            context = context.aq_parent
        catalog = getToolByName(self.context, 'portal_catalog')
        if cycle_id in context.keys():
            cycle = context[cycle_id]  
            if cycle:
                cat = catalog(object_provides= IAuteur.__identifier__,
                           path={'query': '/'.join(cycle.getPhysicalPath()),
                                 'depth': 1
                                },
                           sort_on="modified", sort_order="reverse")     
                return cat
        return None

    def cycles(self, projectPath='', wf_state='all'):
        """Return a catalog search result of cycles from a project
        """
        context = aq_inner(self.context)
        if not projectPath:
            projectPath = '/'.join(context.getPhysicalPath())
        catalog = getToolByName(self.context, 'portal_catalog')
        if wf_state == 'all':
            cat = catalog(object_provides= ICycle.__identifier__,
                           path={'query': projectPath, 'depth': 1},
                           sort_on="id")  
            return cat      
        return catalog(object_provides=[ICycle.__identifier__],
                       review_state=wf_state,
                       path={'query': projectPath, 'depth': 2},
                       sort_on='sortable_title')

                    
    def localcycles(self):
        #return a list of actual cycle objects
        context = aq_inner(self.context)
        cycles = {}
        catalog = getToolByName(self.context, 'portal_catalog')
        if context.portal_type == 'ageliaco.rd2.cycle':
            parent = context.aq_parent
            cat = catalog(object_provides= ICycle.__identifier__,
                            path={'query': '/'.join(parent.getPhysicalPath()), 'depth': 1})
            cycles = {c.id:c for c in cat if c.id==context.id}
            return cycles
        else:
            cat = self.cycles('/'.join(context.getPhysicalPath()))
        #import pdb; pdb.set_trace()
        for cycle in cat:
            cycles[cycle.id] = cycle   
        return cycles

    def getPortal(self):
        return getSite()
        
    def school(self,pseudo):
        projets = getProjetsParent(self.context)
        #import pdb; pdb.set_trace()
        if projets == None:
            return pseudo
        ecoles = projets.schools
        if ecoles:
            maListe = [x.strip() for x in ecoles.split(u'\n')]
            schooldict = {}
            for ordre in sorted(maListe):
                school = ordre.split(',')
                if school[0]== pseudo:
                    return school[1] 
        #try:
        return pseudo
        #except:
        #    return pseudo
        
    def cycle_state(self,review_state):
        wtool = getToolByName(self.context, 'portal_workflow', None)
        cycles = dict([(w.id,w.title) 
            for w in wtool['rd2.cycle-workflow'].states.values()])
        return cycles[review_state]

    def supervisor(self,sup_id):
        if not sup_id:
            return ""
        context = aq_inner(self.context)
        mt = getToolByName(self, 'portal_membership')
        if mt.getMemberById(sup_id) is None:
            return ""
        return mt.getMemberInfo(sup_id)['fullname']

    def supervisor_list(self,supervisor):
        if type(supervisor) == str:
            return [supervisor]
        return supervisor