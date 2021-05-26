#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from os import path
from setuptools import setup

HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

with open(path.join(HERE, 'requirements.txt'), encoding='utf-8') as f:
    REQUIREMENTS = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.
setup(
    name='scl_loader',  # Required
    version='1.8.1',  # Required
    description='Outil de manipulation de SCD',  # Required
    long_description=LONG_DESCRIPTION,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    package_dir={'': 'src'},  # Optional
    packages=["scl_loader"],  # Required
    python_requires='>=3.6, <4',
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],

    # If there are data files included in your packages that need to be
    # installed, specify them here.
    #
    # If using Python 2.6 or earlier, then these have to be included in
    # MANIFEST.in as well.
    # package_data={  # Optional
    #    'resources': [],
    # },
    include_package_data=True,
    install_requires=REQUIREMENTS,

    entry_points={  # Optional
        'console_scripts': [],
    },
)
