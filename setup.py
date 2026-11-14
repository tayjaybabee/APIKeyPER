
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='apikeyper',
    version='0.2.0',
    description='APIKeyPER - API Key Personal Encrypted Reliquary',
    author='Taylor B. <tayjaybabee@gmail.com>',
    url='',
    classifiers=[],
    packages=[
        'apikeyper',
        'apikeyper.cli',
        'apikeyper.cli.handlers',
        'apikeyper.config',
        'apikeyper.crypt',
        'apikeyper.database',
        'apikeyper.log_engine',
        'apikeyper.ui',
        'apikeyper.utils',
    ],
    py_modules=['main'],
    install_requires=requirements,
    entry_points={'console_scripts': ['apikeyper=main:main']},
)
