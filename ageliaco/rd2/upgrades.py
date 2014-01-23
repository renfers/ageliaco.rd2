import logging
from zope.schema import getFieldsInOrder
from Products.CMFCore.utils import getToolByName
from interface import ICycle
from zope.component import getUtility
from plone.dexterity.interfaces import IDexterityFTI

PROFILE_ID='profile-ageliaco.rd2:default'

def convert_to_new_cycle(context, logger=None):
    """Method to convert old cycle objects to new schema (more attributes).

    When called from the import_various method, 'context' is
    the plone site and 'logger' is the portal_setup logger.

    But this method will be used as upgrade step, in which case 'context'
    will be portal_setup and 'logger' will be None.

    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('ageliaco.rd2')

    # Run the catalog.xml step as that may have defined new metadata
    # columns.  We could instead add <depends name="catalog"/> to
    # the registration of our import step in zcml, but doing it in
    # code makes this method usable as upgrade step as well.
    # Remove these lines when you have no catalog.xml file.
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type='ageliaco.rd2.cycle')
    schema = getUtility(IDexterityFTI, name='ageliaco.rd2.cycle').lookupSchema()
    count = 0
    for content in brains:
        changed = False
        obj = content.getObject()
        fields = getFieldsInOrder(schema)
        for id, field in fields:
            #if ICycle.providedBy(field):
            try:
                attr = getattr(obj,id)
                if attr==None or type(attr)==None:
                    changed = True
                    print id, obj
                    default = field.default
                    if default==None:
                        default = field._type()
                    #import pdb; pdb.set_trace()
                    setattr(obj, id, default)
                
            except:
                changed = True
                logger.info(
                    "Could not change this field (%s) in this cycle : %s !"%\
                        (id,obj)
                    )
        if changed:
            count += 1
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')
    logger.info("%s Cycle objects converted." % count)
    
def convert_to_new_note(context, logger=None):
    """Method to convert old note objects to new schema (less attributes).

    When called from the import_various method, 'context' is
    the plone site and 'logger' is the portal_setup logger.

    But this method will be used as upgrade step, in which case 'context'
    will be portal_setup and 'logger' will be None.

    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('ageliaco.rd2')

    # Run the catalog.xml step as that may have defined new metadata
    # columns.  We could instead add <depends name="catalog"/> to
    # the registration of our import step in zcml, but doing it in
    # code makes this method usable as upgrade step as well.
    # Remove these lines when you have no catalog.xml file.
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type='ageliaco.rd2.note')
    schema = getUtility(IDexterityFTI, name='ageliaco.rd2.note').lookupSchema()
    count = 0
    for content in brains:
        changed = False
        obj = content.getObject()
        fields = getFieldsInOrder(schema)
        for id, field in fields:
            try:
                attr = getattr(obj,id)
                if attr==None or type(attr)==None:
                    changed = True
                    print id, obj
                    default = field.default
                    if default==None:
                        default = field._type()
                    #import pdb; pdb.set_trace()
                    setattr(obj, id, default)
                
            except:
                changed = True
                logger.info(
                    "Could not change this field (%s) in this note : %s !"%\
                        (id,obj)
                    )
        if changed:
            count += 1
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')
    logger.info("%s Note objects converted." % count)   

def set_authors_to_cycle(context, logger=None):
    """Method for old cycle objects to set authors in 'participants' field.

    When called from the import_various method, 'context' is
    the plone site and 'logger' is the portal_setup logger.

    But this method will be used as upgrade step, in which case 'context'
    will be portal_setup and 'logger' will be None.

    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('ageliaco.rd2')

    # Run the catalog.xml step as that may have defined new metadata
    # columns.  We could instead add <depends name="catalog"/> to
    # the registration of our import step in zcml, but doing it in
    # code makes this method usable as upgrade step as well.
    # Remove these lines when you have no catalog.xml file.
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type='ageliaco.rd2.cycle')
    schema = getUtility(IDexterityFTI, name='ageliaco.rd2.cycle').lookupSchema()
    count = 0
    for content in brains:
        changed = False
        obj = content.getObject()
        attr = getattr(obj,'participants',None)
        if attr == '':
            for id in obj.keys():
                subobj = obj[id]
                if subobj.portal_type=='ageliaco.rd2.auteur':
                    obj.participants += "%s\n" % id
                    changed = True
        if changed:
            count += 1
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')
    logger.info("Cycle authors added to %s old cycles." % count)
    
def convert_projet_to_leadimage(context, logger=None):
    """Method to change the attribute "picture" to lead-image behavior "image".

    When called from the import_various method, 'context' is
    the plone site and 'logger' is the portal_setup logger.

    But this method will be used as upgrade step, in which case 'context'
    will be portal_setup and 'logger' will be None.

    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('ageliaco.rd2')

    # Run the catalog.xml step as that may have defined new metadata
    # columns.  We could instead add <depends name="catalog"/> to
    # the registration of our import step in zcml, but doing it in
    # code makes this method usable as upgrade step as well.
    # Remove these lines when you have no catalog.xml file.
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(portal_type='ageliaco.rd2.projet')
    schema = getUtility(IDexterityFTI, name='ageliaco.rd2.projet').lookupSchema()
    count = 0
    for content in brains:
        changed = False
        obj = content.getObject()
        fields = getFieldsInOrder(schema)
        if hasattr(obj,'picture'):
            attr = getattr(obj,'picture')
            if attr == None:
                continue
            try:
                setattr(obj,'image',attr)
                changed = True
                logger.info("Image changed for %s" % obj.id)
            except:
                logger.info("!!! Image could not be changed for %s !!!" % obj.id)
            
            if changed:
                count += 1
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')
    logger.info("%s Note objects converted." % count)   


def upgrade_from_2_to_3(context):
    print "Upgrading from 2 to 3"
    context.runImportStepFromProfile(default_profile, 'controlpanel') 

def upgrade_from_3_to_4(context):
    print "Upgrading from 3 to 4"
    context.runImportStepFromProfile(default_profile, 'controlpanel') 
    
def upgrade_from_3_to_4(context):
    print "Upgrading from 4 to 5"
    context.runImportStepFromProfile(default_profile, 'controlpanel')     