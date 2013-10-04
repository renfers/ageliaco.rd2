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
        # trying to cut => won't work if on the object itself, will work if from folderContent of the parent
        projet.manage_pasteObjects(parent.manage_copyObjects(contentObject.id)) 
        log("try copy OK!")
        n = len(projet.keys())
        projet.manage_renameObject(contentObject.id, projet.start + str(n))
    except: 
        log("couldn't copy => then nothing instead")
    return  

def archiveCycle(self, state_change):
    """ sends an email to the school's director """
    print "archiveCycle called !!!"
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
                   review_state='archives')
    
    if not len(cat):
        log("No ageliaco.rd2.projet archive => cannot migrate cycle to projet archives!")
        return
    
    projet = cat[0].getObject()
    
    objectOwner = contentObject.Creator()
    projetPath = cat[0].getPath()
    #import pdb; pdb.set_trace()
    try:
        # trying to cut => won't work if on the object itself, will work if from folderContent of the parent
        projet.manage_pasteObjects(parent.manage_cutObjects([contentObject.id])) 
        log("try cut OK!")
    except: 
        projet.manage_pasteObjects(parent.manage_copyObjects([contentObject.id]))   
        log("couldn't cut => then copy instead")
    return  
    
def finaliseCycle(self, state_change):
    """ sends an email to the school's director """
    print "finaliseCycle called !!!"
    #pass
    
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
    parent = contentObject.aq_parent
    
    parentState = workflowTool.getStatusOf("rd2.projet-workflow", parent)["review_state"]
    
    if parentState == 'encours':
        return #no moving required
    portal = self.portal_url.getPortalObject()
    catalog = getToolByName(portal,'portal_catalog')
    cat = catalog(portal_type='ageliaco.rd2.projets',
                   review_state='published')
    
    if not len(cat):
        log("No ageliaco.rd2.projets published => cannot migrate cycle to projet !")
        return
    
    projets = cat[0].getObject()
    
    cat = catalog(portal_type='ageliaco.rd2.projet',
                   review_state='repository')
    depot_url = cat[0].getURL()
    objectOwner = contentObject.Creator()
    projetPath = contentObject.projet
    import pdb; pdb.set_trace()
    if not projetPath: 
        #we must create a new one if grandpa is not "projets"
        if depot_url in parent.absolute_url():
            projet = createContentInContainer(projets,'ageliaco.rd2.projet', 
                title=contentObject.Title(), duration=1, presentation=RichTextValue(
                raw=contentObject.presentation.raw
                ))
            try:
                # trying to cut => won't work if on the object itself, will work if from folderContent of the parent
                projet.manage_pasteObjects(parent.manage_cutObjects(contentObject.id)) 
                log("try cut OK!")
            except: 
                projet.manage_pasteObjects(parent.manage_copyObjects(contentObject.id))   
                log("couldn't cut => then copy instead")            
        else:
            contentObject.projet = parent.absolute_url() #ne marche pas !!!
            return
        #print "Parent : ", parent, contentObject.id, parent.objectIds()
        #cb_copy_data = parent.manage_cutObjects(contentObject.id)
    else:
        projetId = projetPath.split('/')[-1]
        print projetPath, projetId, projets
        if projetId not in projets.keys() and not projets[projetId]:
            log('Problem, cannot find projet %s in %s !' % (projetPath, projets.id))
            self.context.addStatusMessage(u'Problème, projet %s pas trouvé dans %s !' % (projetPath, projets.id))
            return False
        projet = projets[projetId]
        parent = contentObject.aq_parent
        print "Parent : ", parent, contentObject.id, parent.objectIds()
        #cb_copy_data = parent.manage_cutObjects(contentObject.id)
        try:
            # trying to cut => won't work if on the object itself, will work if from folderContent of the parent
            projet.manage_pasteObjects(parent.manage_cutObjects(contentObject.id)) 
            log("try cut OK!")
        except: 
            projet.manage_pasteObjects(parent.manage_copyObjects(contentObject.id))   
            log("couldn't cut => then copy instead")
    return  
