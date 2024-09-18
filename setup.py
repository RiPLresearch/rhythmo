#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools

# Package meta-data.
NAME = 'Rhythmo'
DESCRIPTION = 'Rythmo identifies cycles in physiological rhythms and predicts future phases'
URL = 'https://github.com/RiPLresearch/rhythmo'
EMAIL = 'rachelstirling1@gmail.com'
AUTHOR = 'Rachel E. Stirling'
REQUIRES_PYTHON = '>=3.11.8'
VERSION = '1.0.0'

install_requires = ['click==8.1.7', 'pycwt==0.4.0b0']

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name=NAME,
                 version=VERSION,
                 author=AUTHOR,
                 author_email=EMAIL,
                 description=DESCRIPTION,
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 url=URL,
                 packages=setuptools.find_packages(),
                 include_package_data=True,
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ],
                 entry_points={
                     'console_scripts': ['rhythmo=rhythmo.runtime.cli:cli'],
                 },
                 install_requires=install_requires)