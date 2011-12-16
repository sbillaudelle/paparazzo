#!/usr/bin/env python

import os
from distutils.core import setup
from distutils.command.install_scripts import install_scripts

class post_install(install_scripts):

    def run(self):
        install_scripts.run(self)

        from shutil import move
        for i in self.get_outputs():
            n = i.replace('.py', '')
            move(i, n)
            print("moving '{0}' to '{1}'".format(i, n))

setup(
    name = 'Paparazzo',
    version = '0.0.8',
    author = 'Sebastian Billaudelle',
    url = 'http://github.com/sbillaudelle/paparazzo',
    package_dir = {'paparazzo': 'src/paparazzo'},
    packages = ['paparazzo'],
    data_files = [('share/icons', ['paparazzo.png']), ('share/applications', ['Paparazzo.desktop'])],
    cmdclass={'install_scripts': post_install},
    scripts = ['src/paparazzo.py']
)
