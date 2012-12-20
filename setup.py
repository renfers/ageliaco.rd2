from setuptools import setup, find_packages
import os

version = '0.6'

setup(name='ageliaco.rd2',
      version=version,
      description="new implementantion of RD service",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='ageliaco rd project management',
      author='Serge Renfer',
      author_email='serge.renfer@gmail.com',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ageliaco'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity',
          'collective.autopermission',
          # -*- Extra requirements: -*-
          'Plone',
          'plone.principalsource',
          'plone.app.users >= 1.0b7',
          'collective.wtf',
          'plone.namedfile[blobs]',
          'plone.formwidget.namedfile',
          'collective.z3cform.datagridfield',
          'collective.z3cform.wizard',
          'yafowil.plone',
        ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
