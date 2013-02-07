# -*- coding: UTF-8 -*-
from five import grok
from zope import schema

from Products.ATContentTypes.lib import constraintypes

from plone.directives import form, dexterity
from zope.app.container.interfaces import IObjectAddedEvent

from plone.z3cform.textlines import TextLinesFieldWidget

from zope.interface import invariant, Invalid

from interface import IProjet, IAuteur, ICycle, idDefaultFromContext
from interface import cycle_default_problematique, cycle_default_projet_presentation
from note import INote

import yafowil.plone
import yafowil.loader
from yafowil.base import factory, UNSET, ExtractionError
from yafowil.controller import Controller
from yafowil.plone.form import Form
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.dexterity.utils import createContentInContainer
from zope.schema.vocabulary import SimpleVocabulary
from plone.app.textfield.value import RichTextValue
from DateTime import DateTime
from plone.indexer import indexer
import datetime

from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage

from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from zope.security import checkPermission
from zope.app.content import queryContentType
from zope.schema import getFieldsInOrder
from plone.dexterity.interfaces import IDexterityFTI 
from zope.component import queryUtility

 
from ageliaco.rd2 import _



@grok.subscribe(IProjet, IObjectAddedEvent)
def setRealisation(projet, event):
    admid = 'realisation'
    try:
        cycles = projet[admid]
    except KeyError: 
        rea = projet.invokeFactory("Folder", id=admid, title=u'Réalisation')
        #projet[admid] = rea
        rea.setConstrainTypesMode(constraintypes.ENABLED)
        rea.setLocallyAllowedTypes(["File","Folder","Image","Document","Link"])
        rea.setImmediatelyAddableTypes(["File","Folder","Image","Document","Link"])
    
    #projet.setContributors(projet.contributor)
    #request.response.redirect(cycles.absolute_url() + '++add++ageliaco.rd2.cycle')
    return #request.response.redirect(cycles.absolute_url() + '++add++ageliaco.rd2.cycle')
    
@indexer(IProjet)
def searchableIndexer(context):
    keywords = " ".join(context.keywords)
    return "%s %s %s %s" % (context.title, context.description, context.presentation, keywords)

grok.global_adapter(searchableIndexer, name="SearchableText")

    

def richtext():
    part = factory(u'fieldset', name='yafowilwidgetrichtext')
    part['richtext'] = factory('#field:richtext', props={
        'label': 'Richtext field',
        'required': 'Text is required'})
    return {'widget': part,
            'doc': "Doc",
            'title': 'Richtext'}


# class DepotView(grok.View,Form):
#     grok.context(IProjet)
#     grok.require('zope2.View')
#     grok.name('depot')
# 
#     newprojet = ''
#     newprojet_url = ''
#     next = ''
#     projet = ''
#     def form(self):
#         form = factory(
#             'form',
#             name='myform',
#             props={
#                 'action': self.form_action,
#             })
# 
#         # form widgets creation here...
#         form['newprojet'] = factory(
#             'field:label:error:text',
#             props={
#                 'label': _(u'Titre du nouveau projet : '),
#                 'field.class': 'field',
#                 'default' : self.request.get('view.cycleId'),
#                 'text.class': 'text',
#                 'size': '80',
#         })
# 
#         form['projet'] = factory(
#             'field:label:error:select',
#             props={
#                 'label': _(u'Reconduire le projet suivant : '),
#                 'field.class': 'field',
#                 'select.class': 'select',
#                 'vocabulary': self.activeProjets,
#         })
# 
#         form['submit'] = factory(
#             'field:submit',
#             props={
#                 'label': self.set_label(),
#                 'submit.class': 'btn-primary',
#                 #'handler': self.form_handler,
#                 'action' : True,
#                 'next' : self.nextform,
#         })
# 
#         form['presentation'] = factory(
#             '#field:richtext',
#             props={
#                 'label': u'Présentation résumée du projet',
#                 #'placeholder': u'Présentation succincte du projet',
#                 'required': 'Text is required',
#         })
#         controller = Controller(form, self.request)
#         return controller.rendered
# 
# 
# 
#     def re_form_handler(self, widget, data):
#         self.projet = data['projet'].extracted
# 
# 
#     def re_form_action(self, widget, data):
#         import pdb; pdb.set_trace()
#         if not hasattr(self,'projet') or not self.projet:
#             error = ExtractionError(
#                 'Choisissez un projet dans la liste!')
#             return self.context.absolute_url()
#         context = aq_inner(self.context)
#         catalog = getToolByName(self.context, 'portal_catalog')
#         cat = catalog(object_provides= ICycle.__identifier__,
#                    path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
#                    sort_on="modified", sort_order="reverse")  
#         print "cat len = ", len(cat), cat
#         cycleId = "%s-%i" % (context.start,(len(cat)+1))
#         item = createContentInContainer(context, "ageliaco.rd2.cycle", 
#                                         id=cycleId, title=self.projet)
#         
#         print '%s/%s/edit' % (context.absolute_url(),cycleId)
#         self.next = '%s/%s/edit' % (context.absolute_url(),cycleId)
#         return '%s/%s/edit' % (context.absolute_url(),cycleId)
# 
#     def set_label(self):
#         if not hasattr(self.request,'newprojet'):
#             return _(u'Déposer un nouveau projet')
#         return _(u'Compléter le nouveau projet')
#         
#     def form_action(self, widget, data):
#         import pdb; pdb.set_trace()
#         if not 'newprojet' in data.keys() or not data['newprojet'].extracted:
#             self.newprojet = ''
#             return ''
#         self.newprojet = data['newprojet'].extracted
#         context = aq_inner(self.context)
#         catalog = getToolByName(self.context, 'portal_catalog')
#         cat = cat(object_provides= ICycle.__identifier__,
#                    path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
#                    sort_on="modified", sort_order="reverse")  
#         print "cat len = ", len(cat), cat
#         cycleId = "%s-%i" % (context.start,(len(cat)+1))
#         item = createContentInContainer(context, "ageliaco.rd2.cycle", 
#                                         id=cycleId, title=self.newprojet)
#         self.nextId = cycleId
#         self.next = item.absolute_url() + '/edit'
#         
#         return self.next #self.context.absolute_url() + '/depot?newprojet=' + self.newprojet
# 
#     def submit_action(self, widget, data):
#         #import pdb; pdb.set_trace()
# 
#         return self.next

#     def form_handler(self, widget, data):
#         #import pdb; pdb.set_trace()
#         self.newprojet = self.result()
#         context = aq_inner(self.context)
#         if not hasattr(self,'newprojet') or not self.newprojet:
#             error = ExtractionError(
#                 'Complétez le titre du projet!')
#             return self.context.absolute_url()
#         import pdb; pdb.set_trace()
#         data.value = self.next
#         return self.next

#     
#     def result(self):
#         if not hasattr(self,'newprojet') or not self.newprojet:
#             return ''
#         return self.newprojet
#     
#     def nextform(self,request):
# 
#         import pdb; pdb.set_trace()
#         if not hasattr(self.request,'myform.newprojet') \
#             or not hasattr(self.request,'myform.projet'):
#             return ''
# 
#         context = aq_inner(self.context)
#         
#         title = ''
#         description = ''
#         presentation = ''
#         
#         # in case of new project
#         if hasattr(self.request,'myform.newprojet') \
#             and self.request['myform.newprojet']:
#             
#             self.newprojet = self.request['myform.newprojet']
#             title = self.newprojet
#             description = ''
#             presentation = ''
#         
#         # in case of reconduction of an active project
#         if hasattr(self.request,'myform.projet') \
#             and self.request['myform.projet']:
#             
#             self.projet = self.request['myform.projet']
#             proj = context.unrestrictedTraverse(self.projet)
#             title = proj.title
#             description = proj.description
#             presentation = proj.presentation.raw
#         
#             
#         catalog = getToolByName(self.context, 'portal_catalog')
#         cat = catalog(object_provides= ICycle.__identifier__,
#                    path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
#                    sort_on="modified", sort_order="reverse")  
#         print "cat len = ", len(cat), cat
#         cycleId = "%s-%i" % (context.start,(len(cat)+1))
#         item = createContentInContainer(context, "ageliaco.rd2.cycle", 
#                                         id=cycleId, title=title,
#                                         description=description, 
#                                         presentation=presentation)
#         self.nextId = cycleId
#         self.next = item.absolute_url() + '/editusers'
#         form2 = factory(
#             'form',
#             name='myform2',
#             props={
#                 'action': self.submit_action,
#             })
# 
#         # form widgets creation here...
#         form2['title'] = factory(
#             'field:label:error:text',
#             props={
#                 'label': u'Titre du projet',
#                 'default': title,
#                 'field.class': 'field',
#         })
# 
#         form2['subtitle'] = factory(
#             'field:label:error:textarea',
#             props={
#                 'label': u'sous-titre du projet',
#                 #'placeholder': description,
#                 'default' : description,
#                 'field.class': 'field',
#                 'rows' : 2,
#         })
# 
#         form2['presentation'] = factory(
#             '#field:richtext',
#             props={
#                 'label': u'Présentation résumée du projet',
#                 #'placeholder': presentation,
#                 'default' : presentation,
#                 'field.class': 'field',
#                 'required': 'Text is required',
#         })
# 
#         form2['submit'] = factory(
#             'field:submit',
#             props={
#                 'label': (u'Compléter le projet'),
#                 'submit.class': 'btn-primary',
#                 #'handler': self.form_handler,
#                 'action' : True,
#         })
# 
#         form2['fieldset'] = factory(u'fieldset', name='yafowilwidgetrichtext')
#         form2['richtext'] = factory('#field:wysihtml5', props={
#             'label': 'WYSIHTML5 Field',
#             'default' : presentation,
#             'required': 'Text is required'})
# 
#         self.form2 = form2
#         controller = Controller(self.form2, self.request)
#         return controller.rendered
# 
#     def activeProjets(self):
#         catalog = getToolByName(self.context, 'portal_catalog')
#         cat = catalog(portal_type='ageliaco.rd2.projet',
#                        review_state='encours',
#                        sort_on='sortable_title')
#         #log('catalogue : %s items'%len(cat))
#     
#         terms = [('',''),]
#                     
#         for brain in cat:
#             print dir(brain)
#             print "getURL : %s => getPath : %s " % (brain.getURL(),brain.getPath())
#             terms.append((brain.getPath(),brain.Title))
#         return terms #SimpleVocabulary([SimpleVocabulary.createTerm(x.id, x.getURL(), x.Title) for x in cat])
    

class View(grok.View,Form):
    grok.context(IProjet)
    grok.require('zope2.View')

    def _form_handler(self, widget, data):
        if not hasattr(self.request,'form1.newprojet') \
            and not self.request['form1.newprojet']:
            return ''
        self.request['form1.action'] = self.context.absolute_url() + '/edit'
        self.request['form1.submit.next'] = self.nextform
        title = self.request['form1.newprojet']
        context = aq_inner(self.context)
        #         catalog = getToolByName(self.context, 'portal_catalog')
        #         cat = catalog(object_provides= ICycle.__identifier__,
        #                    path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
        #                    sort_on="modified", sort_order="reverse")  
        #         print "cat len = ", len(cat), cat
        #         cycleId = "%s-%i" % (context.start,(len(cat)+1))
        new_id = idDefaultFromContext(context) #"%s-%s" %(context.start,len(context.objectIds()))
        item = createContentInContainer(context, "ageliaco.rd2.cycle", id=new_id, 
                    title=title,
                    presentation=RichTextValue(
                        raw=cycle_default_projet_presentation
                    ),
                    problematique=RichTextValue(
                        raw=cycle_default_problematique
                    ))
        self.request['form1.cycleId'] = item.id


    def _form_action(self, widget, data):
        if  hasattr(self.request,'form1.newprojet') \
            and self.request['form1.newprojet']:
            #self.form_handler(widget,data)
            pass

        if not hasattr(self.request,'form1.cycleId') \
            or not self.request['form1.cycleId']:
            #self.request['form1.submit.next'] = self.nextform
            return self.context.absolute_url() 
        return self.context.absolute_url() + '/edit'
        #return self.form_handler
        

    def nextform(self,request):
        #import pdb; pdb.set_trace()
        #return self.context.absolute_url() + '/depot'
        if not hasattr(self.request,'form1.cycleId') \
            or not self.request['form1.cycleId']:
            return ''

        form = factory(
            'form',
            name='form1',
            props={
                'action': self.submit_action,
            })


        form['submit'] = factory(
            'field:submit',
            props={
                'label': (u'Compléter le projet'),
                'submit.class': 'btn-primary',
                #'handler': self.form_handler,
                'action' : 'complation',
        })

        form['cycleId'] = factory(
            'field:label',
            props={
                'label' : self.request['form1.cycleId'],
        })


        self.form = form
        #return self.form
        controller = Controller(self.form, self.request)
        return controller.rendered
        
    def prepare(self):
        form = factory(
            'form',
            name='form1',
            props={
                'action': self._form_action,
            })

        form['cycleId'] = factory(
            'field:hidden',
            props={
                'label' : '',
        })

        # form widgets creation here...
        form['newprojet'] = factory(
            'field:label:error:text',
            props={
                'label': _(u'Titre du nouveau projet : '),
                'field.class': 'field',
                'text.class': 'text',
                'size': '80',
        })
        form['submit'] = factory(
            'field:submit',
            props={
                'label': _(u'Créer un nouveau projet'),
                'submit.class': 'btn-primary',
                'handler': self._form_handler,
                'action': 'save',
                'next' : self.nextform,
                #'skip' : hasattr(self.request,'form1.cycleId'),
        })


        reconductionform = form['reconduction'] = factory(
            'fieldset',
            props={
                'legend': _(u'Reconduction d\'un projet existant'),
                'class': 'reconduction',
        })
        reconductionform['projet'] = factory(
            'field:label:error:select',
            props={
                'label': _(u'Reconduire le projet choisi dans la liste'),
                'field.class': 'field',
                'select.class': 'select',
                'vocabulary': self.activeProjets,
        })
        reconductionform['submit'] = factory(
            'field:submit',
            props={
                'label': _(u'Reconduire le projet'),
                'submit.class': 'btn-primary',
                'handler': self.form_handler2,
                'action': 'save',
                'next' : self.nextform,
                #'skip' : hasattr(self.request,'form1.cycleId') and self.request['form1.cycleId'],
        })

        self.form = form
        #controller = Controller(form, self.request)
        #return controller.rendered

    def submit_action(self, widget, data):
        #import pdb; pdb.set_trace()
        
        if not hasattr(self.request,'form1.cycleId') \
            or not self.request['form1.cycleId']:
            return ''
        cycleId = self.request['form1.cycleId']
        return self.context.absolute_url() + '/%s/edit' % cycleId

    def inBTwin(self):
        if (hasattr(self.request,'form1.newprojet') \
            and self.request['form1.newprojet']) \
            or (hasattr(self.request,'form1.projet') \
            and self.request['form1.projet']):
            return True
        return False

    def newprojet(self):
        #import pdb; pdb.set_trace()
        if hasattr(self.request,'form1.newprojet') \
            and self.request['form1.newprojet']:
            return self.request['form1.newprojet']
        return ''
    
    def reconductprojet(self):
        #import pdb; pdb.set_trace()
        if hasattr(self.request,'form1.reconduction.projet') \
            and self.request['form1.reconduction.projet']:
            return self.request['form1.reconduction.projet']
        return ''
    
    def form_handler2(self, widget, data):
        if not hasattr(self.request,'form1.reconduction.projet') \
            and not self.request['form1.reconduction.projet']:
            return ''
        projetpath = self.request['form1.reconduction.projet']
        
        # look for last cycle in projetpath
        context = aq_inner(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        cat = catalog(object_provides= ICycle.__identifier__,
                   path={'query': projetpath, 'depth': 1},
                   sort_on="modified", sort_order="reverse")  
        
        portal_url = getToolByName(context, "portal_url")
        portal = portal_url.getPortalObject()
        # clone the cycle in a new cycle here and remove anything other than auteurs in the new cycle
        # Bypass security
        projet = portal.unrestrictedTraverse(projetpath)
        
        item = None
        #getting a copy of last cycle
        #import pdb; pdb.set_trace()
        if len(cat):
            try:
                ids = context.manage_pasteObjects(projet.manage_copyObjects(cat[0].id)) 
                #context.manage_renameObject(newcycle.id, id + "-old")
                cycleId = ids[0]['new_id']
                item = context[cycleId]
                new_id = idDefaultFromContext(context) #"%s-%s" %(context.start,len(context.objectIds()))
                item.aq_parent.manage_renameObject(cycleId, str(new_id))
                cycleId = new_id
                if not item.presentation:
                    item.presentation = RichTextValue(
                            raw=cycle_default_projet_presentation
                        ) 
                item.problematique = RichTextValue(
                        raw=cycle_default_problematique
                    ) 
                #removing notes in new cycle
                cat = catalog(object_provides= INote.__identifier__,
                           path={'query': '/'.join(item.getPhysicalPath()), 'depth': 1},
                           sort_on="modified", sort_order="reverse")  
                for note in cat:
                    del item[note.id]
            except: #creating a new cycle
                new_id = idDefaultFromContext(context)
                item = createContentInContainer(context, "ageliaco.rd2.cycle", id=new_id, title="")
                item.projet = projetpath
                item.presentation = RichTextValue(
                        raw=cycle_default_projet_presentation
                    ) 
                item.problematique = RichTextValue(
                        raw=cycle_default_problematique
                    ) 
                
                
        else: #creating a new cycle
            title = self.request['form1.newprojet']
            context = aq_inner(self.context)
        #             catalog = getToolByName(self.context, 'portal_catalog')
        #             cat = catalog(object_provides= ICycle.__identifier__,
        #                        path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
        #                        sort_on="modified", sort_order="reverse")  
        #             print "cat len = ", len(cat), cat
        #             cycleId = "%s-%i" % (context.start,(len(cat)+1))
            item = createContentInContainer(context, "ageliaco.rd2.cycle", title=title)
             
        self.request['form1.cycleId'] = item.id
        self.request['form1.action'] = item.absolute_url() + '/edit'
        self.request['form1.submit.next'] = self.nextform
        title = self.request['form1.newprojet']
       

    def activeProjets(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        cat = catalog(portal_type='ageliaco.rd2.projet',
                       review_state='encours',
                       sort_on='sortable_title')
        #log('catalogue : %s items'%len(cat))
    
        terms = [('',''),]
                    
        for brain in cat:
            #print dir(brain)
            #print "getURL : %s => getPath : %s " % (brain.getURL(),brain.getPath())
            terms.append((brain.getPath(),brain.Title))
        return terms #SimpleVocabulary([SimpleVocabulary.createTerm(x.id, x.getURL(), x.Title) for x in cat])
    
    def canRequestReview(self):
        return checkPermission('cmf.RequestReview', self.context)

    def logo_url(self):
        context = aq_inner(self.context)
        portal_url = getToolByName(context, 'portal_url')
        if 'logo.png' in context.keys():
            return context.absolute_url() + '/logo.png'
        return portal_url + '/++resource++ageliaco.rd/screens.png'      

    def noCycle(self):
        context = aq_inner(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        cat = catalog(object_provides= ICycle.__identifier__,
                   path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
                   sort_on="modified", sort_order="reverse")     
        if len(cat)>0:
            return False
        return True
        
    def canAddContent(self, context=None):
        if not context:
            context = self.context            
        return checkPermission('cmf.AddPortalContent', context)
            
    def canModifyContent(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)
        
        
    def cycles_obj(self):
        #return a list of actual cycle objects
        context = aq_inner(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        cat = catalog(object_provides= ICycle.__identifier__,
                   path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
                   sort_on="modified", sort_order="reverse")     
        return cat
        
    def review_state(self):
        context = aq_inner(self.context)
        portal_workflow = getToolByName(context, 'portal_workflow')
        review_state = portal_workflow.getInfoFor(context, 'review_state')
        return review_state
        
    def isRepository(self):
        context = aq_inner(self.context)
        portal_workflow = getToolByName(context, 'portal_workflow')
        review_state = portal_workflow.getInfoFor(context, 'review_state')
        return review_state == u'repository'
        

    def contributeurs(self,cycle_id):
        context = aq_inner(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        if cycle_id in context.keys():
            cycle = context[cycle_id]  
            if cycle:
                cat = catalog(object_provides= IAuteur.__identifier__,
                           path={'query': '/'.join(cycle.getPhysicalPath()), 'depth': 1},
                           sort_on="modified", sort_order="reverse")     
                return cat
        return None
    
    def hasRealisation(self):
        context = aq_inner(self.context)
        if not context.has_key('realisation'):
            return ""
        if len(context['realisation'].keys()) or self.canAddContent(context['realisation']):
            return context['realisation'].absolute_url()
        return ""
    
    
    def hasLink(self):
        context = aq_inner(self.context)
        #pdb.set_trace()
        
        if getattr(context,'lien',0):
            #print context.getAttribute('lien')
            return context.lien
        #         else:
        #             print "no Property 'link'"
        return ''
    
            
