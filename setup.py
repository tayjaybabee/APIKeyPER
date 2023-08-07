
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='apikeyper',
    version='0.1.0',
    description='',
    author='Taylor B. <tayjaybabee@gmail.com>',
    url='',
    classifiers=[],
    packages=['apikeyper', 'apikeyper.config', 'apikeyper.crypt', 'apikeyper.database', 'apikeyper.log_engine', 'apikeyper.ui', 'apikeyper.utils'],
    install_requires=requirements,
)
