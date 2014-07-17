# -*- coding: UTF-8 -*-
from plone.dexterity.utils import createContent
from plone.dexterity.utils import createContentInContainer
from Products.CMFPlone.utils import log
from Products.CMFCore.utils import getToolByName
from plone.app.textfield.value import RichTextValue

def reproposeCycle(self, state_change):
    """ sends an email to the school's director """
    print "reproposeCycle called !!!"
    dest_folder = None
    workflowTool = getToolByName(self, "portal_workflow")
    contentObject = state_change.object
    parent = contentObject.aq_parent
    
    parentState = workflowTool.getStatusOf("rd2.projet-workflow", parent)["review_state"]
    
    if parentState == 'archives':
        return #no moving required
    portal = self.portal_url.getPortalObject()
    catalog = getToolByName(portal,'portal_catalog')
    cat = catalog(portal_type='ageliaco.rd2.projet',
                   review_state='repository')
    
    if not len(cat):
        log("No ageliaco.rd2.projet archive => cannot migrate cycle to projet repository!")
        return
    
    projet = cat[0].getObject()
    
    objectOwner = contentObject.Creator()
    projetPath = cat[0].getPath()
    try:
        # trying to cut => won't work if on the object itself, will work 
        # if from folderContent of the parent
        projet.manage_pasteObjects(parent.manage_copyObjects(contentObject.id)) 
        log("try copy OK!")
        n = len(projet.keys())
        projet.manage_renameObject(contentObject.id, projet.start + str(n))
    except: 
        log("couldn't copy => then nothing instead")
    return  

def retractCycle(self, state_change):
    pass

def archiveCycle(self, state_change):
    """ sends an email to the school's director """
    print "archiveCycle called !!!"
    dest_folder = None
    workflowTool = getToolByName(self, "portal_workflow")
    contentObject = state_change.object
    parent = contentObject.aq_parent
    
    parentState = workflowTool.getStatusOf("rd2.projet-workflow", 
                    parent)["review_state"]
    
    if parentState == 'archives':
        return #no moving required
    portal = self.portal_url.getPortalObject()
    catalog = getToolByName(portal,'portal_catalog')
    cat = catalog(portal_type='ageliaco.rd2.projet',
                   review_state='archives')
    
    if not len(cat):
        log("No ageliaco.rd2.projet archive => cannot migrate" +
            "cycle to projet archives!")
        return
    
    projet = cat[0].getObject()
    
    objectOwner = contentObject.Creator()
    projetPath = cat[0].getPath()
    #import pdb; pdb.set_trace()
    try:
        # trying to cut => won't work if on the object itself, will work 
        # if from folderContent of the parent
        projet.manage_pasteObjects(parent.manage_cutObjects([contentObject.id])) 
        log("try cut OK!")
    except: 
        projet.manage_pasteObjects(
            parent.manage_copyObjects([contentObject.id])
            )   
        log("couldn't cut => then copy instead")
    return  
    
def finaliseCycle(self, state_change):
    """ sends an email to the school's director """
    print "finaliseCycle called !!!"
    cycle = state_change.object
    owners = [auteur for auteur,roles in cycle.get_local_roles() \
                                    if 'Owner' in roles]
    for owner in owners:
        cycle.manage_setLocalRoles(owner, ['Reader','Owner'])
    cycle.reindexObjectSecurity()

    
def attributeCycle(self, state_change):
    """ sends an email to the school's director """
    print "attributeCycle called !!!"
    #pass
    
def publishProjet(self, state_change):
    """ finish any active cycle """
    print "publishCycle called !!!"
    #pass
    
def activateCycle(self, state_change):
    """ activate Cycle and moving it to known projet or new one """
    print "activateCycle called !!!"
    ## Script (Python) "move_published_content"
    ##bind container=container
    ##bind context=context
    ##bind namespace=
    ##bind script=script
    ##bind subpath=traverse_subpath
    ##parameters=state_change
    ##title=Move published content to subfolder of portal root
    ##
    # missing :     - sharing of projet for all auteurs in cycle (reader)
    #               - sharing of projet/realisation (reader,editor,contributor)
    dest_folder = None
    workflowTool = getToolByName(self, "portal_workflow")
    contentObject = state_change.object
    cycle = contentObject
    parent = contentObject.aq_parent
    
    parentState = workflowTool.getStatusOf("rd2.projet-workflow", 
                                        parent)["review_state"]
    portal = self.portal_url.getPortalObject()
    catalog = getToolByName(portal,'portal_catalog')
    cat = catalog(portal_type='ageliaco.rd2.projets',
                   review_state='published')
    
    if not len(cat):
        log("No ageliaco.rd2.projets published => cannot migrate cycle to projet !")
        return False
    
    #there should be only one ageliaco.rd2.projets object
    projets = cat[0].getObject()
    
    cat = catalog(portal_type='ageliaco.rd2.projet',
                   review_state='repository')
                   
    #there should be only one ageliaco.rd2.projet object with state 'repository'
    depot_url = cat[0].getURL()
    objectOwner = contentObject.Creator()
    projetPath = contentObject.projet
    #import pdb; pdb.set_trace()
    if not projetPath: 
        #we must create a new one if grandpa is not "projets"
        if depot_url in parent.absolute_url():
            projet = createContentInContainer(projets,'ageliaco.rd2.projet', 
                title=contentObject.Title(), duration=contentObject.duree, 
                presentation=RichTextValue(
                raw=contentObject.description.raw
                ))
            try:
                # trying to cut => won't work if on the object itself, 
                # will work if from folderContent of the parent
                projet.manage_pasteObjects(parent.manage_cutObjects(
                                        contentObject.id)
                                        ) 
                log("try cut OK!")
            except: 
                projet.manage_pasteObjects(
                        parent.manage_copyObjects(contentObject.id)
                        )   
                log("couldn't cut => then copy instead")    
            contentObject.projet = projet.absolute_url()  
            parent = projet     
        else:
            contentObject.projet = parent.absolute_url() #ne marche pas !!!
            #return
        
        print "Parent : ", parent, contentObject.id, parent.objectIds()
        #cb_copy_data = parent.manage_cutObjects(contentObject.id)
    # projet and realisation sharing for auteurs
    cyclepath = '/'.join(cycle.getPhysicalPath())
    auteurBrains = catalog(portal_type='ageliaco.rd2.auteur',
                    path={'query': cyclepath, 'depth': 1})

    for auteur in auteurBrains:
        parent.manage_addLocalRoles(auteur.id, ['Reader','Editor','Contributor'])
    
    if parentState == 'draft':
        workflowTool.doActionFor(parent, "activate")
    owners = [auteur for auteur,roles in cycle.get_local_roles() \
                                    if 'Owner' in roles]
    for owner in owners:
        parent.manage_setLocalRoles(owner, ['Reader','Owner'])
    parent.reindexObjectSecurity()
    
    return  
