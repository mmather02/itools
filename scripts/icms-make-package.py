#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2006 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2006-2007 Juan David Ibáñez Palomar <jdavid@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from the future
from __future__ import with_statement

# Import from the Standard Library
from datetime import date
from optparse import OptionParser
from os import environ
from os.path import exists, basename, dirname, join
from string import Template

# Import from itools
import itools
from itools import vfs


def make(parser, options, target):
    if exists(target):
        parser.error("Directory '%s' already existing" % target)

    # Find out the name of the package
    package = basename(target)

    # Build the namespace
    namespace = {}
    namespace['YEAR'] = date.today().year
    namespace['PACKAGE_NAME'] = package
    if 'GIT_AUTHOR_NAME' in environ:
        namespace['AUTHOR_NAME'] = environ['GIT_AUTHOR_NAME']
    if 'GIT_AUTHOR_EMAIL' in environ:
        namespace['AUTHOR_EMAIL'] = environ['GIT_AUTHOR_EMAIL']

    # Create the target folder
    vfs.make_folder(target)
    folder = vfs.open(target)

    # Copy source files
    path_prefix = 'cms/skeleton/%s/' % options.type
    path_prefix_n = len(path_prefix)

    itools_path = dirname(itools.__file__)
    manifest = join(itools_path, 'MANIFEST')
    with open(manifest) as manifest:
        for path in manifest.readlines():
            if not path.startswith(path_prefix):
                continue
            path = path.strip()
            # Read and process the data
            source = join(itools_path, path)
            source = open(source).read()
            data = Template(source).safe_substitute(**namespace)
            # Create the target file
            with folder.make_file(path[path_prefix_n:]) as file:
                file.write(data)

    # Print a helpful message
    print '*'
    print '* Package "%s" created' % package
    print '*'
    print '* To install it type:'
    print '*'
    print '*   $ cd %s' % target
    print '*   $ %s' % __file__.replace('icms-make-package', 'isetup-build')
    print '*   ...'
    print '*   $ %s setup.py install' % __file__.replace('icms-make-package', 'python')
    print '*'



if __name__ == '__main__':
    # The command line parser
    usage = '%prog TARGET'
    version = 'itools %s' % itools.__version__
    description = 'Creates a new Python package for itools.cms of name TARGET.'
    parser = OptionParser(usage, version=version, description=description)
    parser.add_option('-t', '--type', type="string", default="bare",
                      help='Choose the type of package to make.')

    # Get the name of the package to build
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error('incorrect number of arguments')

    target = args[0]

    # Action!
    make(parser, options, target)