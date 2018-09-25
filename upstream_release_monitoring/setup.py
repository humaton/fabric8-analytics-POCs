#!/usr/bin/python3
import os

from setuptools import setup, find_packages


def get_requirements():
    requirements_txt = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')
    with open(requirements_txt) as fd:
        lines = fd.read().splitlines()

    return list(line for line in lines if not line.startswith('#'))


setup(
    name='fabric8-analytics-release-monitor',
    version='0.1',
    packages=find_packages(),
    install_requires=get_requirements(),
    py_modules='cli',
    scripts=['cli.py'],
    entry_points='''
        [console_scripts]
        cli=cli:cli
    ''',
    include_package_data=True,
    author='Tomas Hrcka',
    author_email='thrcka@redhat.com',
    description='fabric8-analytics pypi npm new releases monitor',
    license='ASL 2.0',
    keywords='fabric8 analytics firehose libraries.io',
    url='https://github.com/fabric8-analytics/fabric8-analytics-release-monitor',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Intended Audience :: Developers",
    ]
)
