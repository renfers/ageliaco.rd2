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
from plone.app.textfield.value import RichTextValue
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
from zope.interface import invariant, Invalid, Interface

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

import yafowil.plone
import yafowil.loader
from yafowil.base import factory, UNSET, ExtractionError
from yafowil.controller import Controller
from yafowil.plone.form import Form

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

sponsorships = {u"0":[u"0",0],
    u"0.25":[u"0.25",0.25],
    u"0.50":[u"0.50",0.50],
    u"0.75":[u"0.75",0.75],
    u"1.00":[u"1.00",1.00],
    u"1.25":[u"1.25",1.25],
    u"1.50":[u"1.50",1.50],
    u"1.75":[u"1.75",1.75],
    u"2.00":[u"2.00",2.00],
    u"2.25":[u"2.25",2.25],
    u"2.50":[u"2.50",2.50],
    u"2.75":[u"2.75",2.75],
    u"3.00":[u"3.00",3.00],
    u"3.25":[u"3.25",3.25],
    u"3.50":[u"3.50",3.50],
    u"3.75":[u"3.75",3.75],
    u"4.00":[u"4.00",4.00]}

class SchoolsVocabulary(object):
    grok.implements(IVocabularyFactory)
    def __call__(self, context):
        terms = []
        for school in sorted(schools.keys()):
            terms.append(SimpleVocabulary.createTerm(unicodedata.normalize('NFKC',school).encode('ascii','ignore'), 
                            unicodedata.normalize('NFKC',schools[school][0]).encode('ascii','ignore'), 
                            unicodedata.normalize('NFKC',schools[school][0]).encode('ascii','ignore')))
        return SimpleVocabulary(terms)
grok.global_utility(SchoolsVocabulary, name=u"ageliaco.rd2.schools")


class SponsorshipVocabulary(object):
    grok.implements(IVocabularyFactory)
    def __call__(self, context):
        terms = []
        for sponsorship in sorted(sponsorships.keys()):
            terms.append(SimpleVocabulary.createTerm(unicodedata.normalize('NFKC',sponsorship).encode('ascii','ignore'), 
                            unicodedata.normalize('NFKC',sponsorships[sponsorship][0]).encode('ascii','ignore'), 
                            unicodedata.normalize('NFKC',sponsorships[sponsorship][0]).encode('ascii','ignore')))
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
            required=True,
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
    
    sponsorasked = schema.Choice(
            title=_(u"Dégrèvement demandé"),
            description=_(u"Dégrèvement total demandé pour cet auteur"),
            vocabulary=u"ageliaco.rd2.sponsorship",
            required=True,
        )
    
    dexterity.read_permission(sponsorSEM='cmf.ReviewPortalContent')
    dexterity.write_permission(sponsorSEM='cmf.ReviewPortalContent')
    sponsorSEM = schema.Choice(
            title=_(u"Dégrèvement SEM"),
            description=_(u"Dégrèvement SEM attribué pour cet auteur"),
            vocabulary=u"ageliaco.rd2.sponsorship",
            required=False,
        )
    
    dexterity.read_permission(sponsorRD='cmf.ReviewPortalContent')
    dexterity.write_permission(sponsorRD='cmf.ReviewPortalContent')
    sponsorRD = schema.Choice(
            title=_(u"Dégrèvement R&D"),
            description=_(u"Dégrèvement R&D attribué pour cet auteur"),
            vocabulary=u"ageliaco.rd2.sponsorship",
            required=False,
        )
    
    dexterity.read_permission(sponsorSchool='cmf.ReviewPortalContent')
    dexterity.write_permission(sponsorSchool='cmf.ReviewPortalContent')
    sponsorSchool= schema.Choice(
            title=_(u"Dégrèvement Ecole"),
            description=_(u"Dégrèvement école attribué pour cet auteur"),
            vocabulary=u"ageliaco.rd2.sponsorship",
            required=False,
        )
    
@grok.subscribe(IAuteur, IObjectAddedEvent)
def setAuteur(auteur, event):
    portal_url = getToolByName(auteur, 'portal_url')
    acl_users = getToolByName(auteur, 'acl_users')
    
    #print "Nous y voici ::::>>>> ", auteur.id
    portal = portal_url.getPortalObject() 
    cycles = auteur.aq_parent
    #print 'auteur id : ' + auteur.id
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
        #print dir(brain)
        #print "getURL : %s => getPath : %s " % (brain.getURL(),brain.getPath())
        terms.append(SimpleVocabulary.createTerm(brain.getPath(), brain.id, brain.Title))
    return SimpleVocabulary(terms) #SimpleVocabulary([SimpleVocabulary.createTerm(x.id, x.getURL(), x.Title) for x in cat])

cycle_default_projet_presentation = """
<h2><span style="color: rgb(204, 0, 0); ">Discipline(s) concernée(s) par le projet :<br /></span></h2>
<p class="callout">&nbsp; </p>
<h2><span style="color: rgb(1, 40, 0); "><span style="color: rgb(204, 0, 0); ">Description synthétique de l'ensemble du projet :</span><br /></span></h2>
<p><i><span class="discreet noprint">Décrire brièvement votre projet en vue de sa promotion sur le site Ressources et développement.</span></i></p>
<p class="callout">&nbsp;</p><br />
<h2><span style="color: rgb(204, 0, 0);">Thématique:</span></h2>
<h3>Quel est le thème du projet ?</h3>
<p><i><span class="discreet noprint">Expliciter en quelques lignes le(s) contenu(s) sur le(s)quel(s) les participants au projet souhaitent travailler.</span></i></p>
<p class="callout">&nbsp;</p><br />
<h2><span style="color: rgb(204, 0, 0); ">Contexte :</span></h2>
<h3>a. Sur quelles expériences ou connaissances préalables repose le projet ?</h3>
<p><i><span class="discreet noprint">Quels sont le travail et la réflexion déjà  entamés dans le domaine de la recherche proposée : bibliographie, 
 inventaire d'expérience, etc.</span></i></p>
<p class="callout">&nbsp;</p><br />
<h3>b.   Quels éléments de la situation présente sont à l'origine du besoin exprimé ?</h3>
<p><i><span class="discreet noprint">Justification et preuves du besoin : études, enquête, sondage, argumentaire précis, etc..</span></i></p>
<p class="callout">&nbsp;</p><br />
<h2><span style="color: rgb(204, 0, 0); ">Objectifs pédagogiques :</span></h2>
<h3>Quels sont les objectifs généraux du projet ?</h3>
<p><i><span class="discreet noprint">Changements et actions concrets auxquels on peut s'attendre à court et à long terme</span></i></p>
<p class="callout">&nbsp;</p><br />
<h2><span style="color: rgb(204, 0, 0); ">Résultats pédagogiques pour les élèves et les maîtres :</span></h2>
<h3>a.  Quels sont le public visé et les établissements concernés ?</h3>
<p class="callout">&nbsp; </p>
<h3>b.  Quelle forme prend le produit fini au terme du projet ?</h3>
<p><i><span class="discreet noprint">Brochure, site, etc..</span></i></p>
<p class="callout">&nbsp;</p><br />
<h2><span style="color: rgb(204, 0, 0); ">Organisation :</span></h2>
<h3>a.  Quelle est la durée estimée du projet, en année(s) scolaire(s) ?</h3>
<p class="callout">&nbsp; </p>
<h3>b.  Quels sont les objectifs spécifiques du projet pour l'(es) année(s) scolaire(s) ?</h3>
<p class="callout">&nbsp; </p>
"""

cycle_default_problematique = """
<h2><span style="color: rgb(204, 0, 0); ">Planification et répartition des tâches pour l'année en cours :</span></h2>
<h3>a.  Quelle planification est prévue ? (étapes) :</h3>
<p class="callout">&nbsp; </p>
<h3>b.  Quel rôle et quelle répartition des tâches sont prévus par participant?</h3>
<p class="callout">&nbsp; </p>
<p> </p>
<h2><span style="color: rgb(204, 0, 0); ">Modalités de travail :</span></h2>
<h3>Quelles sont les modalités de travail qui faciliteraient la réalisation de votre projet ?</h3>
<p><i><span class="discreet noprint">Plateforme pour un travail à distance,   horaire aménagé sur 2 heures hebdomadaires, etc. (à préciser également  
 dans les vœux horaires dans votre établissement.)</span></i></p>
<p class="callout">&nbsp;</p><br />
<h2><span style="color: rgb(204, 0, 0); ">Ressources supplémentaires :</span></h2>
<p><i><span class="discreet noprint">Accompagnement par des experts du Service   Ecole Media, par des experts sous forme de demi-journées d'étude, par  
 des séminaires de formation continue, etc.</span></i></p>
<p class="callout">&nbsp; </p>
<br />
<p style="text-align: center; "><span style="color: rgb(204, 0, 0); "><strong>
<img alt="Sourire" border="0" src="../plugins/emotions/img/smiley-smile.gif" title="Sourire" /> 
Le secteur Ressources et développement vous remercie d'avoir complété ce formulaire auquel il portera toute son attention</strong>
</span><i><span> 
<img alt="Sourire" border="0" src="../plugins/emotions/img/smiley-smile.gif" title="Sourire" /><br /></span></i></p>
<p>&nbsp;</p>
"""
    
class ICycle(form.Schema):
    """
    Cycle de projet RD
    """
    
    # -*- Your Zope schema definitions here ... -*-
    id = schema.TextLine(
            title=_(u"Identifiant"),
            description=_(u"Ne pas changer celui donné par défaut! Merci!"),
            required=True,
        )
    title = schema.TextLine(
            title=_(u"Titre"),
            description=_(u"Titre bref du projet"),
            required=True,
        )
    description = schema.Text(
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
        
#     objectifs = RichText(
#             title=_(u"Objectifs"),
#             description=_(u"Objectifs, moyens nécessaires et résultats escomptés du projet pour l'année"),
#             required=False,
#         )    

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



@form.default_value(field=ICycle['presentation'])
def presentationDefaultValue(data):
    # To get hold of the folder, do: context = data.context
    return RichTextValue(
            raw=cycle_default_projet_presentation
            ) 

@form.default_value(field=ICycle['problematique'])
def problematiqueDefaultValue(data):
    # To get hold of the folder, do: context = data.context
    return RichTextValue(
            raw=cycle_default_problematique
            )

    
@grok.subscribe(ICycle, IObjectModifiedEvent)
def setSupervisor(cycle, event):
    if not cycle.supervisor:
        return
    if IRoleManager.providedBy(cycle):
        cycle.manage_addLocalRoles(cycle.supervisor, ['Reader', 'Contributor', 'Editor'])
    log("Role added to %s for %s"%(cycle.id,cycle.supervisor))

@grok.subscribe(ICycle, IObjectAddedEvent)
def setAuteurs(cycle, event):
    #print "Projet lié à %s ==> %s ==> %s" % (cycle.id,cycle.projet,cycle.supervisor)
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
    
    def set2float(self,value):
        if not value:
            return 0.0
        else:
            return float(value)
            
    def canRequestReview(self):
        return checkPermission('cmf.RequestReview', self.context)
        
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
                                             0.0,
                                             0.0]            
            
        return self.objectPath
        
    def getObjectPath(self):
        return self.objectPath
        
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
        #log( 'authors : ' + projectPath)
        cat = catalog(object_provides=[IAuteur.__identifier__],
                       path={'query': projectPath, 'depth': 2},
                       sort_on="modified", sort_order="reverse")
        for auteur in cat:
            #print auteur.id, auteur.firstname, auteur.lastname, auteur.email
            
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
        if self.withTotal:
            self.degrevements[self.objectPath][0] += self.set2float(author.sponsorasked)
            self.degrevements[self.objectPath][1] += self.set2float(author.sponsorSEM)
            self.degrevements[self.objectPath][2] += self.set2float(author.sponsorRD)
            self.degrevements[self.objectPath][3] += self.set2float(author.sponsorSchool)
            self.degrevements[self.objectPath][4] += self.set2float(author.sponsorSchool) + \
                            self.set2float(author.sponsorRD) + self.set2float(author.sponsorSEM)
        return (author.sponsorasked,author.sponsorSEM,author.sponsorRD,author.sponsorSchool)
        
    def multiselect(self,indx='Subject'):
        self.indx = indx
        catalog = getToolByName(self.context, 'portal_catalog')
        wtool = getToolByName(self.context, 'portal_workflow', None)
        if indx == 'Subject':
            keywords = catalog.uniqueValuesFor('Subject')
            self.multikey = '@@keywordview'
            label = u'Selectionner un ou plusieurs mots-clé'
            self.searchType = IProjet.__identifier__

        else:
            keywords = catalog.uniqueValuesFor('review_state')
            self.multikey = '@@cyclesview'
            label = u'Selectionner un ou plusieurs états'
            self.searchType = ICycle.__identifier__
            
        #print keywords
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
        form['submit'] = factory(
            'field:submit',
            props={
                'label': _(u'Lancer la recherche'),
                'submit.class': '',
                'handler': self._form_handler,
                'action': 'search'
        })

        controller = Controller(form, self.request)
        return controller.rendered

    def results(self):
        if not hasattr(self,'searchterm') or not self.searchterm:
            return []
        context = aq_inner(self.context)
        cat = getToolByName(self.context, 'portal_catalog')
        query = {}
    
        query[self.indx] = self.searchterm
        query['object_provides'] = self.searchType
        #print query
        return cat(**query)                
    def _form_action(self, widget, data):
        #import pdb; pdb.set_trace()
        #print "retour à ",  self.context.absolute_url()

        return '%s/%s' % (self.context.absolute_url(),self.multikey)

    def _form_handler(self, widget, data):
        #import pdb; pdb.set_trace()
        self.searchterm = data['searchterm'].extracted

    def projets(self, wf_state='all'):
        """Return a catalog search result of projects to show
        """
        
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        #log( "context's physical path : " + '/'.join(context.getPhysicalPath()))
        if wf_state == 'all':
            #log( "all projets")
            #log('/'.join(context.getPhysicalPath()))
            return catalog(portal_type='ageliaco.rd2.projet',
                           path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
                           sort_on="start", sort_order="reverse")        
        #log('/'.join(context.getPhysicalPath()))
        cat = catalog(portal_type='ageliaco.rd2.projet',
                       review_state=wf_state,
                       path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
                       sort_on='sortable_title')
        #log('catalogue : %s items'%len(cat))
        return cat

    def cycles(self, projectPath, wf_state='all'):
        """Return a catalog search result of cycles from a project
        """
        #import pdb; pdb.set_trace()
        context = aq_inner(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        #log( 'cycle : ' + projectPath)
        #log( wf_state + " state chosen")
        if wf_state == 'all':
            #log( "all cycles")
            cat = catalog(object_provides= ICycle.__identifier__,
                           path={'query': projectPath, 'depth': 1},
                           sort_on="modified", sort_order="reverse")  
            #print len(cat)
            return cat      
        return catalog(object_provides=[ICycle.__identifier__],
                       review_state=wf_state,
                       path={'query': projectPath, 'depth': 2},
                       sort_on='sortable_title')

    def getPortal(self):
        return getSite()
        
        
