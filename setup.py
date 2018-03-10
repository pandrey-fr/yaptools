# coding: utf-8

"""Setup for the installation of the 'yaptools' package.

Installation in a virtual environment is strongly advised.
"""

import setuptools

import yaptools


setuptools.setup(
    name='yaptools',
    version=yaptools.__version__,
    packages=setuptools.find_packages(),
    include_package_data=True,
    author='Paul Andrey',
    description='Yet Another Python Toolbox (YAPTools)',
    license='MIT',
    long_description=open('README.md').read(),
    url='https://github.com/pandrey-fr/yaptools/',
    install_requires=[
        'pandas >= 0.20.1',
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent"
    ]
)
