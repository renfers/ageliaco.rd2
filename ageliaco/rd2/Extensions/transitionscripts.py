# -*- coding: UTF-8 -*-
from plone.dexterity.utils import createContent
from plone.dexterity.utils import createContentInContainer
from Products.CMFPlone.utils import log
from Products.CMFCore.utils import getToolByName

def archiveCycle(self, state_change):
    """ sends an email to the school's director """
    print "archiveCycle called !!!"
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
    
    objectOwner = contentObject.Creator()
    projetPath = contentObject.projet
    if not projetPath: 
        #we must create a new one if grandpa is not "projets"
        if 'depot-de-projet' in parent.absolute_url().split('/'):
            projet = createContentInContainer(projets,'ageliaco.rd2.projet', 
                title=contentObject.Title, duration=1, presentation=u" ")
        else:
            contentObject.projet = parent.absolute_url() #ne marche pas !!!
            
    else:
        projetId = projetPath.split('/')[-1]
        print projetPath, projetId, projets
        projet = projets[projetId]
        if not projet:
            log('Problem, cannot find projet %s in %s !' % (projetPath, projets.id))
            return
        parent = contentObject.aq_parent
        print "Parent : ", parent, contentObject.id, parent.objectIds()
        #cb_copy_data = parent.manage_cutObjects(contentObject.id)
        try:
            # trying to cut => won't work if on the object itself, will work if from folderContent of the parent
            print "try cut OK!"
            projet.manage_pasteObjects(parent.manage_cutObjects(contentObject.id)) 
        except: 
            print "couldn't cut => then copy instead"
            projet.manage_pasteObjects(parent.manage_copyObjects(contentObject.id))   
    return  
#         dest_folder = projet
#         print "dest_folder.id = ", dest_folder.id
#     
#         content_folder = contentObject.aq_parent
#         content_id = contentObject.getId()
#         dest_folder.manage_pasteObjects(content_folder.manage_cutObjects(content_id))    
