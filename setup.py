#!/usr/bin/env python

from distutils.core import setup

setup(name='svbtle_subscriber',
      version='0.1',
      description='Get rss feed addresses for all writers on svbtle.com',
      author='Luke Lee',
      author_email='durdenmisc@gmail.com',
      url='http://github.com/durden/svbtle_subscriber',
      py_modules=['svbtle_subscriber'],
      entry_points={
          'console_scripts': ['svbtle_subscriber = svbtle_subscriber:main']
      }
    )
