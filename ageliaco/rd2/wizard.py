# -*- coding: UTF-8 -*-
from zope import schema, interface
from zope.interface import implements
from z3c.form import field, form
from collective.z3cform.wizard import wizard
from plone.z3cform.fieldsets import group
from plone.z3cform.layout import FormWrapper
from Products.statusmessages.interfaces import IStatusMessage
from Products.statusmessages.adapter import _decodeCookieValue

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.form.browser.checkbox import CheckBoxFieldWidget

from Products.Five import BrowserView

from five import grok

from interface import IProjet


from ageliaco.rd2 import _


countries = SimpleVocabulary([SimpleTerm(value="not_selected", title=_("Chose your region")),
                            SimpleTerm(value="belgium", title=_("Belgium")),
                            SimpleTerm(value="canada", title=_("Canada")),
                            SimpleTerm(value="us", title=_("United States")),
                            ])
products = SimpleVocabulary([SimpleTerm(value="product1", title=_("Product1")),
                            SimpleTerm(value="product2", title=_("Product2")),
                            SimpleTerm(value="product3", title=_("Product3")),
                            SimpleTerm(value="product4", title=_("Product4")),
                            SimpleTerm(value="product5", title=_("Product5"))
                            ])
class Step1(wizard.Step):
    prefix = 'one'
    fields = field.Fields(schema.Choice(__name__="region",
                                title=_("Select your region"), vocabulary=countries,
                                required=True, default="not_selected")
                        )
class Step2(wizard.Step):
    prefix = 'two'
    fields = field.Fields(schema.List(__name__="product",
                                value_type=schema.Choice(
                                    title=_("Select your product"),
                                    vocabulary=products),
                                    required=True
                                    )
                        )
    for fv in fields.values():
        fv.widgetFactory = CheckBoxFieldWidget


class WizardForm(wizard.Wizard):
    label= _("Find Product")
    steps = Step1, Step2
    def finish(self):
        ##check answer here
        print dir(self)
        #import pdb; pdb.set_trace()

class WizardView(FormWrapper):
    grok.context(IProjet)
    grok.name('wizard')
    grok.require('zope2.View')

    form = WizardForm
    def __init__(self, context, request):
        FormWrapper.__init__(self, context, request)
    def absolute_url(self):
        return '%s/%s' % (self.context.absolute_url(), self.__name__)