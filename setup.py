#!/usr/bin/env python

from distutils.core import setup

setup(name='rwiparsing',
      version='1.2',
      description='Parsing of Remcom Wireless InSite .p2m files',
      author='LASSE',
      author_email='pedosb@gmail.com',
      url='https://github.com/lasseufpa/5gm-rwi-simulation',
      packages=['rwiparsing'],
      requires=['numpy(>=1.14)']
      )