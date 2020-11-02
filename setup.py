#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
# To use a consistent encoding
from os import path
import codecs

here = path.abspath(path.dirname(__file__))
long_description = "Create custom maps for GARMIN GPS from mapant "


def read(rel_path):
    with codecs.open(path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name='mapant',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=get_version("mapant/__init__.py"),

    description='Create custom maps for GARMIN GPS from mapant',
    long_description='Create custom maps for GARMIN GPS from mapant',

    # The project's main homepage.
    url='https://github.com/trygveasp/mapant',

    # Author details
    author='Trygve Aspelien',
    author_email='trygve@aspelien.no',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    # What does your project relate to?
    keywords='custom maps, mapant, garmin, gps, utm',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=["mapant"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=["pyproj"],

    scripts=[
        'bin/mapant2kml',
    ],
)
