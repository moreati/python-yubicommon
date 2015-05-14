# Copyright (c) 2013 Yubico AB
# All rights reserved.
#
#   Redistribution and use in source and binary forms, with or
#   without modification, are permitted provided that the following
#   conditions are met:
#
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from setuptools import Command
from distutils.errors import DistutilsSetupError
from setuptools.command.sdist import sdist
from PySide import QtGui
from . import utils, classes
import os
import sys


__dependencies__ = ['PySide']
__all__ = ['qt_sdist', 'qt_resources'] + classes.__all__ + utils.__all__


# Font fixes for OSX
if sys.platform == 'darwin':
    from platform import mac_ver
    mac_version = tuple(mac_ver()[0].split('.'))
    if (10, 9) <= mac_version < (10, 10):  # Mavericks
        QtGui.QFont.insertSubstitution('.Lucida Grande UI', 'Lucida Grande')
    if (10, 10) <= mac_version:  # Yosemite
        QtGui.QFont.insertSubstitution('.Helvetica Neue DeskInterface',
                                        'Helvetica Neue')


class qt_sdist(sdist):
    def run(self):
        self.run_command('qt_resources')

        sdist.run(self)


class _qt_resources(Command):
    description = "convert file resources into code"
    user_options = []
    boolean_options = []
    _source = 'qt_resources'
    _target = ''

    def initialize_options(self):
        pass

    def finalize_options(self):
        self.cwd = os.getcwd()
        self.source = os.path.join(self.cwd, self._source)
        self.target = os.path.join(self.cwd, self._target)

    def _create_qrc(self):
        qrc = os.path.join(self.source, 'qt_resources.qrc')
        with open(qrc, 'w') as f:
            f.write('<RCC>\n<qresource>\n')
            for fname in os.listdir(self.source):
                f.write('<file>%s</file>\n' % fname)
            f.write('</qresource>\n</RCC>\n')
        return qrc

    def run(self):
        if os.getcwd() != self.cwd:
            raise DistutilsSetupError("Must be in package root!")

        qrc = self._create_qrc()
        self.execute(os.system,
                     ('pyside-rcc "%s" -o "%s"' % (qrc, self.target),))
        os.unlink(qrc)

        self.announce("QT resources compiled into %s" % self.target)


def qt_resources(target, sourcedir='qt_resources'):
    target = target.replace('.', os.path.sep)
    if os.path.isdir(target):
        target = os.path.join(target, 'qt_resouces.py')
    else:
        target += '.py'

    return type('qt_resources', (_qt_resources, object), {
        '_source': sourcedir,
        '_target': target
    })
