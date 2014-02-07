#!/usr/bin/env python

from distutils.core import setup
from lib601.version import version

setup(name='lib601',
      version=version,
      description='6.01 Code Distribution',
      author='6.01 Staff',
      author_email='6.01-help@mit.edu',
      license='GPLv2',
      url='http://mit.edu/6.01/',
      packages = ['lib601','form','soar','soar.io','soar.graphics','soar.serial','soar.controls','soar.outputs'],
      package_data={'lib601': ['*.pyc','sigFiles/*'],'soar': ['media/*','worlds/*']},
      scripts=['installsoar.py', 'lib601/CMax','soar/soar'],
     )
