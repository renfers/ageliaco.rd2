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
                logger.info("Could not change this field (%s) in this cycle : %s !"%(id,obj))
        if changed:
            count += 1
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')
    logger.info("%s Cycle objects converted." % count)