# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 'author':'zouliwei'


from setuptools import setup, find_packages


with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='KaKa',
    version='0.2.0',
    description='A simple and easy-to-use web framework',
    long_description=long_description,
    keywords=('pip', 'web', 'framework', 'wsgi', 'restful'),
    license='BSD',

    url='https://github.com/zlw10100/kaka/',
    author='zouliwei',
    author_email='330494152@qq.com',

    packages=find_packages(),
    platforms='any',
    install_requires=[
        'Werkzeug>=0.14.1',
        'jinja2>=2.10',
    ],
    classifiers=[
            "Programming Language :: Python :: 3",
            'License :: OSI Approved :: BSD License',
            "Operating System :: OS Independent",
        ],
)
