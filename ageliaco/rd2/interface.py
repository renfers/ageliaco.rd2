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


from plone.directives import form, dexterity
from plone.app.textfield import RichText
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.indexer import indexer

from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.schema.fieldproperty import FieldProperty
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
import unicodedata
from zope.interface import invariant, Invalid, Interface
from plone.z3cform.interfaces import IWrappedForm

from ageliaco.rd2 import MessageFactory
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
import datetime

import z3c.form
from z3c.form import validator
from z3c.form import button
from z3c.form.interfaces import ActionExecutionError, WidgetActionExecutionError
from zope.app.pagetemplate import ViewPageTemplateFile as Zope3PageTemplateFile
from plone.z3cform.z2 import processInputs
from plone.z3cform.crud import crud
# for debug purpose => log(...)
from Products.CMFPlone.utils import log


from zope.schema.interfaces import IContextSourceBinder
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.app.container.interfaces import IObjectAddedEvent
from Products.CMFCore.utils import getToolByName
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from plone.namedfile.field import NamedImage
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from z3c.form.browser.checkbox import CheckBoxFieldWidget

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
ordres = {
    "COLLEGES" : u"COLLEGES",
    "ECG" : u"ECG",
    "CFP" : u"ECOLES PROFESSIONNELLES",
    "INSERTION" : u"INSERTION",
    }

professionnelles = {
    "CFPPC": u"CFPPC",
    "CFPS":u"CFPS",
    "CFPT":u"CFPT",
    "CFPSH":u"CFPSHR-EGEI",
    "CFPNE":u"CFPNE",
    "CFPAA":u"CFPAA",
    }
    
schools = {
    'CALV' : ['CALV',u"collège Calvin",u"COLLEGES"],
    'CAND' : ['CAND',u"collège de Candolle",u"COLLEGES"],
    'CLAP' : ['CLAP',u"collège Claparède",u"COLLEGES"],
    'ROUS' : ['ROUS',u"collège Rousseau",u"COLLEGES"],
    'SAUS' : ['SAUS',u"collège de Saussure",u"COLLEGES"],
    'SISM' : ['SISM',u"collège Sismondi",u"COLLEGES"],
    'VOLT' : ['VOLT',u"collège Voltaire",u"COLLEGES"],
    'STAEL' : ['STAEL',u"collège de Staël",u"COLLEGES"],
    'COPAD' : ['COPAD',u"collège pour adultes Alice-Rivaz",u"COLLEGES"],
    'CEBOU' : ['CEBOU',u"EC Nicolas-Bouvier",u"CFPPC"],
    'CECHA' : ['CECHA',u"CEC André-Chavanne",u"CFPPC"],
    'CEGOU' : ['CEGOU',u"CEC Emilie-Gourd",u"CFPPC"],
    'STITE' : ['STITE',u"EC Aimée-Stitelmann",u"CFPPC"],
    'BGRIE' : ['BGRIE',u"EC Bougeries",u"CFPPC"],
    'CFPAA' : ['CFPAA',u"centre de formation professionnelle arts appliqués",u"CFP"],
    'CFPC' : ['CFPC',u"centre de formation professionnelle construction",u"CFP"],
    'CFPSHR' : ['CFPSHR',u"centre de formation professionnelle service hôtellerie restauration",u"CFP"],
    'CFPT' : ['CFPT',u"centre de formation professionnelle technique",u"CFP"],
    'CFPne' : ['CFPne',u"centre de formation professionnelle nature et environnement",u"CFP"],
    'CFPS' : ['CFPS',u"centre de formation professionnelle santé social",u"CFP"],
    'ESPOD' : ['ESPOD',u"école supérieure des podologues",u"CFP"],
    'ESHYD' : ['ESHYD',u"école supérieure des hygiénistes dentaires",u"CFP"],
    'ESAME' : ['ESAME',u"école supérieure des assistant-e-s de médecin",u"CFP"],
    'ECLAB' : ['ECLAB',u"école des métiers du laboratoire",u"CFP"],
    'ESEDE' : ['ESEDE',u"école supérieure d'éducatrices et d'éducateurs de l'enfance",u"CFP"],
    'ESAMB' : ['ESAMB',u"école supérieure des ambulancier-ère-s",u"CFP"],
    'CUISI' : ['CUISI',u"filière romande de cuisinier-ère-s en diététique",u"CFP"],
    'FORAD' : ['FORAD',u"formation d'assistant-e-s dentaires",u"CFP"],
    'ECGEI' : ['ECGEI',u"école des gestionnaires en intendance",u"CFP"],
    'ECASE' : ['ECASE',u"école d'assistant-e-s socio-éducativ-ve-s",u"CFP"],
    'ECASO' : ['ECASO',u"école d'assistant-e-s en soins et santé communautaire",u"CFP"],
    'DUNAN' : ['DUNAN',u"ECG Henry-Dunant",u"ECG"],
    'PIAGE' : ['PIAGE',u"ECG Jean-Piaget",u"ECG"],
    'MAILL' : ['MAILL',u"ECG Ella-Maillart",u"ECG"],
    'ACPO' : ['ACPO',u"service de l'accueil du postobligatoire",u"INSERTION"],
    'CTP' : ['CTP',u"centre de la transition professionnelle",u"INSERTION"],
    }

sponsorships = {"0":[u"0",0],
    0.25:[u"0.25",0.25],
    0.5:[u"0.5",0.5],
    0.75:[u"0.75",0.75],
    1.0:[u"1.0",1.0],
    1.25:[u"1.25",1.25],
    1.5:[u"1.5",1.5],
    1.75:[u"1.75",1.75],
    2.0:[u"2.0",2.0],
    2.25:[u"2.25",2.25],
    2.5:[u"2.5",2.5],
    2.75:[u"2.75",2.75],
    3.0:[u"3.0",3.0]}

class SchoolsVocabulary(object):
    grok.implements(IVocabularyFactory)
    def __call__(self, context):
        terms = []
        for school in sorted(schools.keys()):
            terms.append(SimpleVocabulary.createTerm(school, 
                            str(school),
                            schools[school][1]))
        return SimpleVocabulary(terms)
grok.global_utility(SchoolsVocabulary, name=u"ageliaco.rd2.schools")

class OrdresEnseignementVocabulary(object):
    grok.implements(IVocabularyFactory)
    def __call__(self, context):
        terms = []
        for ordre in sorted(ordres.keys()):
            terms.append(SimpleVocabulary.createTerm(ordre, 
                            str(ordre),
                            ordres[ordre]))
        return SimpleVocabulary(terms)
grok.global_utility(OrdresEnseignementVocabulary, name=u"ageliaco.rd2.ordres")

class ProfessionnellesVocabulary(object):
    grok.implements(IVocabularyFactory)
    def __call__(self, context):
        terms = []
        for ordre in sorted(professionnelles.keys()):
            terms.append(SimpleVocabulary.createTerm(ordre, 
                            str(ordre),
                            professionnelles[ordre]))
        return SimpleVocabulary(terms)
grok.global_utility(ProfessionnellesVocabulary, name=u"ageliaco.rd2.professionnelles")


class SponsorshipVocabulary(object):
    grok.implements(IVocabularyFactory)
    def __call__(self, context):
        terms = []
        for sponsorship in sorted(sponsorships.keys()):
            terms.append(SimpleVocabulary.createTerm(sponsorship, 
                            str(sponsorship), 
                            sponsorships[sponsorship][0]))
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


@grok.provider(IContextSourceBinder)
def possibleAttendees(context):
    # auteurs + supervisors
    cycle = None
    terms = []
    parent = context.aq_parent 
    #import pdb; pdb.set_trace()
    if context.portal_type == 'ageliaco.rd2.cycle':
        cycle = context
    else:
        return  SimpleVocabulary(terms) #no list for internal notes (notes in a note)
    mt = getToolByName(context, 'portal_membership')
    for supervisor in cycle.supervisor:
        member =  mt.getMemberById(supervisor)
        name = member.getProperty('fullname')
        terms.append(SimpleVocabulary.createTerm(supervisor, 
                            str(supervisor), 
                            name))
    catalog = getToolByName(context, 'portal_catalog')
    auteurBrains = catalog(portal_type='ageliaco.rd2.auteur',
                        path={'query': cycle.virtual_url_path(), 'depth': 1})
    for brain in auteurBrains:
        member = brain.id
        if brain.has_key('firstname') and brain.has_key('lastname'):
            name = "%s %s" % (brain.lastname,brain.firstname)
        else:
            name = brain.id
        terms.append(SimpleVocabulary.createTerm(brain.id, 
                            str(brain.id), 
                            name))
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

    presentation = RichText(
            title=MessageFactory(u"Notes de séance"),
            description=MessageFactory(u"Compte-rendu de l'avancement du projet"),
            required=False,
        )    

@form.default_value(field=INote['title'])
def startDefaultValue(data):
    # To get hold of the folder, do: context = data.context
    day =  datetime.datetime.today()
    return "Note-" + day.strftime("%Y-%m-%d")

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



    lastname = schema.TextLine(
            title=MessageFactory(u"Nom"),
            description=MessageFactory(u"Nom de famille"),
            required=True,
        )

    firstname = schema.TextLine(
            title=MessageFactory(u"Prénom"),
            description=MessageFactory(u"Prénom"),
            required=True,
        )

    school = schema.Choice(
            title=MessageFactory(u"Ecole"),
            description=MessageFactory(u"Etablissement scolaire de référence"),
            vocabulary=u"ageliaco.rd2.schools",
            default='',
            required=True,
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
            description=MessageFactory(u"Dégrèvement total demandé pour cet auteur (1 heure ~= 2 x 1/2 journées/mois sur le projet)"),
            vocabulary=u"ageliaco.rd2.sponsorship",
            required=True,
            default='',
        )
    
    dexterity.read_permission(sponsorRD='cmf.ReviewPortalContent')
    dexterity.write_permission(sponsorRD='cmf.ReviewPortalContent')
    sponsorRD = schema.Choice(
            title=MessageFactory(u"Dégrèvement R&D"),
            description=MessageFactory(u"Dégrèvement R&D attribué pour cet auteur"),
            vocabulary=u"ageliaco.rd2.sponsorship",
            required=False,
        )
    
    dexterity.read_permission(sponsorSchool='cmf.ReviewPortalContent')
    dexterity.write_permission(sponsorSchool='cmf.ReviewPortalContent')
    sponsorSchool= schema.Choice(
            title=MessageFactory(u"Dégrèvement Ecole"),
            description=MessageFactory(u"Dégrèvement école attribué pour cet auteur"),
            vocabulary=u"ageliaco.rd2.sponsorship",
            required=False,
        )

class Auteur(object):
    grok.implements(IAuteur)
    def __init__(self,id,lastname,firstname,email,phone='',school='',sponsorasked='',sponsorRD='',sponsorSchool=''): 
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
    cycle = auteur.aq_parent

    cycle.manage_addLocalRoles(auteur.id, ['Reader',])


class IProjet(form.Schema):
    """
    Projet RD
    """
    dexterity.read_permission(start='cmf.ReviewPortalContent')
    dexterity.write_permission(start='cmf.ReviewPortalContent')
    start = schema.TextLine(
            title=MessageFactory(u"Année"),
            description=MessageFactory(u"L'année à laquelle le projet a commencé ou devrait commencer"),
            required=True,
        )

    dexterity.read_permission(duration='cmf.ReviewPortalContent')
    dexterity.write_permission(duration='cmf.ReviewPortalContent')
    duration = schema.Int(
            title=MessageFactory(u"Durée"),
            description=MessageFactory(u"Durée (en années) du projet, prévue ou effective"),
            required=True,
        )
    
    presentation = RichText(
            title=MessageFactory(u"Présentation"),
            description=MessageFactory(u"Présentation synthétique du projet (présentation publiée)"),
            required=True,
        )    

    picture = NamedImage(
            title=MessageFactory(u"Chargez une image pour le projet"),
            required=False,
        )

    lien = schema.TextLine(
            title=MessageFactory(u"Lien vers la réalisation"),
            description=MessageFactory(u"Lien extérieur vers la réalisation"),
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
    terms = []
                
    for brain in cat:
        terms.append(SimpleVocabulary.createTerm(brain.getPath(), brain.id, brain.Title))
    return SimpleVocabulary(terms) #SimpleVocabulary([SimpleVocabulary.createTerm(x.id, x.getURL(), x.Title) for x in cat])


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
            description=MessageFactory(u"Ne pas changer celui donné par défaut! Merci!"),
            required=True,
        )
        
    title = schema.TextLine(
            title=MessageFactory(u"Titre"),
            description=MessageFactory(u"Titre bref du projet"),
            required=True,
            default=u'',
        )
        
    description = schema.Text(
            title=MessageFactory(u"Synopsys"),
            description=MessageFactory(u"Présentation du projet en un paragraphe"),
            required=False,
            default=u'',
        )
        
    #form.widget(projet=AutocompleteFieldWidget)
    projet = schema.Choice(
            title=MessageFactory(u"Projet existant"),
            description=MessageFactory(u"Lien vers un projet existant (en cas de reconduction)"),
            source=activeProjects,
            required=False,
            default=u'',
        )
            
    dexterity.write_permission(supervisor='cmf.ReviewPortalContent')
    form.widget(supervisor=CheckBoxFieldWidget)
    supervisor = schema.List(
            title=MessageFactory(u"Superviseur(s) R&D"),
            description=MessageFactory(u"Personne(s) de R&D qui supervise(nt) ce projet"),
            value_type=schema.Choice(source=GroupMembers('Supervisor')),
            required=False,
            missing_value=(),
            default=[],
        )
        
    domaine = schema.Text(
            title=MessageFactory(u"Domaine(s)"),
            description=MessageFactory(u"Domaine(s) couvert(s) par le projet (un par ligne)"),
            required=False,
            default=u'',
        )

    discipline = schema.Text(
            title=MessageFactory(u"Discipline(s)"),
            description=MessageFactory(u"Discipline(s) touchée(s) par le projet (une par ligne)"),
            required=False,
            default=u'',
        )
        
    presentation = RichText(
            title=MessageFactory(u"Problématique"),
            description=MessageFactory(u"Quel est le thème du projet? Expliciter le(s) contenu(s) sur le(s)quel(s) les participants au projet souhaitent travailler."),
            required=True,
            default=u'',
        )    

    # contexte Fieldset
    form.fieldset(
        'contexte',
        label=_(u"Contexte"),
        fields=['experiences', 'besoin']
    )

    experiences = RichText(
            title=MessageFactory(u"Expériences préalables"),
            description=MessageFactory(u"Sur quelles expériences ou connaissances préalables repose le projet? Quels sont le travail et la réflexion déjà entamés dans le domaine de la recherche proposée (bibliographie, inventaire d'expériences, etc.)"),
            required=True,
            default=u'',
        )    

    besoin = RichText(
            title=MessageFactory(u"Origine du besoin"),
            description=MessageFactory(u"Quels éléments de la situation présente sont à l'origine du besoin exprimé ? Justification et preuves du besoin (plan cadre, directives, etc.)"),
            required=True,
            default=u'',
        )    

    # Objectifs Fieldset
    form.fieldset(
        'objectifs',
        label=_(u"Objectifs"),
        fields=['problematique', 'cible', 'pro', 'forme']
    )
    
    problematique = RichText(
            title=MessageFactory(u"Objectifs généraux du projet"),
            description=MessageFactory(u"Changements et actions concrets auxquels on peut s'attendre à court et à long terme"),
            required=True,
            default=u'',
        )    

    cible = schema.List(
        title=MessageFactory(u"Filière visée"),
        description=MessageFactory(u"Sélectionnez la filière concernée"),
        value_type=schema.Choice(vocabulary=u"ageliaco.rd2.ordres"),
        required=True,
        missing_value=(),
        )
    
    pro = schema.List(
        title=MessageFactory(u"CFP"),
        description=MessageFactory(u"Si école professionnelle, précisez laquelle"),
        value_type=schema.Choice(vocabulary=u"ageliaco.rd2.professionnelles"),
        required=False,
        missing_value=(),
        )
    
    forme = RichText(
            title=MessageFactory(u"Forme du produit fini"),
            description=MessageFactory(u"Quels types de documents seront déposés sur le site de R&D? (documents maître, documents élève, documents de référence)"),
            required=True,
            default=u'',
        )    

    # Organisation Fieldset
    form.fieldset(
        'organisation',
        label=_(u"Organisation"),
        fields=['duree','planification', 'plan', 'repartition', 'modalites', 'participants','porteparole']
    )

    duree = schema.Int(
            title=MessageFactory(u"Durée du projet"),
            description=MessageFactory(u"Durée estimée du projet en années scolaires"),
            default = 1,
        )

    planification = RichText(
            title=MessageFactory(u"Planification des objectifs par année"),
            description=MessageFactory(u"Organisation des objectifs sur toute la durée du projet"),
            required=True,
            default=u'',
        )    

    plan = RichText(
            title=MessageFactory(u"Echéancier"),
            description=MessageFactory(u"Planification détaillée pour l'année à venir"),
            required=True,
            default=u'',
        )    
    
    repartition = RichText(
            title=MessageFactory(u"Répartition et rôles"),
            description=MessageFactory(u"Répartition prévue des tâches entre participants"),
            required=True,
            default=u'',
        )    

    modalites = RichText(
            title=MessageFactory(u"Modalités de travail"),
            description=MessageFactory(u"Plage horaire commune : demande du groupe de travail auprès des établissements concernés"),
            required=True,
            default=u'',
        )    

    participants = schema.Text(
            title=MessageFactory(u"Participants pour l'année à venir"),
            description=MessageFactory(u"Mettre le login EDU de chaque participant, un par ligne (ex: 'edu-travoltaj')"),
            required=True,
            default=u'',
        )    

    porteparole = schema.TextLine(
            title=MessageFactory(u"Coordinateur"),
            description=MessageFactory(u"Porte-parole du projet pour R&D (mettre le login EDU)"),
            required=True,
            default=u'',
        )

    @invariant
    def validatePorteparole(data):
        if data.porteparole not in data.participants.split():
            raise PorteparoleNotInParticipants(_(u"Le porte-parole doit faire partie des participants"))
                
        

def idDefaultFromContext(context):
    """context must be a ageliaco.rd2.projet object"""
    newId = ''
    indice = 1
    start = ''
    
    
    catalog = getToolByName(context, 'portal_catalog')
    cat = catalog.unrestrictedSearchResults(object_provides= ICycle.__identifier__,
               path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
               sort_on="modified", sort_order="reverse")  

    if hasattr(context,'start'):
        start = context.start
    else:
        start = str(datetime.datetime.today().year)

    if len(cat): #first is last generated,if it is not a copy from an old cycle
        for cycle in cat:
            lastId = cycle.id
            index = lastId.find('-')
            if (index > -1) and (lastId[:index]==start):
                indice = int(lastId[index+1:])
                indice+=1
                break
                
    newId =  "%s-%s" % (start,indice)
    while newId in context.objectIds():
        indice+=1
        newId =  "%s-%s" % (start,indice)
        
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
            cycle.manage_addLocalRoles(supervisor, ['Reader', 'Contributor', 'Editor','Reviewer'])
        log("Role added to %s for %s"%(cycle.id,cycle.supervisor))


def checkAuteurs(cycle, value=u""):
    if value:
        newauteurs = value.split('\n')
    else:
        newauteurs = []
    inputproblem = u""
    notfoundproblem = u""
    newparticipants = {}
    #import pdb; pdb.set_trace()
    for ligne in newauteurs:
        ligne = ligne.strip()
        #import pdb; pdb.set_trace()
        try:
            login = ligne
            if login :
                newparticipants[login.upper()] = login.upper()
        except:
            inputproblem += u"%s\n" % ligne
            raise ActionExecutionError(Invalid(_(u"Il y a un problème avec le ligne suivante : %s" % ligne)))
    return newparticipants
    
def aboutAuteurs(cycle, value=u""):
    newparticipants = checkAuteurs(cycle,value)
    #import pdb; pdb.set_trace()
    catalog = getToolByName(cycle, 'portal_catalog')
    cyclepath = '/'.join(cycle.getPhysicalPath())
    auteurBrains = catalog(portal_type='ageliaco.rd2.auteur',
                    path={'query': cyclepath, 'depth': 1})
    for brain in auteurBrains:
        if brain.id.upper() in newparticipants.keys():
            del newparticipants[brain.id]
            continue
        
        else: #auteur removed
            cycle.manage_delLocalRoles([brain.id.upper()])
            #import pdb; pdb.set_trace()
            if brain.id in cycle.keys():
                del cycle[brain.id]
                cycle.reindexObject()
    
        #try:
    acl_users = getToolByName(cycle, 'acl_users')
    acl = acl_users['ldap-plugin'].acl_users
    #import pdb; pdb.set_trace()
    for login in newparticipants.keys():
        ok = False
        members = acl.searchUsers(cn=login)
        for member in members:
            ok = False
            if login.upper() == member['cn'].upper():
                # create an auteur
                #auteur = createContentInContainer(cycle,"ageliaco.rd2.auteur", 
                auteur = createContent("ageliaco.rd2.auteur", 
                    id = str(login).upper(),
                    title = u"%s %s" % (member['sn'],member['givenName']),
                    firstname = member['givenName'],
                    lastname = member['sn'],
                    email = member['mail'],)
                    #sponsorasked = newparticipants[login])
                #print "rename %s to %s" % (auteur.id, str(login).upper())
                #auteur.id = str(login).upper()
                #cycle[str(login).upper()] = auteur
                #cycle.manage_renameObject(auteur.id, str(login).upper())
                cycle[auteur.id]=auteur
                cycle.manage_addLocalRoles(auteur.id.upper(), ['Reader','Owner'])
                print "OK => id %s is in !!!" % auteur.id
                ok = True
        if not ok:
            print "no member found for %s" % login
            raise ActionExecutionError(Invalid(_(u"Le login suivant n'est pas reconnu : %s" % login)))

 
@grok.subscribe(ICycle, IObjectAddedEvent)
def setAuteurs(cycle,event):
    aboutAuteurs(cycle, cycle.participants)
    #return cycle.absolute_url()+'/Auteurs'
 
class EditForm(dexterity.EditForm):
    grok.context(ICycle)
    #     def updateWidgets(self):
    #         """ """
    #         dexterity.EditForm.updateWidgets(self)

    @button.buttonAndHandler(_(u'Sauvegarder'))
    def handleApply(self, action):
        data, errors = self.extractData()
        #import pdb; pdb.set_trace()
        # Some additional validation
        if 'participants' in data:
            cycle = self.context
            aboutAuteurs(cycle, data['participants'])
            #if data['porteparole'] not in data['participants'].split():
            #    raise ActionExecutionError(Invalid(_(u"Le porte-parole (%s) ne se trouve pas parmi les participants!" % data['porteparole'])))

        if errors:
            self.status = self.formErrorsMessage
            return
        else:
            processInputs(self.request)
            extrapath = ''
            if data['participants'] != cycle.participants:
                # changes were made
                extrapath = '/'+'Auteurs'
            #save changes
            self.applyChanges(data)
            cycle.reindexObject()
            return self.request.response.redirect(cycle.absolute_url()+extrapath)


class AddForm(dexterity.AddForm):
    grok.name('ageliaco.rd2.cycle')

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
                checkAuteurs(cycle, data['participants'])
            #import pdb; pdb.set_trace()
        return self.request.response.redirect(cycle.absolute_url()+extrapath)

class AuteursEditForm(crud.EditForm):
    """ Pigeonhole edit form.  Just a normal CRUD form without the form title or edit button.
    """

    label = u"""Complétez les informations
    
    école : attachement administratif, 
    dégrèvement demandé : une heure de dégrèvement correspond à 2 demi-journées de travail par mois!"""

    
    buttons = crud.EditForm.buttons.copy().omit('delete')
    handlers = crud.EditForm.handlers.copy()
    @button.buttonAndHandler(_(u"Retour au formulaire"),name= "Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """
        print self.request['URL1']
        cycleurl = self.request['URL1']
        return self.request.response.redirect(cycleurl)


class AuteursForm(crud.CrudForm,grok.View):
    update_schema = IAuteur
    addform_factory = crud.NullForm
    editform_factory = AuteursEditForm
    grok.context(ICycle)
    grok.require('zope2.View')
    grok.name('Auteurs')
    #grok.template('interface_templates/auteursEdit.pt')
    #template = Zope3PageTemplateFile('interface_templates/auteursEdit.pt')    
    def get_items(self):
        #import pdb; pdb.set_trace()
        return self.context.objectItems()
        
#     def remove(self, (id, item)):
#         self.context.manage_deleteItems([id,])

#     def demos(self):
#         form = AuteursForm(self.context, self.request)
#         form.update()
#         return form

#     def updateWidgets(self):
#         """ Make sure that return URL is not visible to the user.
#         """
#         import pdb; pdb.set_trace()
#         crud.CrudForm.updateWidgets(self)
# 
#         # Use the return URL suggested by the creator of this form
#         # (if not acting standalone)
#         self.widgets["sponsorRD"].mode = z3c.form.interfaces.HIDDEN_MODE
#         self.widgets["sponsorSchool"].mode = z3c.form.interfaces.HIDDEN_MODE
        
        
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
    allauthors = "cycle,author.id,author.lastname,author.firstname,author.school,ordre,author.sponsorasked,author.sponsorRD,author.sponsorSchool"
    keyword_dict = {}
         
    def set2float(self,value):
        if not value:
            return 0.0
        else:
            return float(value)
            
    # canReviewContent        
    def canReviewContent(self):
        return checkPermission('cmf.ReviewPortalContent', self.context)
    
        
    def canAddContent(self):
        return checkPermission('cmf.AddPortalContent', self.context)
        
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
        #import pdb; pdb.set_trace()
        return auteurs
        
    def getSponsoring(self):
        if self.withTotal:
            return self.degrevements[self.objectPath]
        else:
            return {}

    def sponsorasked(self,auteur):
        context = aq_inner(self.context)
        author = auteur.getObject()
        ordre = ''
        if author.school in schools.keys():
            ordre = schools[author.school][1]
        oneauthor = "\n%s,%s,%s,%s,%s,%s,%d,%d"%(auteur.getPath().split('/')[-2],author.id,author.lastname,
                                    author.firstname,author.school,ordre,
                                    self.set2float(author.sponsorRD),self.set2float(author.sponsorSchool))
        self.allauthors += oneauthor
        if self.withTotal:
            self.degrevements[self.objectPath][0] += self.set2float(author.sponsorasked)
            self.degrevements[self.objectPath][1] += self.set2float(author.sponsorRD)
            self.degrevements[self.objectPath][2] += self.set2float(author.sponsorSchool)
            self.degrevements[self.objectPath][3] += self.set2float(author.sponsorSchool) + \
                            self.set2float(author.sponsorRD)
        return (author.sponsorasked,author.sponsorRD,author.sponsorSchool)
        
    def __call__(self):
        if 'search.csvexport' in self.request.keys() and self.request['search.csvexport'] == ' export csv':
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
            R.setHeader('Content-Disposition', 'attachment; filename=%s.csv' % self.context.getId())
        
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
            self.keyword_dict = dict([(w.title,w.id) for w in wtool['rd2.cycle-workflow'].states.values()])
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
            if 'search.csvexport' in self.request.keys() and self.request['search.csvexport']:
                self.searchType = 'ageliaco.rd2.interface.IProjet'
                self.pathDepth = 3
            query[self.indx] = self.searchterm
            query['object_provides'] = self.searchType
            if self.pathDepth:
                localpath = {'query': '/'.join(context.getPhysicalPath()), 'depth': self.pathDepth}
                query['path'] = localpath
            #print query
            return cat(**query)                
        
        if 'search.csvexport' in self.request.keys() and self.request['search.csvexport']:
            self.searchType = 'ageliaco.rd2.interface.ICycle'
            self.pathDepth = 2
        wtool = getToolByName(self.context, 'portal_workflow', None)

        #keywords1 = wtool.listWFStatesByTitle(filter_similar=1)
        self.keyword_dict = dict([(w.title,w.id) for w in wtool['rd2.cycle-workflow'].states.values()])

        query[self.indx] = [self.keyword_dict[term] for term in self.searchterm]
        query['object_provides'] = self.searchType
        if self.pathDepth:
            localpath = {'query': '/'.join(context.getPhysicalPath()), 'depth': self.pathDepth}
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
                           path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
                           sort_on="start", sort_order="reverse")        
        cat = catalog(portal_type='ageliaco.rd2.projet',
                       review_state=wf_state,
                       path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
                       sort_on='sortable_title')
        return cat

    def cycles(self, projectPath, wf_state='all'):
        """Return a catalog search result of cycles from a project
        """
        context = aq_inner(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        if wf_state == 'all':
            cat = catalog(object_provides= ICycle.__identifier__,
                           path={'query': projectPath, 'depth': 1},
                           sort_on="modified", sort_order="reverse")  
            return cat      
        return catalog(object_provides=[ICycle.__identifier__],
                       review_state=wf_state,
                       path={'query': projectPath, 'depth': 2},
                       sort_on='sortable_title')

    def getPortal(self):
        return getSite()
        
    def school(self,pseudo):
        try:
            return schools[pseudo][0]
        except:
            return pseudo
        
    def cycle_state(self,review_state):
        wtool = getToolByName(self.context, 'portal_workflow', None)
        cycles = dict([(w.id,w.title) for w in wtool['rd2.cycle-workflow'].states.values()])
        return cycles[review_state]

    def supervisor(self,sup_id):
        context = aq_inner(self.context)
        mt = getToolByName(self, 'portal_membership')
        if mt.getMemberById(sup_id) is None:
            return ""
        return mt.getMemberInfo(sup_id)['fullname']

    def supervisor_list(self,supervisor):
        if type(supervisor) == str:
            return [supervisor]
        return supervisor