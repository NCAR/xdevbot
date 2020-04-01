from os.path import exists

from setuptools import find_packages, setup

NAME = find_packages(exclude=['*.tests'])[0]

with open('requirements.txt') as f:
    install_requires = f.read().strip().split('\n')

if exists('README.rst'):
    with open('README.rst') as f:
        long_description = f.read()
else:
    long_description = ''

setup(
    name=NAME,
    packages=[NAME],
    install_requires=install_requires,
    author='Kevin Paul',
    author_email='kpaul@ucar.edu',
    description='The NCAR Xdev Team Bot',
    long_description=long_description,
    keywords='aiohttp mongodb motor ',
    url='https://github.com/ncar-xdev/xdevbot',
    project_urls={
        'Source Code': 'https://github.com/ncar-xdev/xdevbot',
        'Documentation': 'https://ncar-xdev.github.io/xdevbot',
        'Bug Tracker': 'https://github.com/ncar-xdev/xdevbot/issues',
    },
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
    ],
    use_scm_version={'version_scheme': 'post-release', 'local_scheme': 'dirty-tag'},
    setup_requires=['setuptools_scm', 'setuptools>=30.3.0'],
)
